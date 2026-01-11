from dataclasses import dataclass

@dataclass
class ResultResponseDto:
  metricId: int
  metricName: str
  isPrimary: bool
  variationId: int
  variationName: str
  triggeredOnQA: int
  triggeredOnLIVE: int