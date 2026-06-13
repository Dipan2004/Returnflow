# app/main.py
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import health, returns
from app.api.routers import grades
from app.config import get_config
from app.container import Container
from app.domain.exceptions import (
    ConfidenceBelowThresholdError,
    DomainValidationError,
    EntityNotFoundError,
    FraudFlaggedError,
    ImageUploadError,
    InfrastructureError,
    InvalidStateTransitionError,
    QRTokenAlreadyScannedError,
    QRTokenNotFoundError,
    ReturnIQError,
)
from app.infrastructure.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config = get_config()
    configure_logging(config)
    container = Container()
    container.wire(packages=["app.api.routers"])
    app.state.container = container
    logger.info(
        "ReturnIQ starting",
        env=config.app_env,
        version=config.app_version,
    )
    yield
    logger.info("ReturnIQ shutting down")


def create_app() -> FastAPI:
    config = get_config()

    application = FastAPI(
        title="ReturnIQ",
        description="Intelligent returns disposition engine",
        version=config.app_version,
        lifespan=lifespan,
        docs_url="/docs" if config.is_local else None,
        redoc_url="/redoc" if config.is_local else None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if config.is_local else [config.base_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(returns.router)
    application.include_router(grades.router)

    @application.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(DomainValidationError)
    async def domain_validation_handler(
        request: Request, exc: DomainValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(InvalidStateTransitionError)
    async def invalid_state_handler(
        request: Request, exc: InvalidStateTransitionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(ConfidenceBelowThresholdError)
    async def confidence_threshold_handler(
        request: Request, exc: ConfidenceBelowThresholdError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(ImageUploadError)
    async def image_upload_error_handler(
        request: Request, exc: ImageUploadError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(FraudFlaggedError)
    async def fraud_flagged_handler(
        request: Request, exc: FraudFlaggedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(QRTokenAlreadyScannedError)
    async def qr_scanned_handler(
        request: Request, exc: QRTokenAlreadyScannedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(QRTokenNotFoundError)
    async def qr_not_found_handler(
        request: Request, exc: QRTokenNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(InfrastructureError)
    async def infrastructure_handler(
        request: Request, exc: InfrastructureError
    ) -> JSONResponse:
        logger.error("Infrastructure error", service=exc.service, message=exc.message)
        return JSONResponse(
            status_code=503,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    @application.exception_handler(ReturnIQError)
    async def returniq_base_handler(
        request: Request, exc: ReturnIQError
    ) -> JSONResponse:
        logger.error("Unhandled ReturnIQ error", code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=500,
            content={"errors": [{"code": exc.code, "message": exc.message}]},
        )

    return application


app = create_app()