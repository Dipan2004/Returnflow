from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.domain.exceptions import DomainValidationError


class Money:
    __slots__ = ("_amount", "_currency")

    ZERO_DECIMAL = Decimal("0.00")
    QUANTIZE_EXP = Decimal("0.01")

    def __init__(self, amount: Decimal | float | str | int, currency: str = "INR") -> None:
        try:
            raw = Decimal(str(amount))
        except Exception:
            raise DomainValidationError(f"Invalid monetary amount: '{amount}'")
        if raw < Decimal("0"):
            raise DomainValidationError(f"Monetary amount cannot be negative, got {raw}")
        self._amount = raw.quantize(self.QUANTIZE_EXP, rounding=ROUND_HALF_UP)
        self._currency = currency.upper()

    @classmethod
    def zero(cls, currency: str = "INR") -> Money:
        return cls(Decimal("0"), currency)

    @classmethod
    def of(cls, amount: Decimal | float | str | int, currency: str = "INR") -> Money:
        return cls(amount, currency)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    def percentage(self, pct: float) -> Money:
        factor = Decimal(str(pct)) / Decimal("100")
        return Money(self._amount * factor, self._currency)

    def subtract(self, other: Money) -> Money:
        if self._currency != other._currency:
            raise DomainValidationError(
                f"Cannot subtract {other._currency} from {self._currency}"
            )
        result = self._amount - other._amount
        if result < Decimal("0"):
            return Money.zero(self._currency)
        return Money(result, self._currency)

    def add(self, other: Money) -> Money:
        if self._currency != other._currency:
            raise DomainValidationError(
                f"Cannot add {other._currency} to {self._currency}"
            )
        return Money(self._amount + other._amount, self._currency)

    def is_zero(self) -> bool:
        return self._amount == self.ZERO_DECIMAL

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount == other._amount and self._currency == other._currency

    def __lt__(self, other: Money) -> bool:
        if self._currency != other._currency:
            raise DomainValidationError("Cannot compare different currencies")
        return self._amount < other._amount

    def __le__(self, other: Money) -> bool:
        if self._currency != other._currency:
            raise DomainValidationError("Cannot compare different currencies")
        return self._amount <= other._amount

    def __gt__(self, other: Money) -> bool:
        if self._currency != other._currency:
            raise DomainValidationError("Cannot compare different currencies")
        return self._amount > other._amount

    def __hash__(self) -> int:
        return hash((self._amount, self._currency))

    def __str__(self) -> str:
        return f"{self._currency} {self._amount}"

    def __repr__(self) -> str:
        return f"Money(amount={self._amount}, currency='{self._currency}')"