from abc import ABC, abstractmethod
from src.db.links.UserProjectLink import UserProjectLink
from src.project.model.Project import Project

class ProjectRepository(ABC):
  @abstractmethod
  def getProjectById(self, id: int) -> Project:
    pass

  @abstractmethod
  def add(self, project: Project) -> Project:
    pass

  @abstractmethod
  def getAllProjects(self, rows: int, page: int, orgId: int) -> list[Project]:
    pass

  @abstractmethod
  def countAllProjects(self, orgId: int) -> int:
    pass

  @abstractmethod
  def getAllByUserId(self, userId: int) -> list[tuple[Project, UserProjectLink]]:
    pass