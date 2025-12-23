from db import DBSessionDep
from src.org.repository.OrgRepository import OrgRepository
from src.org.model.Organization import Organization
from fastapi import status, HTTPException
from sqlmodel import select
from sqlmodel import col


class OrgRepositoryImp(OrgRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def getByDomain(self, domain: str) -> Organization:
    return self.db.exec(select(Organization).filter_by(domain=domain)).first()

  def add(self, org: Organization) -> Organization:
    existOrg = self.getByDomain(org.domain)

    if existOrg:
      raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Organization already exist by this domain!")
    
    self.db.add(org)
    self.db.commit()
    self.db.refresh(org)

    return org
  
  def search(self, query: str, limit: int = 10) -> list[Organization]:
    return self.db.exec(
      select(Organization)
      .where(col(Organization.name).ilike(f"%{query}%"))
      .limit(limit)
    ).all()
  
  def getById(self, id: int) -> Organization:
    org = self.db.get(Organization, id)
    if not org:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found!")
    return org
  
