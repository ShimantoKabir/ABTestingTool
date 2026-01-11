from fastapi import APIRouter
from di import ResultServiceDep
from src.result.dtos.ResultResponseDto import ResultResponseDto

routes = APIRouter()

@routes.get(
  "/experiments/{experimentId}/results",
  response_model=list[ResultResponseDto],
  tags=["result"],
  name="act:get-experiment-results"
)
async def getExperimentResults(
    experimentId: int,
    service: ResultServiceDep
  ) -> list[ResultResponseDto]:
  """
  Get all metric results (QA and LIVE triggers) for a specific experiment,
  broken down by Variation and Metric.
  """
  return service.getResultsByExperiment(experimentId)