from sqlmodel import Field, SQLModel
from typing import Optional
from sqlalchemy import UniqueConstraint

class Result(SQLModel, table=True):
    # Ensure we don't have duplicate rows for the same metric+variation+experiment pair
    __table_args__ = (
      UniqueConstraint(
        "metricId", 
        "variationId", 
        "experimentId", 
        name="unique_metric_variation_experiment_result"
      ),
    )

    id: int = Field(default=None, primary_key=True)
    
    # Foreign Keys
    metricId: int = Field(foreign_key="metrics.id", index=True)
    variationId: int = Field(foreign_key="variation.id", index=True)
    experimentId: int = Field(foreign_key="experiment.id", index=True)
    
    # The actual data
    triggeredOnLIVE: int = Field(default=0)
    triggeredOnQA: int = Field(default=0)