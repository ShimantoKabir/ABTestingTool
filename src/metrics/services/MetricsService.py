from fastapi import HTTPException
from src.metrics.dtos.MetricsTrackRequestDto import MetricsTrackRequestDto
from src.metrics.repository.MetricsRepository import MetricsRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.metrics.dtos.MetricsCreateRequestDto import MetricsCreateRequestDto
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto
from src.metrics.model.Metrics import Metrics
from src.metrics.dtos.MetricsTrackResponseDto import MetricsTrackResponseDto
from src.metrics.model.TriggerMode import TriggerMode
from src.experiment.model.ExperimentStatus import ExperimentStatus

class MetricsService:
  def __init__(
    self, 
    repo: MetricsRepository,
    experimentRepo: ExperimentRepository
  ):
    self.repo = repo
    self.experimentRepo = experimentRepo

  def createMetric(
      self, 
      experimentId: int, 
      reqDto: MetricsCreateRequestDto
    ) -> MetricsResponseDto:
    # 1. Validate Experiment Exists
    self.experimentRepo.getById(experimentId)

    # 2. Create Metric
    newMetric = Metrics(
      title=reqDto.title,
      custom=reqDto.custom,
      selector=reqDto.selector,
      description=reqDto.description,
      experimentId=experimentId,
      triggered=0 # Default count
    )
    
    savedMetric = self.repo.add(newMetric)

    return self._mapToResponse(savedMetric)

  def getMetrics(self, experimentId: int) -> list[MetricsResponseDto]:
    self.experimentRepo.getById(experimentId)
    metrics = self.repo.getByExperimentId(experimentId)
    return [self._mapToResponse(m) for m in metrics]

  def deleteMetric(self, id: int) -> MetricsResponseDto:
    metric = self.repo.getById(id)
    self.repo.delete(metric)
    return self._mapToResponse(metric)

  def trackMetric(self, reqDto: MetricsTrackRequestDto):
    # Resolve the Metric Object
    if reqDto.custom:
      if not reqDto.eventName:
        raise HTTPException(status_code=400, detail="Event Name is required for custom metrics!")
        
      # Find the metric ID based on the event name (selector)
      metric = self.repo.getByExperimentAndEventName(reqDto.experimentId, reqDto.eventName)

    else:
      if not reqDto.metricsId:
        raise HTTPException(status_code=400, detail="Metric ID is required for standard metrics!")
        
      metric = self.repo.getById(reqDto.metricsId)

    # Determine Mode (QA vs Live)
    # We fetch experiment to check status
    experiment = self.experimentRepo.getById(metric.experimentId)
    
    mode = TriggerMode.LIVE if experiment.status == ExperimentStatus.ACTIVE else TriggerMode.QA

    # Increment Counter
    self.repo.incrementTrigger(metric.id, mode)

    return MetricsTrackResponseDto(
      message=f"Metric tracked successfully in {mode} mode"
    )

  def _mapToResponse(self, m: Metrics) -> MetricsResponseDto:
    return MetricsResponseDto(
      id=m.id,
      experimentId=m.experimentId, # type: ignore
      title=m.title, # type: ignore
      custom=m.custom,
      selector=m.selector,
      description=m.description,
      triggeredOnQA=m.triggeredOnQA if m.triggeredOnQA else 0, # <--- Added
      triggeredOnLIVE=m.triggeredOnLIVE if m.triggeredOnLIVE else 0 # <--- Added
    )