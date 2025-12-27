from dataclasses import dataclass
from pydantic import EmailStr

@dataclass
class UserJoinOrgRequestDto:
  email: EmailStr
  orgId: int