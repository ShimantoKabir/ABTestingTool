from src.condition.repository.ConditionRepository import ConditionRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.condition.dtos.ConditionCreateRequestDto import ConditionCreateRequestDto
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto
from src.condition.model.Condition import Condition
from src.utils.CacheService import CacheService
from fastapi import HTTPException, status

class ConditionService:
  def __init__(
    self, 
    repo: ConditionRepository,
    experimentRepo: ExperimentRepository,
    cacheService: CacheService
  ):
    self.repo = repo
    self.experimentRepo = experimentRepo
    self.cache = cacheService

  def createCondition(
      self, 
      experimentId: int, 
      reqDto: ConditionCreateRequestDto
    ) -> ConditionResponseDto:
    # Check if experiment exists
    experiment = self.experimentRepo.getById(experimentId)
    if not experiment:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")

    newCondition = Condition(
      experimentId=experimentId,
      operator=reqDto.operator,
      urls=reqDto.urls
    )
    
    savedCondition = self.repo.add(newCondition)
    
    # 3. INVALIDATE CACHE
    # The targeting rules have changed. We must clear the cache for this project.
    self.invalidateProjectCache(experiment.projectId)
    
    return self.mapToResponse(savedCondition)

  def deleteCondition(self, id: int) -> ConditionResponseDto:
    condition = self.repo.getById(id)
    if not condition:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found!")
        
    # We need the experiment to find the projectId
    experiment = self.experimentRepo.getById(condition.experimentId)
    
    self.repo.delete(condition)
    
    # 3. INVALIDATE CACHE
    if experiment:
      self.invalidateProjectCache(experiment.projectId)
        
    return self.mapToResponse(condition)

  # Helper to keep code clean
  def invalidateProjectCache(self, projectId: int):
    cacheKey = f"project:{projectId}:active_experiments"
    self.cache.delete(cacheKey)

  def mapToResponse(self, c: Condition) -> ConditionResponseDto:
    return ConditionResponseDto(
      id=c.id,
      experimentId=c.experimentId,
      urls=c.urls,
      operator=c.operator
    )
  
  def getConditions(self, experimentId: int) -> list[ConditionResponseDto]:
    self.experimentRepo.getById(experimentId)
    conditions = self.repo.getByExperimentId(experimentId)
    return [self.mapToResponse(c) for c in conditions]