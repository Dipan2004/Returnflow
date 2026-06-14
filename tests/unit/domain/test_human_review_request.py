# tests/unit/domain/test_human_review_request.py
from __future__ import annotations

import pytest

from app.domain.entities.condition_grade import DamageLabel
from app.domain.entities.human_review_request import (
    HumanReviewRequest,
    ReviewPriority,
    ReviewStatus,
)
from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.return_id import ReturnId


def _make_damage_labels() -> list[DamageLabel]:
    return [DamageLabel(name="Scratch", confidence=70.0)]


def _make_image_keys() -> list[ImageKey]:
    return [ImageKey.pending("TEST123", 1)]


def test_create_valid_review_request() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=75.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Confidence below threshold",
    )
    assert request.status == ReviewStatus.PENDING
    assert request.confidence == 75.0
    assert request.threshold == 87.0


def test_create_raises_when_empty_reason() -> None:
    with pytest.raises(DomainValidationError, match="reason cannot be empty"):
        HumanReviewRequest.create(
            return_id=ReturnId("TEST123"),
            confidence=75.0,
            threshold=87.0,
            damage_labels=_make_damage_labels(),
            image_keys=_make_image_keys(),
            reason="",
        )


def test_create_raises_when_confidence_meets_threshold() -> None:
    with pytest.raises(DomainValidationError, match="meets threshold"):
        HumanReviewRequest.create(
            return_id=ReturnId("TEST123"),
            confidence=90.0,
            threshold=87.0,
            damage_labels=_make_damage_labels(),
            image_keys=_make_image_keys(),
            reason="Should not be created",
        )


def test_priority_critical_when_confidence_very_low() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=30.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Very low confidence",
    )
    assert request.priority == ReviewPriority.CRITICAL


def test_priority_high_when_confidence_moderate() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=50.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Moderate confidence",
    )
    assert request.priority == ReviewPriority.HIGH


def test_priority_medium_when_confidence_near_threshold() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=70.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Near threshold",
    )
    assert request.priority == ReviewPriority.MEDIUM


def test_priority_low_when_confidence_just_below_threshold() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=80.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Just below threshold",
    )
    assert request.priority == ReviewPriority.LOW


def test_to_queue_payload_contains_all_fields() -> None:
    request = HumanReviewRequest.create(
        return_id=ReturnId("TEST123"),
        confidence=72.0,
        threshold=87.0,
        damage_labels=_make_damage_labels(),
        image_keys=_make_image_keys(),
        reason="Below threshold",
    )
    payload = request.to_queue_payload()
    assert payload["return_id"] == "TEST123"
    assert payload["confidence"] == 72.0
    assert payload["threshold"] == 87.0
    assert payload["priority"] == "MEDIUM"
    assert payload["status"] == "PENDING"
    assert len(payload["damage_labels"]) == 1
    assert len(payload["image_keys"]) == 1
