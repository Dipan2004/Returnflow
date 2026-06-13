from __future__ import annotations

from datetime import UTC, datetime

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.return_id import ReturnId


class BuyerMatch:
    def __init__(
        self,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        distance_km: float,
        match_source: str,
        matched_at: datetime,
        notification_sent: bool = False,
        notification_sent_at: datetime | None = None,
        accepted: bool | None = None,
        responded_at: datetime | None = None,
    ) -> None:
        if not buyer_id or not buyer_id.strip():
            raise DomainValidationError("buyer_id cannot be empty")
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if distance_km < 0:
            raise DomainValidationError(
                f"distance_km cannot be negative, got {distance_km}"
            )
        if not match_source or not match_source.strip():
            raise DomainValidationError("match_source cannot be empty")

        self._return_id = return_id
        self._buyer_id = buyer_id.strip()
        self._sku_id = sku_id.strip()
        self._distance_km = distance_km
        self._match_source = match_source.strip()
        self._matched_at = matched_at
        self._notification_sent = notification_sent
        self._notification_sent_at = notification_sent_at
        self._accepted = accepted
        self._responded_at = responded_at

    @classmethod
    def create(
        cls,
        return_id: ReturnId,
        buyer_id: str,
        sku_id: str,
        distance_km: float,
        match_source: str,
    ) -> BuyerMatch:
        return cls(
            return_id=return_id,
            buyer_id=buyer_id,
            sku_id=sku_id,
            distance_km=distance_km,
            match_source=match_source,
            matched_at=datetime.now(UTC),
        )

    def mark_notified(self) -> None:
        if self._notification_sent:
            raise DomainValidationError("Buyer has already been notified for this match")
        self._notification_sent = True
        self._notification_sent_at = datetime.now(UTC)

    def record_response(self, accepted: bool) -> None:
        if self._accepted is not None:
            raise DomainValidationError("Buyer response has already been recorded")
        self._accepted = accepted
        self._responded_at = datetime.now(UTC)

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
    def distance_km(self) -> float:
        return self._distance_km

    @property
    def match_source(self) -> str:
        return self._match_source

    @property
    def matched_at(self) -> datetime:
        return self._matched_at

    @property
    def notification_sent(self) -> bool:
        return self._notification_sent

    @property
    def notification_sent_at(self) -> datetime | None:
        return self._notification_sent_at

    @property
    def accepted(self) -> bool | None:
        return self._accepted

    @property
    def responded_at(self) -> datetime | None:
        return self._responded_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuyerMatch):
            return NotImplemented
        return self._return_id == other._return_id and self._buyer_id == other._buyer_id

    def __hash__(self) -> int:
        return hash((self._return_id, self._buyer_id))

    def __repr__(self) -> str:
        return (
            f"BuyerMatch(return_id={self._return_id}, buyer={self._buyer_id}, "
            f"distance={self._distance_km}km)"
        )
