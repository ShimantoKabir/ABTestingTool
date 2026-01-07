from fastapi import APIRouter, Request, status, HTTPException, BackgroundTasks
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
  request: Request,
  bgTasks: BackgroundTasks # Change: Inject BackgroundTasks
) -> DecisionResponseDto:
  
  projectIdHeader = request.headers.get("project-id")
  if not projectIdHeader:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project ID header required")
  
  try:
    projectId = int(projectIdHeader)
  except ValueError:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Project ID format")

  # Pass bgTasks to service
  return decisionService.makeDecision(reqDto, projectId, bgTasks)