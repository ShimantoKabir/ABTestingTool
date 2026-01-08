from dataclasses import dataclass
from typing import Optional

@dataclass
class DecisionRequestDto:
  url: str # Required
  projectId: int # Required
  endUserId: Optional[int] = None
                     