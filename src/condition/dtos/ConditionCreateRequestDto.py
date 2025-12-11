from typing import List
from pydantic import BaseModel, field_validator, HttpUrl, TypeAdapter, ValidationError
from src.condition.model.Operator import Operator

class ConditionCreateRequestDto(BaseModel):
  urls: List[str]
  operator: Operator

  @field_validator('urls')
  def validate_urls(cls, v):
    if not v:
      raise ValueError("The list of URLs cannot be empty!")

    for url in v:
      try:
        TypeAdapter(HttpUrl).validate_python(url)
      except ValidationError:
        raise ValueError(f"Invalid URL format: {url}!")
    return v