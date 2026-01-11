from dataclasses import dataclass

@dataclass
class PreviewRequestDto:
  experimentId: int
  variationId: int