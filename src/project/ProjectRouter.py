from fastapi import APIRouter, Request, status, HTTPException
from di import ProjectServiceDep, UserServiceDep
from src.project.dtos.ProjectCreateRequestDto import ProjectCreateRequestDto
from src.project.dtos.ProjectCreateResponseDto import ProjectCreateResponseDto
from src.project.dtos.ProjectResponseDto import ProjectResponseDto
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto
from src.project.dtos.ProjectAssignUserRequestDto import ProjectAssignUserRequestDto
from src.project.dtos.ProjectAssignUserResponseDto import ProjectAssignUserResponseDto
from src.project.dtos.ProjectRemoveUserResponseDto import ProjectRemoveUserResponseDto

routes = APIRouter()

@routes.post(
  "/projects/", 
  response_model=ProjectCreateResponseDto, 
  tags=["project"],
  name="act:create-project"
)
async def createProject(
    reqDto: ProjectCreateRequestDto,
    projectService: ProjectServiceDep,
    userService: UserServiceDep,
    request: Request
  ) -> ProjectCreateResponseDto:
  
  # Extract email from header (set by AuthMiddleware)
  email = request.headers.get("email")
  if not email:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User email not found")
      
  # We need the User ID to link them to the project
  user = userService.repo.getUserByEmail(email)
  if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  return projectService.createProject(reqDto, user.id)

@routes.post(
  "/projects/all",
  tags=["project"],
  name="act:get-projects",
  response_model=PaginationResponseDto[ProjectResponseDto]
)
async def getProjects(
  reqDto: PaginationRequestDto, 
  projectService: ProjectServiceDep
) -> PaginationResponseDto[ProjectResponseDto]:  
  return projectService.getProjects(reqDto)

@routes.post(
  "/projects/{projectId}/users",
  tags=["project"],
  name="act:assign-user-to-project",
  response_model=ProjectAssignUserResponseDto
)
async def assignUserToProject(
  projectId: int,
  reqDto: ProjectAssignUserRequestDto,
  projectService: ProjectServiceDep
) -> ProjectAssignUserResponseDto:
  """
  Assign an existing user to a project with a specific permission level.
  """
  return projectService.assignUser(projectId, reqDto)

@routes.get(
  "/projects/user/{userId}",
  tags=["project"],
  name="act:get-user-projects",
  response_model=list[ProjectResponseDto]
)
async def getProjectsByUser(
  userId: int,
  projectService: ProjectServiceDep
) -> list[ProjectResponseDto]:
  """
  Get all projects assigned to a specific user.
  """
  return projectService.getProjectsByUserId(userId)


@routes.delete(
  "/projects/{projectId}/users/{userId}",
  tags=["project"],
  name="act:remove-user-from-project",
  response_model=ProjectRemoveUserResponseDto
)
async def removeUserFromProject(
  projectId: int,
  userId: int,
  projectService: ProjectServiceDep
) -> ProjectRemoveUserResponseDto:
  """
  Remove (unassign) a user from a specific project.
  """
  return projectService.removeUserFromProject(projectId, userId)