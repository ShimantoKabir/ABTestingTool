from src.result.repository.ResultRepository import ResultRepository
from src.result.dtos.ResultResponseDto import ResultResponseDto

class ResultService:
  def __init__(self, repo: ResultRepository):
    self.repo = repo

  def getResultsByExperiment(self, experimentId: int) -> list[ResultResponseDto]:
    data = self.repo.getByExperimentId(experimentId)
    
    # row structure: (ResultObject, metricName, isPrimary, variationName)
    return [
      ResultResponseDto(
        metricId=row.Result.metricId,
        metricName=row.metricName,      
        isPrimary=row.isPrimary,          
        variationId=row.Result.variationId,
        variationName=row.variationName, 
        triggeredOnQA=row.Result.triggeredOnQA,
        triggeredOnLIVE=row.Result.triggeredOnLIVE
      ) for row in data
    ]