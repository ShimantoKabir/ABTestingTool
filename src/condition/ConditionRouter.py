from fastapi import APIRouter
from di import ConditionServiceDep
from src.condition.dtos.ConditionCreateRequestDto import ConditionCreateRequestDto
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto

routes = APIRouter()

@routes.post(
  "/experiments/{experimentId}/conditions", 
  response_model=ConditionResponseDto, 
  tags=["condition"],
  name="act:create-condition"
)
async def createCondition(
    experimentId: int,
    reqDto: ConditionCreateRequestDto,
    service: ConditionServiceDep
  ) -> ConditionResponseDto:
  return service.createCondition(experimentId, reqDto)

@routes.get(
  "/experiments/{experimentId}/conditions", 
  response_model=list[ConditionResponseDto], 
  tags=["condition"],
  name="act:get-conditions"
)
async def getConditions(
    experimentId: int,
    service: ConditionServiceDep
  ) -> list[ConditionResponseDto]:
  return service.getConditions(experimentId)

@routes.delete(
  "/conditions/{id}", 
  response_model=ConditionResponseDto, 
  tags=["condition"],
  name="act:delete-condition"
)
async def deleteCondition(
    id: int,
    service: ConditionServiceDep
  ) -> ConditionResponseDto:
  return service.deleteCondition(id)