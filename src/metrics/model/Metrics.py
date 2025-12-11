from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional

class Metrics(SQLModel, table=True):
  id: int = Field(default=None, primary_key=True)
  title: str = Field(default=None, nullable=True)
  custom: bool = Field(default=False , nullable=False)
  selector: str = Field(default=None, nullable=True)
  triggered: int = Field(default=None, nullable=True)
  experiment: Optional["Experiment"] = Relationship(back_populates="metrics") # type: ignore
  description: str = Field(default=None, nullable=True)
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