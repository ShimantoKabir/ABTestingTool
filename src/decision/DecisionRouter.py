from fastapi import APIRouter, BackgroundTasks
from di import DecisionServiceDep
from src.decision.dtos.DecisionRequestDto import DecisionRequestDto
from src.decision.dtos.DecisionResponseDto import DecisionResponseDto

routes = APIRouter()

@routes.post(
  "/decision", 
  tags=["decision"],
  name="act:make-decision",
  response_model=DecisionResponseDto
)
async def makeDecision(
  reqDto: DecisionRequestDto, 
  decisionService: DecisionServiceDep,
  bgTasks: BackgroundTasks # Change: Inject BackgroundTasks
) -> DecisionResponseDto:

  # Pass bgTasks to service
  decisionRes: DecisionResponseDto = decisionService.makeDecision(reqDto, bgTasks)
  return decisionRes