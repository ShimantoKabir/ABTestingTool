from src.db.links.UserProjectLink import UserProjectLink
from src.project.repository.ProjectRepository import ProjectRepository
from src.project.model.Project import Project
from db import DBSessionDep
from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

class ProjectRepositoryImp(ProjectRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def getProjectById(self, id: int) -> Project:
    project = self.db.get(Project, id)
    if not project:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

  def add(self, project: Project) -> Project:
    # Optional: Check if project name exists within the SAME org
    existProject = self.db.exec(
      select(Project)
      .where(Project.name == project.name)
      .where(Project.orgId == project.orgId)
    ).first()

    if existProject:
      raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Project already exists in this organization!")
    
    self.db.add(project)
    self.db.commit()
    self.db.refresh(project)
    return project
  
  def getAllProjects(self, rows: int, page: int, orgId: int) -> list[Project]:
    offset: int = (page - 1) * rows
    return self.db.exec(
      select(Project)
      .where(Project.orgId == orgId)
      .offset(offset).limit(rows)
    ).all()
  
  def countAllProjects(self, orgId: int) -> int:
    return self.db.exec(
      select(func.count(Project.id))
      .where(Project.orgId == orgId)
    ).one()
  
  def getAllByUserId(self, userId: int) -> list[tuple[Project, UserProjectLink]]:
    return self.db.exec(
      select(Project, UserProjectLink)
      .join(UserProjectLink, Project.id == UserProjectLink.projectId)
      .where(UserProjectLink.userId == userId)
      .options(selectinload(Project.org))
    ).all()