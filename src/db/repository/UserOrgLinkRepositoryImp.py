from src.db.repository.UserOrgLinkRepository import UserOrgLinkRepository
from src.db.links.UserOrgLink import UserOrgLink
from db import DBSessionDep
from sqlmodel import select

class UserOrgLinkRepositoryImp(UserOrgLinkRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def get(self, userId: int, orgId: int) -> UserOrgLink|None:
    return self.db.exec(select(UserOrgLink).filter_by(userId=userId,orgId=orgId)).first()

  def edit(self, userOrgLink: UserOrgLink) -> UserOrgLink:    

    self.db.add(userOrgLink)
    self.db.commit()
    self.db.refresh(userOrgLink)

    return userOrgLink
  
  def getSuperAdminsByOrgId(self, orgId: int) -> list[UserOrgLink]:
    return self.db.exec(
      select(UserOrgLink)
      .where(UserOrgLink.orgId == orgId)
      .where(UserOrgLink.super == True)
    ).all()
  
  def add(self, link: UserOrgLink) -> UserOrgLink:
    self.db.add(link)
    self.db.commit()
    self.db.refresh(link)
    return link
  
  def getActiveOrgs(self, userId: int, orgId: int) -> list[UserOrgLink]:
    return self.db.exec(
      select(UserOrgLink)
      .where(UserOrgLink.orgId == orgId)
      .where(UserOrgLink.disabled == False)
      .where(UserOrgLink.userId == userId)
    ).all()



  