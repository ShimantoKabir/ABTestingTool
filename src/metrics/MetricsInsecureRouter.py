from fastapi import APIRouter
from di import MetricsServiceDep
from src.metrics.dtos.MetricsTrackRequestDto import MetricsTrackRequestDto
from src.metrics.dtos.MetricsTrackResponseDto import MetricsTrackResponseDto
from src.metrics.model.TriggerMode import TriggerMode

routes = APIRouter()

@routes.post(
  "/metrics/track", 
  tags=["metrics"],
  name="act:track-metric",
  response_model=MetricsTrackResponseDto
)
async def trackMetric(
    reqDto: MetricsTrackRequestDto,
    service: MetricsServiceDep
  ):
  """
  Public endpoint to track metrics.
  Does not require Authentication headers.
  """
  return service.trackMetric(reqDto)