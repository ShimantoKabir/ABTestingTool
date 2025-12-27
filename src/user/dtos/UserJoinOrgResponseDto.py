from dataclasses import dataclass

@dataclass
class UserJoinOrgResponseDto:
  message: str
  userId: int
  orgId: int