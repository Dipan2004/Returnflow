# app/infrastructure/adapters/bedrock/prompt_templates.py
from __future__ import annotations

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade

_SYSTEM_PROMPT = (
    "You are a product condition description writer for an e-commerce returns platform. "
    "Given a condition grade and a list of detected damage labels with confidence scores, "
    "write ONE sentence of at most 25 words describing the physical condition from a buyer's perspective. "
    "Rules: be factual and neutral; no vague terms like 'some wear' or 'gently used'; "
    "no hedging language; be specific about what is damaged and where if known; "
    "output only the description sentence with no preamble, no quotes, no punctuation beyond a single period."
)

_GRADE_CONTEXT: dict[Grade, str] = {
    Grade.A: "excellent — only minor cosmetic flaws if any",
    Grade.B: "good — moderate visible damage that does not affect function",
    Grade.C: "fair — significant damage visible",
    Grade.DONATE: "poor — extensive damage, not suitable for resale",
    Grade.SCRAP: "end-of-life — severe damage, structural integrity compromised",
}


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_user_prompt(grade: Grade, damage_labels: list[DamageLabel]) -> str:
    grade_context = _GRADE_CONTEXT.get(grade, "unknown condition")
    if not damage_labels:
        return f"Grade: {grade.value} ({grade_context})\nDetected issues: none"
    issues = "; ".join(
        f"{label.name} ({label.confidence:.0f}% confidence)"
        for label in sorted(damage_labels, key=lambda d: d.confidence, reverse=True)
    )
    return f"Grade: {grade.value} ({grade_context})\nDetected issues: {issues}"