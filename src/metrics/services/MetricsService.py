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
from src.result.repository.ResultRepository import ResultRepository

class MetricsService:
  def __init__(
    self, 
    repo: MetricsRepository,
    experimentRepo: ExperimentRepository,
    resultRepo: ResultRepository
  ):
    self.repo = repo
    self.experimentRepo = experimentRepo
    self.resultRepo = resultRepo

  def createMetric(
      self, 
      experimentId: int, 
      reqDto: MetricsCreateRequestDto
    ) -> MetricsResponseDto:
    # Validate Experiment Exists
    self.experimentRepo.getById(experimentId)

    # Create Metric
    newMetric = Metrics(
      title=reqDto.title,
      custom=reqDto.custom,
      selector=reqDto.selector,
      description=reqDto.description,
      experimentId=experimentId
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
    if reqDto.custom:
      if not reqDto.eventName:
        raise HTTPException(status_code=400, detail="Event Name is required!")
      metric = self.repo.getByExperimentAndEventName(reqDto.experimentId, reqDto.eventName)
    else:
      if not reqDto.metricsId:
        raise HTTPException(status_code=400, detail="Metric ID is required!")
      metric = self.repo.getById(reqDto.metricsId)

    # Determine Mode
    experiment = self.experimentRepo.getById(reqDto.experimentId)
    
    # If it is a Preview request, ALWAYS track as QA.
    # Otherwise, check the experiment status (Active = Live, Draft/Paused = QA)
    if reqDto.isPreview:
      mode = TriggerMode.QA
    else:
      mode = TriggerMode.LIVE if experiment.status == ExperimentStatus.ACTIVE else TriggerMode.QA

    # Increment
    self.resultRepo.increment(
      metricId=metric.id, 
      variationId=reqDto.variationId, 
      experimentId=reqDto.experimentId,
      mode=mode
    )

    return MetricsTrackResponseDto(
      message=f"Metric tracked successfully in {mode} mode"
    )

  def _mapToResponse(self, m: Metrics) -> MetricsResponseDto:
    return MetricsResponseDto(
      id=m.id,
      experimentId=m.experimentId, 
      title=m.title, 
      custom=m.custom,
      selector=m.selector,
      description=m.description,
      isPrimary=m.isPrimary
    )
  
  def makeMetricPrimary(self, metricId: int) -> MetricsResponseDto:
    # Get the metric to ensure it exists and find its experimentId
    metric = self.repo.getById(metricId) # Raises 404 if not found
    
    # Perform the update
    self.repo.markAsPrimary(metric.id, metric.experimentId)
    
    # manually set it to return the response immediately
    metric.isPrimary = True

    return self._mapToResponse(metric)