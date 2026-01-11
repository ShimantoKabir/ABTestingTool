from abc import ABC, abstractmethod
from src.result.model.Result import Result
from src.metrics.model.TriggerMode import TriggerMode

class ResultRepository(ABC):
    
  @abstractmethod
  def increment(self, metricId: int, variationId: int, experimentId: int, mode: TriggerMode):
    """
    Increments the counter for a specific metric and variation.
    Creates the row if it doesn't exist.
    """
    pass

  @abstractmethod
  def getByMetricId(self, metricId: int) -> list[Result]:
    """
    Useful for fetching reports later.
    """
    pass

  @abstractmethod
  def getByExperimentId(self, experimentId: int) -> list[Result]:
    pass