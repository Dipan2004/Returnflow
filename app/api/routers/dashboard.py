# app/api/routers/dashboard.py
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.api.schemas.dashboard_schemas import DashboardMetricsResponse
from app.application.use_cases.get_dashboard_metrics_use_case import (
    GetDashboardMetricsUseCase,
)
from app.container import Container

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/flywheel", response_model=DashboardMetricsResponse, status_code=200)
@inject
async def get_flywheel_metrics(
    period: str = Query(default="last_30_days"),
    use_case: GetDashboardMetricsUseCase = Depends(
        Provide[Container.get_dashboard_metrics_use_case]
    ),
) -> DashboardMetricsResponse:
    result = await use_case.execute(period)
    return DashboardMetricsResponse(
        period=result.period,
        total_returns=result.total_returns,
        p2p_routes=result.p2p_routes,
        resell_routes=result.resell_routes,
        refurbish_routes=result.refurbish_routes,
        donation_routes=result.donation_routes,
        scrap_routes=result.scrap_routes,
        accepted_buyers=result.accepted_buyers,
        rejected_buyers=result.rejected_buyers,
        tamper_alerts=result.tamper_alerts,
        fraud_overrides=result.fraud_overrides,
        revenue_recovered=result.revenue_recovered,
        average_recovery_rate=result.average_recovery_rate,
        average_return_probability=result.average_return_probability,
        computed_at=result.computed_at,
    )


@router.get("/metrics", response_model=DashboardMetricsResponse, status_code=200)
@inject
async def get_metrics(
    period: str = Query(default="last_30_days"),
    use_case: GetDashboardMetricsUseCase = Depends(
        Provide[Container.get_dashboard_metrics_use_case]
    ),
) -> DashboardMetricsResponse:
    result = await use_case.execute(period)
    return DashboardMetricsResponse(
        period=result.period,
        total_returns=result.total_returns,
        p2p_routes=result.p2p_routes,
        resell_routes=result.resell_routes,
        refurbish_routes=result.refurbish_routes,
        donation_routes=result.donation_routes,
        scrap_routes=result.scrap_routes,
        accepted_buyers=result.accepted_buyers,
        rejected_buyers=result.rejected_buyers,
        tamper_alerts=result.tamper_alerts,
        fraud_overrides=result.fraud_overrides,
        revenue_recovered=result.revenue_recovered,
        average_recovery_rate=result.average_recovery_rate,
        average_return_probability=result.average_return_probability,
        computed_at=result.computed_at,
    )
