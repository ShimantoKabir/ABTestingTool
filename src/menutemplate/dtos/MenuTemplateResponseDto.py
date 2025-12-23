from dataclasses import dataclass

@dataclass
class MenuTemplateResponseDto:
  id: int
  name: str
  orgId: int
  tree: str
  orgName: str