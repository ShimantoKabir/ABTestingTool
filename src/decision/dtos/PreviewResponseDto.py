from dataclasses import dataclass
from typing import List, Optional
from src.decision.dtos.DecisionResponseDto import VariationDecisionDto
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto

@dataclass
class PreviewResponseDto:
  experimentId: int
  experimentJs: Optional[str]
  experimentCss: Optional[str]
  variation: VariationDecisionDto
  metrics: List[MetricsResponseDto]