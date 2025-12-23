from dataclasses import dataclass
from pydantic import EmailStr

@dataclass
class UserRegistrationResponseDto:
  id: int
  email: EmailStr
  message: str