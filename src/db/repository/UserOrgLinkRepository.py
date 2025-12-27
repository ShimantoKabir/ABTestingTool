from abc import ABC, abstractmethod
from src.db.links.UserOrgLink import UserOrgLink

class UserOrgLinkRepository(ABC):
  @abstractmethod
  def edit(self, userOrgLink: UserOrgLink) -> UserOrgLink|None:
    pass

  @abstractmethod
  def get(self, userId: int, orgId: int) -> UserOrgLink:
    pass

  @abstractmethod
  def getSuperAdminsByOrgId(self, orgId: int) -> list[UserOrgLink]:
    pass

  @abstractmethod
  def add(self, link: UserOrgLink) -> UserOrgLink:
    pass

  @abstractmethod
  def getActiveOrgs(self, userId: int, orgId: int) -> UserOrgLink:
    pass

