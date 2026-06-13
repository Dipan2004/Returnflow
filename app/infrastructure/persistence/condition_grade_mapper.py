# app/infrastructure/persistence/condition_grade_mapper.py
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.condition_grade import ConditionGrade, DamageLabel
from app.domain.value_objects.confidence_score import ConfidenceScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId

ENTITY_TYPE_CONDITION_GRADE = "CONDITION_GRADE"


def condition_grade_pk(return_id: ReturnId) -> str:
    return f"RETURN#{return_id.value}"


def condition_grade_sk() -> str:
    return "CONDITION_GRADE"


def to_item(condition_grade: ConditionGrade) -> dict[str, Any]:
    return {
        "PK": condition_grade_pk(condition_grade.return_id),
        "SK": condition_grade_sk(),
        "entity_type": ENTITY_TYPE_CONDITION_GRADE,
        "return_id": condition_grade.return_id.value,
        "grade": condition_grade.grade.value,
        "confidence": Decimal(str(condition_grade.confidence.value)),
        "damage_description": condition_grade.damage_description,
        "damage_labels": [
            {"name": d.name, "confidence": Decimal(str(d.confidence))}
            for d in condition_grade.damage_labels
        ],
        "image_keys": [k.value for k in condition_grade.image_keys],
        "routed_to_human_review": condition_grade.routed_to_human_review,
        "graded_at": condition_grade.graded_at.isoformat(),
    }


def from_item(item: dict[str, Any]) -> ConditionGrade:
    damage_labels = [
        DamageLabel(
            name=d["name"],
            confidence=float(d["confidence"]),
        )
        for d in item.get("damage_labels", [])
    ]
    return ConditionGrade(
        return_id=ReturnId(item["return_id"]),
        grade=Grade.from_string(item["grade"]),
        confidence=ConfidenceScore.of(float(item["confidence"])),
        damage_labels=damage_labels,
        damage_description=item["damage_description"],
        image_keys=[ImageKey(k) for k in item.get("image_keys", [])],
        graded_at=datetime.fromisoformat(item["graded_at"]).replace(tzinfo=UTC),
        routed_to_human_review=item.get("routed_to_human_review", False),
    )