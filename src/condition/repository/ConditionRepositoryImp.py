from src.condition.repository.ConditionRepository import ConditionRepository
from src.condition.model.Condition import Condition
from db import DBSessionDep
from sqlmodel import select
from fastapi import status, HTTPException

class ConditionRepositoryImp(ConditionRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def add(self, condition: Condition) -> Condition:
    self.db.add(condition)
    self.db.commit()
    self.db.refresh(condition)
    return condition

  def getByExperimentId(self, experimentId: int) -> list[Condition]:
    return self.db.exec(
      select(Condition).where(Condition.experimentId == experimentId)
    ).all()

  def getById(self, id: int) -> Condition:
    condition = self.db.get(Condition, id)
    if not condition:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    return condition

  def delete(self, condition: Condition):
    self.db.delete(condition)
    self.db.commit()