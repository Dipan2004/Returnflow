# tests/unit/infrastructure/test_prompt_templates.py
from __future__ import annotations

from app.domain.entities.condition_grade import DamageLabel
from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.bedrock.prompt_templates import (
    build_system_prompt,
    build_user_prompt,
)


def test_system_prompt_contains_word_limit() -> None:
    prompt = build_system_prompt()
    assert "25" in prompt


def test_system_prompt_contains_buyer_perspective() -> None:
    prompt = build_system_prompt()
    assert "buyer" in prompt.lower()


def test_user_prompt_no_damage() -> None:
    prompt = build_user_prompt(Grade.A, [])
    assert "none" in prompt.lower()
    assert "A" in prompt


def test_user_prompt_with_labels() -> None:
    labels = [
        DamageLabel(name="Scratch", confidence=82.0),
        DamageLabel(name="Dent", confidence=65.0),
    ]
    prompt = build_user_prompt(Grade.B, labels)
    assert "Scratch" in prompt
    assert "82" in prompt
    assert "Dent" in prompt
    assert "B" in prompt


def test_user_prompt_sorts_labels_by_confidence_desc() -> None:
    labels = [
        DamageLabel(name="Dent", confidence=60.0),
        DamageLabel(name="Scratch", confidence=85.0),
    ]
    prompt = build_user_prompt(Grade.B, labels)
    assert prompt.index("Scratch") < prompt.index("Dent")