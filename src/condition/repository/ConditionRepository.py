from abc import ABC, abstractmethod
from src.condition.model.Condition import Condition

class ConditionRepository(ABC):
  
  @abstractmethod
  def add(self, condition: Condition) -> Condition:
    pass

  @abstractmethod
  def getByExperimentId(self, experimentId: int) -> list[Condition]:
    pass

  @abstractmethod
  def getById(self, id: int) -> Condition:
    pass

  @abstractmethod
  def delete(self, condition: Condition):
    pass