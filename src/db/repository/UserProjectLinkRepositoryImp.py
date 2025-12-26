from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository
from src.db.links.UserProjectLink import UserProjectLink
from db import DBSessionDep
from sqlmodel import select

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