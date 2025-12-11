from dataclasses import dataclass
from typing import List
from src.condition.model.Operator import Operator

@dataclass
class ConditionResponseDto:
  id: int
  experimentId: int
  urls: List[str]
  operator: Operator