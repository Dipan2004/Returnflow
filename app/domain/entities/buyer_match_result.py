# app/domain/entities/buyer_match_result.py | 78 lines
from __future__ import annotations

from datetime import UTC, datetime

from app.domain.exceptions import DomainValidationError
from app.domain.value_objects.buyer_eligibility import BuyerEligibility
from app.domain.value_objects.demand_level import DemandLevel
from app.domain.value_objects.demand_score import DemandScore
from app.domain.value_objects.grade import Grade
from app.domain.value_objects.match_confidence import MatchConfidence
from app.domain.value_objects.return_id import ReturnId


class BuyerMatchResult:
    def __init__(
        self,
        return_id: ReturnId,
        sku_id: str,
        pincode: str,
        grade: Grade,
        demand_score: DemandScore,
        estimated_buyers: int,
        match_found: bool,
        eligibility: BuyerEligibility,
        confidence: MatchConfidence,
        p2p_recommended: bool,
        computed_at: datetime,
    ) -> None:
        if not sku_id or not sku_id.strip():
            raise DomainValidationError("sku_id cannot be empty")
        if not pincode or not pincode.strip():
            raise DomainValidationError("pincode cannot be empty")
        if estimated_buyers < 0:
            raise DomainValidationError(
                f"estimated_buyers cannot be negative, got {estimated_buyers}"
            )

        self._return_id = return_id
        self._sku_id = sku_id.strip()
        self._pincode = pincode.strip()
        self._grade = grade
        self._demand_score = demand_score
        self._estimated_buyers = estimated_buyers
        self._match_found = match_found
        self._eligibility = eligibility
        self._confidence = confidence
        self._p2p_recommended = p2p_recommended
        self._computed_at = computed_at

    @classmethod
    def create(
        cls,
        return_id: ReturnId,
        sku_id: str,
        pincode: str,
        grade: Grade,
        demand_score: DemandScore,
        estimated_buyers: int,
        match_found: bool,
        eligibility: BuyerEligibility,
        confidence: MatchConfidence,
        p2p_recommended: bool,
    ) -> BuyerMatchResult:
        return cls(
            return_id=return_id,
            sku_id=sku_id,
            pincode=pincode,
            grade=grade,
            demand_score=demand_score,
            estimated_buyers=estimated_buyers,
            match_found=match_found,
            eligibility=eligibility,
            confidence=confidence,
            p2p_recommended=p2p_recommended,
            computed_at=datetime.now(UTC),
        )

    @property
    def return_id(self) -> ReturnId:
        return self._return_id

    @property
    def sku_id(self) -> str:
        return self._sku_id

    @property
    def pincode(self) -> str:
        return self._pincode

    @property
    def grade(self) -> Grade:
        return self._grade

    @property
    def demand_score(self) -> DemandScore:
        return self._demand_score

    @property
    def demand_level(self) -> DemandLevel:
        return self._demand_score.level

    @property
    def estimated_buyers(self) -> int:
        return self._estimated_buyers

    @property
    def match_found(self) -> bool:
        return self._match_found

    @property
    def eligibility(self) -> BuyerEligibility:
        return self._eligibility

    @property
    def confidence(self) -> MatchConfidence:
        return self._confidence

    @property
    def p2p_recommended(self) -> bool:
        return self._p2p_recommended

    @property
    def computed_at(self) -> datetime:
        return self._computed_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuyerMatchResult):
            return NotImplemented
        return self._return_id == other._return_id

    def __hash__(self) -> int:
        return hash(self._return_id)

    def __repr__(self) -> str:
        return (
            f"BuyerMatchResult(return_id={self._return_id}, grade={self._grade}, "
            f"demand={self._demand_score.value}, eligible={self._eligibility})"
        )