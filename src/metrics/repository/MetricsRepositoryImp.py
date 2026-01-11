from src.metrics.repository.MetricsRepository import MetricsRepository
from src.metrics.model.Metrics import Metrics
from db import DBSessionDep
from sqlmodel import select
from fastapi import status, HTTPException
from sqlalchemy import update
from src.metrics.model.TriggerMode import TriggerMode

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

  def incrementTrigger(self, id: int, mode: TriggerMode):
    if mode == TriggerMode.QA:
      statement = (
        update(Metrics)
        .where(Metrics.id == id)
        .values(triggeredOnQA=Metrics.triggeredOnQA + 1) # <--- Updated
      )
    else:
      statement = (
        update(Metrics)
        .where(Metrics.id == id)
        .values(triggeredOnLIVE=Metrics.triggeredOnLIVE + 1) # <--- Updated
      )
      
    result = self.db.exec(statement)
    self.db.commit()

    if result.rowcount == 0:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found!")
    
  def getByExperimentAndEventName(self, experimentId: int, eventName: str) -> Metrics:
    statement = select(Metrics).where(
      Metrics.experimentId == experimentId,
      Metrics.selector == eventName,
      Metrics.custom == True
    )
    result = self.db.exec(statement).first()
    if not result:
      raise HTTPException(status_code=404, detail=f"Custom metric '{eventName}' not found for this experiment!")
    return result
  
  def markAsPrimary(self, metricId: int, experimentId: int):
    # Reset ALL metrics in this experiment to False
    statementReset = (
      update(Metrics)
      .where(Metrics.experimentId == experimentId)
      .values(isPrimary=False)
    )
    self.db.exec(statementReset)

    # Set the TARGET metric to True
    statementSet = (
      update(Metrics)
      .where(Metrics.id == metricId)
      .values(isPrimary=True)
    )
    self.db.exec(statementSet)
    
    self.db.commit()