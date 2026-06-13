from __future__ import annotations

from datetime import UTC, datetime

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class FraudAssessment:
    def __init__(
        self,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        purchase_count_in_window: int,
        window_hours: int,
        bulk_buy_threshold: int,
        assessed_at: datetime,
        flagged: bool,
        flag_reason: str | None = None,
    ) -> None:
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if purchase_count_in_window < 0:
            raise DomainValidationError(
                f"purchase_count_in_window cannot be negative, got {purchase_count_in_window}"
            )
        if window_hours < 1:
            raise DomainValidationError("window_hours must be at least 1")
        if bulk_buy_threshold < 1:
            raise DomainValidationError("bulk_buy_threshold must be at least 1")
        if flagged and not flag_reason:
            raise DomainValidationError("flag_reason is required when fraud is flagged")

        self._return_id = return_id
        self._buyer_id = buyer_id.strip()
        self._sku_id = sku_id.strip()
        self._purchase_count_in_window = purchase_count_in_window
        self._window_hours = window_hours
        self._bulk_buy_threshold = bulk_buy_threshold
        self._assessed_at = assessed_at
        self._flagged = flagged
        self._flag_reason = flag_reason

    @classmethod
    def assess(
        cls,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        purchase_count_in_window: int,
        window_hours: int,
        bulk_buy_threshold: int,
    ) -> FraudAssessment:
        flagged = purchase_count_in_window >= bulk_buy_threshold
        flag_reason = (
            f"Buyer purchased {purchase_count_in_window} units of SKU '{sku_id}' "
            f"in the last {window_hours} hours (threshold: {bulk_buy_threshold})"
            if flagged
            else None
        )
        return cls(
            return_id=return_id,
            buyer_id=buyer_id,
            sku_id=sku_id,
            purchase_count_in_window=purchase_count_in_window,
            window_hours=window_hours,
            bulk_buy_threshold=bulk_buy_threshold,
            assessed_at=datetime.now(UTC),
            flagged=flagged,
            flag_reason=flag_reason,
        )

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def buyer_id(self) -> str:
        return self._buyer_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def purchase_count_in_window(self) -> int:
        return self._purchase_count_in_window

    @property
    def window_hours(self) -> int:
        return self._window_hours

    @property
    def bulk_buy_threshold(self) -> int:
        return self._bulk_buy_threshold

    @property
    def assessed_at(self) -> datetime:
        return self._assessed_at

    @property
    def flagged(self) -> bool:
        return self._flagged

    @property
    def flag_reason(self) -> str | None:
        return self._flag_reason

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FraudAssessment):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"FraudAssessment(return_id={self._return_id}, buyer={self._buyer_id}, "
            f"flagged={self._flagged})"
        )
