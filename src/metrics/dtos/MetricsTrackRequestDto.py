from dataclasses import dataclass
from typing import Optional

@dataclass
class MetricsTrackRequestDto:
    # Required fields first
    experimentId: int
    variationId: int
    custom: bool
    isPreview: bool = False
    
    # Optional fields follow
    metricsId: Optional[int] = None
    eventName: Optional[str] = None
    