from src.user.repository.UserRepository import UserRepository
from src.user.model.User import User
from db import DBSessionDep
from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func
from src.db.links.UserOrgLink import UserOrgLink
from src.role.model.Role import Role
from src.menutemplate.model.MenuTemplate import MenuTemplate

class UserRepositoryImp(UserRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def getUserById(self, id: int) -> User:
    user = self.db.get(User,id)
    if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

  def add(self, user: User) -> User:
    existUser = self.db.exec(select(User).filter_by(email=user.email)).first()

    if existUser:
      raise HTTPException(status_code=status.HTTP_302_FOUND, detail="User already exist by this name!")
    
    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)

    return user
  
  def getUserByEmail(self, email: str) -> User:
    return self.db.exec(select(User).filter_by(email=email)).first()
  
  def updateUser(self, user: User):

    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)

    return user
  
  def getAllUser(self, rows: int, page: int, orgId: int)->list[User]:
    offset: int = (page - 1) * rows
    return self.db.exec(
      select(User, UserOrgLink, Role, MenuTemplate)
      .join(UserOrgLink, UserOrgLink.userId == User.id)
      .join(Role, UserOrgLink.roleId == Role.id, isouter=True)
      .join(MenuTemplate, UserOrgLink.menuTemplateId == MenuTemplate.id, isouter=True)
      .where(UserOrgLink.orgId == orgId)
      .offset(offset).limit(rows)
    ).all()
  
  def countAllUser(self, orgId: int) -> int:
    return self.db.exec(
      select(func.count(User.id))
      .select_from(UserOrgLink)
      .join(User, UserOrgLink.userId==User.id)
      .where(UserOrgLink.orgId == orgId)
    ).one()
    
    

  