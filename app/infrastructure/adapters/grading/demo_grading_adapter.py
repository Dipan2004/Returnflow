# app/infrastructure/adapters/grading/demo_grading_adapter.py
from __future__ import annotations

from app.application.ports.grading_port import GradingPort, GradingResult
from app.domain.value_objects.grade import Grade
from app.infrastructure.persistence.in_memory_store import STORE

REJECT_KEYWORDS = [
    "broken", "cracked", "shattered", "burned", "liquid",
    "water damage", "scratched screen", "bent",
]

GRADE_CONFIG: dict[str, dict[str, float | str]] = {
    "A": {"refund_pct": 1.0, "label": "Like New", "confidence": 95.0},
    "B": {"refund_pct": 0.85, "label": "Good Condition", "confidence": 87.0},
    "C": {"refund_pct": 0.70, "label": "Fair Condition", "confidence": 78.0},
    "D": {
        "refund_pct": 0.0,
        "label": "Damaged – Return Rejected",
        "confidence": 95.0,
    },
}


def _get_reason_for_return(return_id: str) -> str:
    returns = STORE.get("returns", {})
    data = returns.get(return_id)
    if isinstance(data, dict):
        return str(data.get("reason", ""))
    return ""


class DemoGradingAdapter(GradingPort):
    async def grade_images(
        self,
        bucket: str,
        image_keys: list[str],
    ) -> GradingResult:
        return_id = ""
        if image_keys:
            parts = image_keys[0].split("/")
            if len(parts) >= 2:
                return_id = parts[1]

        reason = _get_reason_for_return(return_id)
        image_count = len(image_keys) if image_keys else 4

        reason_lower = reason.lower()
        for keyword in REJECT_KEYWORDS:
            if keyword in reason_lower:
                return GradingResult(
                    grade=Grade.D,
                    confidence=95.0,
                    damage_labels=[],
                    damage_description=(
                        "Item shows customer-caused damage."
                        " Return rejected per policy."
                    ),
                    raw_label_count=0,
                    description_used_fallback=False,
                )

        if image_count >= 4:
            grade = Grade.A
        elif image_count >= 2:
            grade = Grade.B
        else:
            grade = Grade.C

        config = GRADE_CONFIG[grade.value]
        confidence: float = float(config["confidence"])
        return GradingResult(
            grade=grade,
            confidence=confidence,
            damage_labels=[],
            damage_description=f"Item is in {config['label']} condition.",
            raw_label_count=0,
            description_used_fallback=False,
        )
