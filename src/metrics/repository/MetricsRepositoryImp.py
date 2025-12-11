from src.metrics.repository.MetricsRepository import MetricsRepository
from src.metrics.model.Metrics import Metrics
from db import DBSessionDep
from sqlmodel import select
from fastapi import status, HTTPException
from sqlalchemy import update

class MetricsRepositoryImp(MetricsRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def add(self, metric: Metrics) -> Metrics:
    self.db.add(metric)
    self.db.commit()
    self.db.refresh(metric)
    return metric

  def getByExperimentId(self, experimentId: int) -> list[Metrics]:
    return self.db.exec(
      select(Metrics).where(Metrics.experimentId == experimentId)
    ).all()

  def getById(self, id: int) -> Metrics:
    metric = self.db.get(Metrics, id)
    if not metric:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    return metric

  def delete(self, metric: Metrics):
    self.db.delete(metric)
    self.db.commit()

  def incrementTrigger(self, id: int):
    # This generates SQL: UPDATE metrics SET triggered = triggered + 1 WHERE id = :id
    statement = (
        update(Metrics)
        .where(Metrics.id == id)
        .values(triggered=Metrics.triggered + 1)
    )
    result = self.db.exec(statement)
    self.db.commit()

    # Check if a row was actually updated (to handle 404 silently or explicitly)
    if result.rowcount == 0:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found!")