from src.metrics.repository.MetricsRepository import MetricsRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.metrics.dtos.MetricsCreateRequestDto import MetricsCreateRequestDto
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto
from src.metrics.model.Metrics import Metrics
from src.metrics.dtos.MetricsTrackResponseDto import MetricsTrackResponseDto
from fastapi import HTTPException, status

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
  
  def trackMetric(self, id: int):
    self.repo.incrementTrigger(id)
    return MetricsTrackResponseDto(message="Metric tracked successfully")

  def _mapToResponse(self, m: Metrics) -> MetricsResponseDto:
    return MetricsResponseDto(
      id=m.id,
      experimentId=m.experimentId, # type: ignore
      title=m.title, # type: ignore
      custom=m.custom,
      selector=m.selector,
      description=m.description,
      triggered=m.triggered if m.triggered else 0
    )