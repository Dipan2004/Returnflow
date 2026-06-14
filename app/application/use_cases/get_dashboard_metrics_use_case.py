# app/application/use_cases/get_dashboard_metrics_use_case.py
from __future__ import annotations

from decimal import Decimal

from app.application.ports.dashboard_repository import DashboardRepository
from app.application.use_cases.dashboard_dto import DashboardResponse
from app.domain.services.dashboard_aggregation_engine import DashboardAggregationEngine


class GetDashboardMetricsUseCase:
    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        aggregation_engine: DashboardAggregationEngine,
    ) -> None:
        self._repository = dashboard_repository
        self._engine = aggregation_engine

    async def execute(self, period: str = "last_30_days") -> DashboardResponse:
        metrics = await self._repository.get_latest(period)
        if metrics is None:
            metrics = self._engine.compute(
                period=period,
                route_counts={},
                accepted=0,
                rejected=0,
                tamper_alerts=0,
                fraud_overrides=0,
                total_recovery=Decimal("0"),
                total_returns=0,
                avg_return_probability=0.0,
            )
        return DashboardResponse(
            period=metrics.period,
            total_returns=metrics.total_returns,
            p2p_routes=metrics.p2p_routes,
            resell_routes=metrics.resell_routes,
            refurbish_routes=metrics.refurbish_routes,
            donation_routes=metrics.donation_routes,
            scrap_routes=metrics.scrap_routes,
            accepted_buyers=metrics.accepted_buyers,
            rejected_buyers=metrics.rejected_buyers,
            tamper_alerts=metrics.tamper_alerts,
            fraud_overrides=metrics.fraud_overrides,
            revenue_recovered=metrics.revenue_recovered,
            average_recovery_rate=metrics.average_recovery_rate,
            average_return_probability=metrics.average_return_probability,
            computed_at=metrics.computed_at,
        )
