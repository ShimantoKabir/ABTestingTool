from src.result.repository.ResultRepository import ResultRepository
from src.result.model.Result import Result
from src.metrics.model.TriggerMode import TriggerMode
from db import DBSessionDep
from sqlmodel import select
from src.variation.model.Variation import Variation
from src.metrics.model.Metrics import Metrics

class ResultRepositoryImp(ResultRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def increment(self, metricId: int, variationId: int, experimentId: int, mode: TriggerMode):
    # Check if the result row exists
    statement = (
      select(Result)
      .where(Result.metricId == metricId)
      .where(Result.variationId == variationId)
      .where(Result.experimentId == experimentId)
    )
    result = self.db.exec(statement).first()

    # If not, create a new one (counters default to 0)
    if not result:
      result = Result(metricId=metricId, variationId=variationId, experimentId=experimentId)
      self.db.add(result)
    
    # Increment based on mode
    if mode == TriggerMode.QA:
      result.triggeredOnQA += 1
    else:
      result.triggeredOnLIVE += 1
    
    self.db.commit()
    self.db.refresh(result)

  def getByMetricId(self, metricId: int) -> list[Result]:
    return self.db.exec(
      select(Result).where(Result.metricId == metricId)
    ).all()
  
  def getByExperimentId(self, experimentId: int):
    statement = (
      select(
        Result, 
        Metrics.title.label("metricName"),       
        Metrics.isPrimary,                        
        Variation.title.label("variationName")   
      )
      .join(Metrics, Result.metricId == Metrics.id)
      .join(Variation, Result.variationId == Variation.id) 
      .where(Result.experimentId == experimentId)
    )
    return self.db.exec(statement).all()