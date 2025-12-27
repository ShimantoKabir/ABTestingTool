from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository
from src.db.links.UserProjectLink import UserProjectLink
from db import DBSessionDep
from sqlmodel import select, col
from src.project.model.Project import Project

class UserProjectLinkRepositoryImp(UserProjectLinkRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def add(self, link: UserProjectLink) -> UserProjectLink:
    self.db.add(link)
    self.db.commit()
    self.db.refresh(link)
    return link

  def get(self, userId: int, projectId: int) -> UserProjectLink | None:
    return self.db.exec(
      select(UserProjectLink)
      .where(UserProjectLink.userId == userId)
      .where(UserProjectLink.projectId == projectId)
    ).first()
  
  def delete(self, link: UserProjectLink):
    self.db.delete(link)
    self.db.commit()

  def getActiveProjectsByOrgIds(self, userId: int, activeOrgIds: list[int]) -> list[Project]:
    # If there are no active orgs, the user cannot have any valid projects
    if not activeOrgIds:
      return []

    return self.db.exec(
      select(Project)
      .join(UserProjectLink, Project.id == UserProjectLink.projectId)
      .where(UserProjectLink.userId == userId)       # Link belongs to user
      .where(UserProjectLink.disabled == False)      # Link is enabled
      .where(col(Project.orgId).in_(activeOrgIds))   # Project belongs to an active Org
    ).all()