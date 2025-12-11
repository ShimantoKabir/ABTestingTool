from src.condition.repository.ConditionRepository import ConditionRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.condition.dtos.ConditionCreateRequestDto import ConditionCreateRequestDto
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto
from src.condition.model.Condition import Condition
from fastapi import HTTPException, status

class ConditionService:
  def __init__(
    self, 
    repo: ConditionRepository,
    experimentRepo: ExperimentRepository
  ):
    self.repo = repo
    self.experimentRepo = experimentRepo

  def createCondition(
      self, 
      experimentId: int, 
      reqDto: ConditionCreateRequestDto
    ) -> ConditionResponseDto:
    # 1. Validate Experiment Exists (Raises 404 if not found)
    self.experimentRepo.getById(experimentId)

    # 2. Create Condition
    newCondition = Condition(
      urls=reqDto.urls,
      operator=reqDto.operator,
      experimentId=experimentId
    )
    
    savedCondition = self.repo.add(newCondition)

    return self._mapToResponse(savedCondition)

  def getConditions(self, experimentId: int) -> list[ConditionResponseDto]:
    self.experimentRepo.getById(experimentId)
    conditions = self.repo.getByExperimentId(experimentId)
    return [self._mapToResponse(c) for c in conditions]

  def deleteCondition(self, id: int)-> ConditionResponseDto:
    condition = self.repo.getById(id)
    self.repo.delete(condition)
    return self._mapToResponse(condition)

  def _mapToResponse(self, c: Condition) -> ConditionResponseDto:
    # Ensure urls is a list of strings
    url_list = [str(u) for u in c.urls] if c.urls else []
    return ConditionResponseDto(
      id=c.id,
      experimentId=c.experimentId, # type: ignore
      urls=url_list,
      operator=c.operator
    )