from dataclasses import dataclass

@dataclass
class MetricsTrackResponseDto:
  message: str
  triggered: bool = True