# app/domain/entities/size_recommendation.py
from __future__ import annotations

from app.domain.exceptions import DomainValidationError


class SizeRecommendation:
    def __init__(
        self,
        sku_id: str,
        current_size: str,
        recommended_size: str,
        confidence: float,
        mismatch_rate: float,
        brand: str,
    ) -> None:
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if not current_size or not current_size.strip():
            raise DomainValidationError("current_size cannot be empty")
        if not recommended_size or not recommended_size.strip():
            raise DomainValidationError("recommended_size cannot be empty")
        if not (0.0 <= confidence <= 1.0):
            raise DomainValidationError(f"confidence must be 0.0-1.0, got {confidence}")
        if not (0.0 <= mismatch_rate <= 1.0):
            raise DomainValidationError(f"mismatch_rate must be 0.0-1.0, got {mismatch_rate}")
        if not brand or not brand.strip():
            raise DomainValidationError("brand cannot be empty")

        self._sku_id = sku_id.strip()
        self._current_size = current_size.strip()
        self._recommended_size = recommended_size.strip()
        self._confidence = confidence
        self._mismatch_rate = mismatch_rate
        self._brand = brand.strip()

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def current_size(self) -> str:
        return self._current_size

    @property
    def recommended_size(self) -> str:
        return self._recommended_size

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def mismatch_rate(self) -> float:
        return self._mismatch_rate

    @property
    def brand(self) -> str:
        return self._brand

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SizeRecommendation):
            return NotImplemented
        return self._sku_id == other._sku_id and self._current_size == other._current_size

    def __repr__(self) -> str:
        return (
            f"SizeRecommendation(sku={self._sku_id}, current={self._current_size}, "
            f"recommended={self._recommended_size}, confidence={self._confidence})"
        )
