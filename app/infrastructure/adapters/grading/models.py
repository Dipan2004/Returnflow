# app/infrastructure/adapters/grading/models.py
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RawLabel:
    name: str
    confidence: float
    parents: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AggregatedLabelSet:
    labels: list[RawLabel]

    @classmethod
    def from_multi_image_results(
        cls, label_sets: list[list[RawLabel]]
    ) -> AggregatedLabelSet:
        best: dict[str, RawLabel] = {}
        for labels in label_sets:
            for label in labels:
                existing = best.get(label.name)
                if existing is None or label.confidence > existing.confidence:
                    best[label.name] = label
        return cls(labels=list(best.values()))

    def filter_by_min_confidence(self, min_confidence: float) -> AggregatedLabelSet:
        return AggregatedLabelSet(
            labels=[l for l in self.labels if l.confidence >= min_confidence]
        )