from dataclasses import dataclass
from typing import Optional

@dataclass
class MetricsResponseDto:
  id: int
  experimentId: int
  title: str
  custom: bool
  selector: Optional[str]
  description: Optional[str]
  isPrimary: bool