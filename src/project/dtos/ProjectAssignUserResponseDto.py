from dataclasses import dataclass
from src.db.links.PermissionType import PermissionType

@dataclass
class ProjectAssignUserResponseDto:
  projectId: int
  userId: int
  message: str