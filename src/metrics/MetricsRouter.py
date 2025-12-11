from fastapi import APIRouter
from di import MetricsServiceDep
from src.metrics.dtos.MetricsCreateRequestDto import MetricsCreateRequestDto
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto
from src.metrics.dtos.MetricsTrackResponseDto import MetricsTrackResponseDto

routes = APIRouter()

@routes.post(
  "/experiments/{experimentId}/metrics", 
  response_model=MetricsResponseDto, 
  tags=["metrics"],
  name="act:create-metric"
)
async def createMetric(
    experimentId: int,
    reqDto: MetricsCreateRequestDto,
    service: MetricsServiceDep
  ) -> MetricsResponseDto:
  return service.createMetric(experimentId, reqDto)

@routes.get(
  "/experiments/{experimentId}/metrics", 
  response_model=list[MetricsResponseDto], 
  tags=["metrics"],
  name="act:get-metrics"
)
async def getMetrics(
    experimentId: int,
    service: MetricsServiceDep
  ) -> list[MetricsResponseDto]:
  return service.getMetrics(experimentId)

@routes.delete(
  "/metrics/{id}", 
  response_model=MetricsResponseDto, 
  tags=["metrics"],
  name="act:delete-metric"
) 
async def deleteMetric(
    id: int,
    service: MetricsServiceDep
  ) -> MetricsResponseDto:
  return service.deleteMetric(id)

@routes.post(
  "/metrics/{id}/track", 
  tags=["metrics"],
  name="act:track-metric",
  response_model=MetricsTrackResponseDto
)
async def trackMetric(
    id: int,
    service: MetricsServiceDep
  ):
  return service.trackMetric(id)