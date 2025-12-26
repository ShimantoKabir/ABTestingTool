from dataclasses import dataclass
from src.db.links.PermissionType import PermissionType

@dataclass
class ProjectAssignUserRequestDto:
  userId: int