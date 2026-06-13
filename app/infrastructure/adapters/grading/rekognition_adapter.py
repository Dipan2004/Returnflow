# app/infrastructure/adapters/grading/rekognition_adapter.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from botocore.exceptions import ClientError

from app.application.ports.grading_port import DamageDescriptionResult, GradingPort, GradingResult
from app.domain.entities.condition_grade import DamageLabel
from app.domain.exceptions import InfrastructureError
from app.domain.value_objects.grade import Grade
from app.infrastructure.adapters.grading.grade_mapper import extract_damage_labels, map_grade
from app.infrastructure.adapters.grading.models import AggregatedLabelSet, RawLabel

if TYPE_CHECKING:
    from mypy_boto3_rekognition import RekognitionClient


class RekognitionGradingAdapter(GradingPort):
    def __init__(
        self,
        rekognition_client: RekognitionClient,
        max_labels: int,
        min_confidence: float,
    ) -> None:
        self._client = rekognition_client
        self._max_labels = max_labels
        self._min_confidence = min_confidence

    async def grade_images(
        self,
        bucket: str,
        image_keys: list[str],
    ) -> GradingResult:
        label_sets = await asyncio.gather(
            *[self._detect_labels(bucket, key) for key in image_keys]
        )
        aggregated = AggregatedLabelSet.from_multi_image_results(list(label_sets))
        grade, confidence = map_grade(aggregated, self._min_confidence)
        damage_labels = extract_damage_labels(
            aggregated.filter_by_min_confidence(self._min_confidence)
        )
        return GradingResult(
            grade=grade,
            confidence=confidence,
            damage_labels=damage_labels,
            raw_label_count=len(aggregated.labels),
        )

    async def describe_damage(
        self,
        grade: Grade,
        damage_labels: list[DamageLabel],
    ) -> DamageDescriptionResult:
        if not damage_labels:
            return DamageDescriptionResult(
                description="No visible damage detected. Product appears in excellent condition.",
                model_id="rule-based",
            )
        label_summary = "; ".join(
            f"{dl.name} ({dl.confidence:.0f}%)" for dl in damage_labels
        )
        description = self._build_description(grade, label_summary)
        return DamageDescriptionResult(description=description, model_id="rule-based")

    def _build_description(self, grade: Grade, label_summary: str) -> str:
        prefix_map: dict[Grade, str] = {
            Grade.A: "Minor cosmetic issue detected",
            Grade.B: "Moderate damage detected",
            Grade.C: "Significant damage detected",
            Grade.DONATE: "Extensive damage — not suitable for resale",
            Grade.SCRAP: "Severe damage — end of life condition",
        }
        prefix = prefix_map.get(grade, "Damage detected")
        return f"{prefix}: {label_summary}."

    async def _detect_labels(self, bucket: str, key: str) -> list[RawLabel]:
        try:
            response: dict[str, Any] = await asyncio.to_thread(
                self._client.detect_labels,
                Image={"S3Object": {"Bucket": bucket, "Name": key}},
                MaxLabels=self._max_labels,
                MinConfidence=self._min_confidence,
            )
        except ClientError as exc:
            raise InfrastructureError("Rekognition", str(exc)) from exc

        return [
            RawLabel(
                name=label["Name"],
                confidence=label["Confidence"],
                parents=[p["Name"] for p in label.get("Parents", [])],
            )
            for label in response.get("Labels", [])
        ]