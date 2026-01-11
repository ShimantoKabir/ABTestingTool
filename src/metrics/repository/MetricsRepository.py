from abc import ABC, abstractmethod
from src.metrics.model.Metrics import Metrics
from src.metrics.model.TriggerMode import TriggerMode

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
  def incrementTrigger(self, id: int, mode: TriggerMode):
    pass

  @abstractmethod
  def getByExperimentAndEventName(self, experimentId: int, eventName: str) -> Metrics:
    pass

  @abstractmethod
  def markAsPrimary(self, metricId: int, experimentId: int):
    pass