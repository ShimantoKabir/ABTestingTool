from fastapi import APIRouter
from di import DecisionServiceDep
from src.decision.dtos.DecisionRequestDto import DecisionRequestDto
from src.decision.dtos.DecisionResponseDto import DecisionResponseDto
from src.decision.dtos.PreviewRequestDto import PreviewRequestDto
from src.decision.dtos.PreviewResponseDto import PreviewResponseDto

routes = APIRouter()

@routes.post(
  "/decision/preview",
  tags=["decision"],
  name="act:preview-decision",
  response_model=PreviewResponseDto
)
async def previewDecision(
  reqDto: PreviewRequestDto,
  decisionService: DecisionServiceDep
) -> PreviewResponseDto:
  """
  Public endpoint called by the SDK (in Preview Mode).
  Force a specific experiment variation, bypassing targeting/bucketing.
  """
  return decisionService.getPreview(reqDto)