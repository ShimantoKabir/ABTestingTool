from typing import Optional
from pydantic import BaseModel, model_validator

class MetricsCreateRequestDto(BaseModel):
  title: str
  custom: bool = False
  selector: Optional[str] = None
  description: Optional[str] = None

  @model_validator(mode='after')
  def validate_selector(self):
    # If it is NOT a custom event (meaning it tracks clicks/elements), a selector is required.
    if not self.custom and not self.selector:
      raise ValueError("Selector is required for non-custom metrics")
    return self