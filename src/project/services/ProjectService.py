from src.project.repository.ProjectRepository import ProjectRepository
from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository
from src.project.dtos.ProjectCreateRequestDto import ProjectCreateRequestDto
from src.project.dtos.ProjectCreateResponseDto import ProjectCreateResponseDto
from src.project.dtos.ProjectResponseDto import ProjectResponseDto
from src.project.model.Project import Project
from src.db.links.UserProjectLink import UserProjectLink
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto
from src.db.links.PermissionType import PermissionType
from fastapi import status, HTTPException
from src.project.dtos.ProjectAssignUserRequestDto import ProjectAssignUserRequestDto
from src.project.dtos.ProjectAssignUserResponseDto import ProjectAssignUserResponseDto
from src.db.links.UserProjectLink import UserProjectLink
from src.project.dtos.ProjectRemoveUserResponseDto import ProjectRemoveUserResponseDto

class ProjectService:
  def __init__(
      self, 
      projectRepo: ProjectRepository, 
      linkRepo: UserProjectLinkRepository
    ):
    self.repo = projectRepo
    self.linkRepo = linkRepo

  def createProject(self, reqDto: ProjectCreateRequestDto, userId: int) -> ProjectCreateResponseDto:
    # 1. Create the project
    newProject = self.repo.add(Project(
      name=reqDto.name,
      description=reqDto.description,
      orgId=reqDto.orgId
    ))

    # 2. Link the creating user as a Super Admin for this project
    self.linkRepo.add(UserProjectLink(
      userId=userId,
      projectId=newProject.id,
      super=True,
      disabled=False,
      permissionType=PermissionType.OWNER
    ))

    return ProjectCreateResponseDto(
      id=newProject.id,
      name=newProject.name,
      orgId=newProject.orgId
    )

  def getProjects(self, reqDto: PaginationRequestDto) -> PaginationResponseDto[ProjectResponseDto]:
    total: int | None = reqDto.total
    
    if reqDto.total is None or reqDto.total == 0:
      total = self.repo.countAllProjects(orgId=reqDto.orgId)

    projects: list[Project] = self.repo.getAllProjects(
      rows=reqDto.rows, 
      page=reqDto.page, 
      orgId=reqDto.orgId
    )

    items: list[ProjectResponseDto] = []
    for p in projects:
      items.append(ProjectResponseDto(
        id=p.id,
        name=p.name,
        description=p.description,
        orgId=p.orgId,
        orgName=p.org.name if p.org else ""
      ))

    return PaginationResponseDto[ProjectResponseDto](items=items, total=total)
  
  def assignUser(self, projectId: int, reqDto: ProjectAssignUserRequestDto) -> ProjectAssignUserResponseDto:
    # 1. Check if Project exists
    project = self.repo.getProjectById(projectId) # raises 404 if not found

    # 2. Check if User is already assigned to this project
    existingLink = self.linkRepo.get(userId=reqDto.userId, projectId=projectId)
    if existingLink:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, 
        detail="User is already assigned to this project!"
      )

    # 3. Create the assignment
    newLink = UserProjectLink(
      userId=reqDto.userId,
      projectId=projectId,
      permissionType=PermissionType.EDITOR,
      disabled=False,
      super=False # Default to false for regular assignments
    )
    
    self.linkRepo.add(newLink)

    return ProjectAssignUserResponseDto(
      projectId=projectId,
      userId=reqDto.userId,
      message="User assigned to project successfully"
    )
  
  def getProjectsByUserId(self, userId: int) -> list[ProjectResponseDto]:
    results = self.repo.getAllByUserId(userId)
    
    responseList = []
    for project, link in results:
      responseList.append(ProjectResponseDto(
        id=project.id,
        name=project.name,
        description=project.description,
        orgId=project.orgId,
        orgName=project.org.name if project.org else ""
      ))
      
    return responseList
  
  def removeUserFromProject(self, projectId: int, userId: int) -> ProjectRemoveUserResponseDto:
    # 1. Find the assignment
    link = self.linkRepo.get(userId=userId, projectId=projectId)
    
    # 2. If no link exists, we can't delete it
    if not link:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="User is not assigned to this project!"
      )

    # 3. Hard Delete (Remove row from DB)
    self.linkRepo.delete(link)

    return ProjectRemoveUserResponseDto(
      message="User removed from project successfully"
    )