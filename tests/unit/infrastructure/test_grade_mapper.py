# tests/unit/infrastructure/test_grade_mapper.py
from __future__ import annotations

import pytest

from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.grading.grade_mapper import map_grade
from app.infrastructure.adapters.grading.models import AggregatedLabelSet, RawLabel


def _label_set(*pairs: tuple[str, float]) -> AggregatedLabelSet:
    return AggregatedLabelSet(labels=[RawLabel(name=n, confidence=c) for n, c in pairs])


def test_no_damage_labels_returns_grade_a() -> None:
    label_set = _label_set(("Shoe", 99.0), ("Sneaker", 95.0))
    grade, confidence = map_grade(label_set, min_confidence=60.0)
    assert grade == Grade.A
    assert confidence == 95.0


def test_low_confidence_damage_filtered_out() -> None:
    label_set = _label_set(("Scratch", 40.0))
    grade, confidence = map_grade(label_set, min_confidence=60.0)
    assert grade == Grade.A


def test_minor_scratch_returns_grade_a() -> None:
    label_set = _label_set(("Scratch", 45.0), ("Sneaker", 99.0))
    grade, _ = map_grade(label_set, min_confidence=60.0)
    assert grade == Grade.A


def test_heavy_damage_returns_grade_b() -> None:
    label_set = _label_set(("Dent", 80.0), ("Scratch", 75.0))
    grade, _ = map_grade(label_set, min_confidence=60.0)
    assert grade in (Grade.B, Grade.C)


def test_severe_damage_returns_donate() -> None:
    label_set = _label_set(
        ("Crack", 95.0), ("Broken", 92.0), ("Rust", 88.0), ("Torn", 85.0)
    )
    grade, _ = map_grade(label_set, min_confidence=60.0)
    assert grade == Grade.DONATE


def test_confidence_decreases_with_more_labels() -> None:
    single = _label_set(("Scratch", 70.0))
    many = _label_set(
        ("Scratch", 70.0), ("Dent", 68.0), ("Stain", 65.0),
        ("Dirt", 62.0), ("Worn", 61.0),
    )
    _, conf_single = map_grade(single, min_confidence=60.0)
    _, conf_many = map_grade(many, min_confidence=60.0)
    assert conf_many <= conf_single


def test_multi_image_aggregation_takes_max_confidence() -> None:
    set1 = [RawLabel(name="Scratch", confidence=70.0)]
    set2 = [RawLabel(name="Scratch", confidence=85.0)]
    aggregated = AggregatedLabelSet.from_multi_image_results([set1, set2])
    scratch = next(l for l in aggregated.labels if l.name == "Scratch")
    assert scratch.confidence == 85.0