from dataclasses import dataclass
from pydantic import constr

@dataclass
class MenuTemplateCreateResponseDto:
  id: int
  name: str
  orgId: int
  tree: str