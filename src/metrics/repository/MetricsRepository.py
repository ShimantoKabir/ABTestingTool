from abc import ABC, abstractmethod
from src.metrics.model.Metrics import Metrics

class MetricsRepository(ABC):
  
  @abstractmethod
  def add(self, metric: Metrics) -> Metrics:
    pass

  @abstractmethod
  def getByExperimentId(self, experimentId: int) -> list[Metrics]:
    pass

  @abstractmethod
  def getById(self, id: int) -> Metrics:
    pass

  @abstractmethod
  def delete(self, metric: Metrics):
    pass

  @abstractmethod
  def incrementTrigger(self, id: int):
    pass