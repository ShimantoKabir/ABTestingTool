import mmh3
import random
from fastapi import BackgroundTasks
from src.bucket.repository.BucketRepository import BucketRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.decision.dtos.DecisionRequestDto import DecisionRequestDto
from src.decision.dtos.DecisionResponseDto import DecisionResponseDto, ExperimentDecisionDto, VariationDecisionDto
from src.bucket.model.Bucket import Bucket
from src.experiment.model.Experiment import Experiment
from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.condition.model.Operator import Operator
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto
from src.utils.CacheService import CacheService
from src.variation.model.Variation import Variation
from src.condition.model.Condition import Condition
from src.metrics.model.Metrics import Metrics
from config import Config

class DecisionService:
  # The bucketing scale (1 to 10,000 for 0.01% granularity)
  MAX_TRAFFIC_VAL = Config.getValByKey("MAX_TRAFFIC_VAL")

  def __init__(
    self, 
    bucketRepo: BucketRepository,
    experimentRepo: ExperimentRepository,
    cacheService: CacheService
  ):
    self.bucketRepo = bucketRepo
    self.experimentRepo = experimentRepo
    self.cache = cacheService

  def makeDecision(
      self, 
      reqDto: DecisionRequestDto, 
      projectId: int, 
      bgTasks: BackgroundTasks
    ) -> DecisionResponseDto:
    
    # 1. Identity Management
    endUserId = reqDto.endUserId if reqDto.endUserId else random.randint(100000, 999999)

    # 2. Fetch Active Experiments (Redis Cache -> DB)
    activeExperiments = self.getActiveExperiments(projectId)

    decisions: list[ExperimentDecisionDto] = []

    for exp in activeExperiments:
      # 3. Targeting Check
      if not self.checkTargeting(exp, reqDto.url):
        continue

      # 4. Consistency Check (Sticky Bucketing)
      existingBucket = self.bucketRepo.get(experimentId=exp.id, endUserId=endUserId)

      if existingBucket:
        # User is already locked in. Return the saved variation.
        assignedVariation = next((v for v in exp.variations if v.id == existingBucket.variationId), None)
        if assignedVariation:
          decisions.append(self.buildDecisionDto(exp, assignedVariation))
      
      else:
        # 5. The Bucketing Machine
        hashKey = f"{endUserId}:{exp.id}"
        hashInt = mmh3.hash(hashKey)
        
        # Scale hash to 1 - 10,000
        bucketVal = (abs(hashInt) % self.MAX_TRAFFIC_VAL) + 1
        
        # 6. Traffic Allocation
        chosenVariation = None
        cumulativeTraffic = 0

        for variation in exp.variations:
          rangeLimit = int(variation.traffic * 100)
          
          if bucketVal <= (cumulativeTraffic + rangeLimit):
            chosenVariation = variation
            break
          
          cumulativeTraffic += rangeLimit

        if chosenVariation:
          # 7. Async Persistence
          bgTasks.add_task(self.recordAssignment, exp.id, endUserId, chosenVariation.id)
          decisions.append(self.buildDecisionDto(exp, chosenVariation))

    return DecisionResponseDto(endUserId=endUserId, decisions=decisions)

  def recordAssignment(self, expId: int, userId: int, varId: int):
    # Runs in background. Checks for duplicates before inserting.
    existing = self.bucketRepo.get(expId, userId)
    if not existing:
      self.bucketRepo.add(Bucket(expId=expId, endUserId=userId, variationId=varId))

  def checkTargeting(self, exp: Experiment, url: str) -> bool:
    if not exp.conditions:
      return True

    matches = []
    for cond in exp.conditions:
      isMatch = False 
      
      if cond.operator in [Operator.IS, Operator.CONTAIN]:
        for condUrl in cond.urls:
          if cond.operator == Operator.CONTAIN and condUrl in url:
            isMatch = True
            break
          if cond.operator == Operator.IS and condUrl == url:
            isMatch = True
            break
             
      elif cond.operator in [Operator.IS_NOT, Operator.NOT_CONTAIN]:
        isMatch = True 
        for condUrl in cond.urls:
          if cond.operator == Operator.NOT_CONTAIN and condUrl in url:
            isMatch = False
            break 
          if cond.operator == Operator.IS_NOT and condUrl == url:
            isMatch = False
            break 
      
      matches.append(isMatch)

    if exp.conditionType == "ALL":
      return all(matches)
    else: # ANY
      return any(matches)

  def getActiveExperiments(self, projectId: int) -> list[Experiment]:
    cacheKey = f"project:{projectId}:active_experiments"
    
    # 1. Try Redis Cache
    cachedData = self.cache.get(cacheKey)
    if cachedData:
      return [self.deserializeExperiment(item) for item in cachedData]
    
    # 2. Cache Miss: Fetch from DB
    allExperiments = self.experimentRepo.getAll(rows=1000, page=1, projectId=projectId)
    activeExperiments = [e for e in allExperiments if e.status == ExperimentStatus.ACTIVE]
    
    # 3. Serialize and Save to Redis
    serializedData = [self.serializeExperiment(e) for e in activeExperiments]
    self.cache.set(cacheKey, serializedData, ttl=60)
    
    return activeExperiments

  # Helper: Convert DB Object to Dictionary for Redis
  def serializeExperiment(self, exp: Experiment) -> dict:
    return {
      "id": exp.id,
      "title": exp.title,
      "status": exp.status,
      "js": exp.js,
      "css": exp.css,
      "conditionType": exp.conditionType,
      "conditions": [c.model_dump() for c in exp.conditions],
      "metrics": [m.model_dump() for m in exp.metrics],
      "variations": [v.model_dump() for v in exp.variations]
    }

  # Helper: Convert Dictionary back to DB Object
  def deserializeExperiment(self, data: dict) -> Experiment:
    # Manually reconstruct objects to keep relationships valid
    exp = Experiment(**data)
    # Reconstruct relationships from nested lists
    exp.conditions = [Condition(**c) for c in data.get("conditions", [])]
    exp.metrics = [Metrics(**m) for m in data.get("metrics", [])]
    exp.variations = [Variation(**v) for v in data.get("variations", [])]
    return exp

  def buildDecisionDto(self, exp: Experiment, variation) -> ExperimentDecisionDto:
    condDtos = [
      ConditionResponseDto(
        id=c.id, 
        experimentId=c.experimentId, 
        urls=[str(u) for u in c.urls], 
        operator=c.operator
      ) for c in exp.conditions
    ]
    
    metDtos = [
      MetricsResponseDto(
        id=m.id, 
        experimentId=m.experimentId, 
        title=m.title, 
        custom=m.custom, 
        selector=m.selector, 
        description=m.description, 
        triggered=m.triggered
      ) for m in exp.metrics
    ]

    return ExperimentDecisionDto(
      experimentId=exp.id,
      experimentTitle=exp.title,
      experimentJs=exp.js,
      experimentCss=exp.css,
      variation=VariationDecisionDto(
        variationId=variation.id,
        variationTitle=variation.title,
        js=variation.js,
        css=variation.css
      ),
      conditions=condDtos,
      metrics=metDtos
    )