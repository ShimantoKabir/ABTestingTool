from src.experiment.model.ConditionType import ConditionType
from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.experiment.model.TriggerType import TriggerType
from src.experiment.model.ExperimentType import ExperimentType
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.project.repository.ProjectRepository import ProjectRepository
from src.experiment.dtos.ExperimentCreateRequestDto import ExperimentCreateRequestDto
from src.experiment.dtos.ExperimentCreateResponseDto import ExperimentCreateResponseDto
from src.experiment.dtos.ExperimentResponseDto import ExperimentResponseDto
from src.experiment.dtos.ExperimentUpdateRequestDto import ExperimentUpdateRequestDto
from src.experiment.model.Experiment import Experiment
from src.variation.model.Variation import Variation
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto
from fastapi import HTTPException, status

class ExperimentService:
  def __init__(
    self, 
    repo: ExperimentRepository, 
    projectRepo: ProjectRepository
  ):
    self.repo = repo
    self.projectRepo = projectRepo

  def createExperiment(self, reqDto: ExperimentCreateRequestDto) -> ExperimentCreateResponseDto:
    self.projectRepo.getProjectById(reqDto.projectId)

    newExp = Experiment(
      title=reqDto.title,
      projectId=reqDto.projectId,
      type=ExperimentType.AB_TEST,
      url=reqDto.url,
      status=ExperimentStatus.DRAFT,
      triggerType=TriggerType.IMMEDIATELY,
      conditionType=ConditionType.ALL,
      description=reqDto.description,
      js="",
      css="",
      variations=[],
      conditions=[], 
      metrics=[]     
    )

    newExp.variations.append(Variation(
      title="Control", 
      traffic=100,
      js=None,
      css=None
    ))

    savedExp = self.repo.add(newExp)

    return ExperimentCreateResponseDto(
      id=savedExp.id,
      title=savedExp.title,
      status=savedExp.status
    )

  def getExperiments(self, reqDto: PaginationRequestDto) -> PaginationResponseDto[ExperimentResponseDto]:
    projectId = reqDto.orgId 
    
    total = reqDto.total
    if total is None or total == 0:
      total = self.repo.countAll(projectId=projectId)

    exps = self.repo.getAll(rows=reqDto.rows, page=reqDto.page, projectId=projectId)
    
    items = []
    for e in exps:
      items.append(self._mapToResponse(e))

    return PaginationResponseDto[ExperimentResponseDto](items=items, total=total)

  def getById(self, id: int) -> ExperimentResponseDto:
    e = self.repo.getById(id)
    return self._mapToResponse(e)

  # 1. Added update logic
  def updateExperiment(
      self, 
      id: int, 
      reqDto: ExperimentUpdateRequestDto
    ) -> ExperimentResponseDto:
    # Fetch existing experiment
    experiment = self.repo.getById(id)

    # Update fields if provided
    if reqDto.title is not None:
      experiment.title = reqDto.title
    if reqDto.js is not None:
      experiment.js = reqDto.js
    if reqDto.css is not None:
      experiment.css = reqDto.css
    if reqDto.type is not None:
      experiment.type = reqDto.type
    if reqDto.status is not None:
      experiment.status = reqDto.status
    if reqDto.url is not None:
      experiment.url = reqDto.url
    if reqDto.description is not None:
      experiment.description = reqDto.description
    if reqDto.triggerType is not None:
      experiment.triggerType = reqDto.triggerType
    if reqDto.conditionType is not None:
      experiment.conditionType = reqDto.conditionType

    updatedExp = self.repo.edit(experiment)
    return self._mapToResponse(updatedExp)

  # Helper to avoid code duplication in mapping
  def _mapToResponse(self, e: Experiment) -> ExperimentResponseDto:
    return ExperimentResponseDto(
      id=e.id,
      title=e.title,
      projectId=e.projectId, # type: ignore
      type=e.type,
      status=e.status,
      url=e.url,
      description=e.description,
      triggerType=e.triggerType,
      conditionType=e.conditionType,
      js=e.js,
      css=e.css,
      createdAt=e.createdAt,
      updatedAt=e.updatedAt
    )