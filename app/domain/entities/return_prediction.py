# app/domain/entities/return_prediction.py
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.keep_rate import KeepRate
from app.domain.value_objects.return_probability import ReturnProbability


class ReturnPrediction:
    def __init__(
        self,
        buyer_id: str,
        sku_id: str,
        size: str,
        return_probability: ReturnProbability,
        keep_rate: KeepRate,
        risk_level: str,
        size_warning: str | None,
        recommended_size: str | None,
        predicted_at: datetime,
    ) -> None:
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if not size or not size.strip():
            raise DomainValidationError("size cannot be empty")

        self._buyer_id = buyer_id.strip()
        self._sku_id = sku_id.strip()
        self._size = size.strip()
        self._return_probability = return_probability
        self._keep_rate = keep_rate
        self._risk_level = risk_level
        self._size_warning = size_warning
        self._recommended_size = recommended_size
        self._predicted_at = predicted_at

    @classmethod
    def create(
        cls,
        buyer_id: str,
        sku_id: str,
        size: str,
        return_probability: ReturnProbability,
        keep_rate: KeepRate,
        size_warning: str | None,
        recommended_size: str | None,
    ) -> ReturnPrediction:
        return cls(
            buyer_id=buyer_id,
            sku_id=sku_id,
            size=size,
            return_probability=return_probability,
            keep_rate=keep_rate,
            risk_level=return_probability.risk_level,
            size_warning=size_warning,
            recommended_size=recommended_size,
            predicted_at=datetime.now(UTC),
        )

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def size(self) -> str:
        return self._size

    @property
    def return_probability(self) -> ReturnProbability:
        return self._return_probability

    @property
    def keep_rate(self) -> KeepRate:
        return self._keep_rate

    @property
    def risk_level(self) -> str:
        return self._risk_level

    @property
    def size_warning(self) -> str | None:
        return self._size_warning

    @property
    def recommended_size(self) -> str | None:
        return self._recommended_size

    @property
    def predicted_at(self) -> datetime:
        return self._predicted_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReturnPrediction):
            return NotImplemented
        return (
            self._buyer_id == other._buyer_id
            and self._sku_id == other._sku_id
            and self._predicted_at == other._predicted_at
        )

    def __repr__(self) -> str:
        return (
            f"ReturnPrediction(buyer={self._buyer_id}, sku={self._sku_id}, "
            f"prob={self._return_probability.value}, risk={self._risk_level})"
        )
