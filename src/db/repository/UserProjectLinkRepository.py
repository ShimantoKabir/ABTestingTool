from abc import ABC, abstractmethod
from src.db.links.UserProjectLink import UserProjectLink
from src.project.model.Project import Project

class UserProjectLinkRepository(ABC):
  @abstractmethod
  def add(self, link: UserProjectLink) -> UserProjectLink:
    pass

  @abstractmethod
  def get(self, userId: int, projectId: int) -> UserProjectLink | None:
    pass

  @abstractmethod
  def delete(self, link: UserProjectLink):
    pass

  @abstractmethod
  def getActiveProjectsByOrgIds(self, userId: int, activeOrgIds: list[int]) -> list[Project]:
    pass