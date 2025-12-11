from sqlmodel import Field, SQLModel, ARRAY, String, Relationship
from typing import Optional, List
from pydantic import HttpUrl
from sqlalchemy import Column, DateTime, func
from datetime import datetime

from src.condition.model.Operator import Operator

class Condition(SQLModel, table=True):
  id: int = Field(default=None, primary_key=True)
  urls: List[HttpUrl] = Field(sa_column=Column(ARRAY(String), nullable=True))
  operator: Operator = Field(default=Operator.CONTAIN)
  experiment: Optional["Experiment"] = Relationship(back_populates="conditions") # type: ignore
  experimentId: Optional[int] = Field(default=None, foreign_key="experiment.id")
  createdAt: Optional[datetime] = Field(
    sa_column=Column(
      DateTime(timezone=True), server_default=func.now(), nullable=True
    )
  )
  updatedAt: Optional[datetime] = Field(
    sa_column=Column(
      DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
  )