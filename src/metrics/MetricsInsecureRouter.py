from fastapi import APIRouter
from di import MetricsServiceDep
from src.metrics.dtos.MetricsTrackResponseDto import MetricsTrackResponseDto
from src.metrics.model.TriggerMode import TriggerMode

routes = APIRouter()

@routes.post(
  "/metrics/{id}/track", 
  tags=["metrics"],
  name="act:track-metric",
  response_model=MetricsTrackResponseDto
)
async def trackMetric(
    id: int,
    service: MetricsServiceDep,
    mode: TriggerMode = TriggerMode.LIVE
  ):
  """
  Public endpoint to track metrics.
  Does not require Authentication headers.
  """
  return service.trackMetric(id, mode)