# tests/unit/domain/test_fraud_engine.py
from __future__ import annotations

from app.domain.entities.fraud_assessment import FraudRiskLevel
from app.domain.services.fraud_engine import FraudEngine
from app.domain.value_objects.return_id import ReturnId
from app.domain.value_objects.route import Route


def _rid() -> ReturnId:
    return ReturnId.generate()


class TestFraudEngine:
    def setup_method(self) -> None:
        self.engine = FraudEngine(bulk_buy_threshold=10, window_hours=72)

    def test_clean_buyer_gets_low_risk(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=1,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=0,
            returns_last_24h=1,
        )
        assert a.risk_level == FraudRiskLevel.LOW
        assert a.risk_score == 0

    def test_excessive_returns_triggers_signal(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=5,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=0,
            returns_last_24h=1,
        )
        assert a.risk_score == 30
        assert a.risk_level == FraudRiskLevel.LOW

    def test_medium_risk_two_signals(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=6,
            high_value_returns_in_window=3,
            same_sku_returns_in_window=0,
            returns_last_24h=1,
        )
        assert a.risk_score == 55
        assert a.risk_level == FraudRiskLevel.MEDIUM

    def test_high_risk_all_signals(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=10,
            high_value_returns_in_window=5,
            same_sku_returns_in_window=3,
            returns_last_24h=4,
        )
        assert a.risk_score == 100
        assert a.risk_level == FraudRiskLevel.HIGH

    def test_high_risk_overrides_p2p_route(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=10,
            high_value_returns_in_window=5,
            same_sku_returns_in_window=3,
            returns_last_24h=4,
            original_route=Route.P2P,
        )
        assert a.override_reason is not None
        assert a.override_reason.original_route == "P2P"
        assert a.override_reason.overridden_route == "RESELL"

    def test_medium_risk_does_not_override(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=6,
            high_value_returns_in_window=3,
            same_sku_returns_in_window=0,
            returns_last_24h=1,
            original_route=Route.P2P,
        )
        assert a.override_reason is None

    def test_no_override_when_no_original_route(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=10,
            high_value_returns_in_window=5,
            same_sku_returns_in_window=3,
            returns_last_24h=4,
            original_route=None,
        )
        assert a.override_reason is None

    def test_velocity_signal_alone(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=2,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=0,
            returns_last_24h=3,
        )
        assert a.risk_score == 20

    def test_repeat_sku_signal_alone(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=2,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=2,
            returns_last_24h=1,
        )
        assert a.risk_score == 25

    def test_four_signals_produce_expected_signals_list(self) -> None:
        a = self.engine.assess(
            return_id=_rid(), buyer_id="buyer_1", sku_id="SKU_1",
            total_returns_in_window=1,
            high_value_returns_in_window=0,
            same_sku_returns_in_window=0,
            returns_last_24h=0,
        )
        assert len(a.signals) == 4
