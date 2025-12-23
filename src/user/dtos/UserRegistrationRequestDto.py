from dataclasses import dataclass
from pydantic import EmailStr, constr, field_validator
from config import Config

@dataclass
class UserRegistrationRequestDto:
  email: EmailStr
  password: constr(min_length=1) # type: ignore
  orgId: int 
  
  @field_validator("password")
  def validatePassword(cls, password):
    if len(password) < int(Config.getValByKey("PASSWORD_MAX_CHAR")):
      raise ValueError(f"Password must be at least {Config.getValByKey("PASSWORD_MAX_CHAR")} characters long!")
    if not any(char.isupper() for char in password):
      raise ValueError("Password must contain at least one uppercase letter!")
    if not any(char.islower() for char in password):
      raise ValueError("Password must contain at least one lowercase letter!")
    if not any(char.isdigit() for char in password):
      raise ValueError("Password must contain at least one digit!")
    if not any(char in "!@#$%^&*()" for char in password):
      raise ValueError("Password must contain at least one special character!")
    return password