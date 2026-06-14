# app/infrastructure/adapters/grading/grade_mapper.py
from __future__ import annotations

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.grading.models import AggregatedLabelSet

_DAMAGE_WEIGHTS: dict[str, int] = {
    "Scratch": 1,
    "Abrasion": 1,
    "Stain": 1,
    "Dirt": 1,
    "Dent": 2,
    "Deformation": 2,
    "Damage": 2,
    "Worn": 2,
    "Torn": 3,
    "Rip": 3,
    "Crack": 3,
    "Rust": 3,
    "Broken": 3,
}

_DAMAGE_LABEL_NAMES: frozenset[str] = frozenset(_DAMAGE_WEIGHTS)

_GRADE_THRESHOLDS: list[tuple[float, Grade]] = [
    (1.5, Grade.A),
    (4.0, Grade.B),
    (8.0, Grade.C),
]


def extract_damage_labels(label_set: AggregatedLabelSet) -> list[DamageLabel]:
    return [
        DamageLabel(name=label.name, confidence=round(label.confidence, 1))
        for label in label_set.labels
        if label.name in _DAMAGE_LABEL_NAMES
    ]


def compute_weighted_score(damage_labels: list[DamageLabel]) -> float:
    return sum(
        dl.confidence * _DAMAGE_WEIGHTS.get(dl.name, 1)
        for dl in damage_labels
    ) / 100.0


def derive_confidence(
    grade: Grade,
    damage_labels: list[DamageLabel],
) -> float:
    base_confidence_map: dict[Grade, float] = {
        Grade.A: 95.0,
        Grade.B: 88.0,
        Grade.C: 82.0,
        Grade.DONATE: 78.0,
        Grade.SCRAP: 85.0,
    }
    base = base_confidence_map[grade]
    ambiguity_penalty = len(damage_labels) * 2.0
    return round(max(60.0, base - ambiguity_penalty), 1)


def map_grade(label_set: AggregatedLabelSet, min_confidence: float) -> tuple[Grade, float]:
    filtered = label_set.filter_by_min_confidence(min_confidence)
    damage_labels = extract_damage_labels(filtered)

    if not damage_labels:
        return Grade.A, 95.0

    weighted_score = compute_weighted_score(damage_labels)

    grade = Grade.DONATE
    for threshold, candidate_grade in _GRADE_THRESHOLDS:
        if weighted_score < threshold:
            grade = candidate_grade
            break

    confidence = derive_confidence(grade, damage_labels)
    return grade, confidence
