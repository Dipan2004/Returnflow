from __future__ import annotations

import logging
import sys
from typing import Any

from app.config import AppConfig, get_config

try:
    import structlog
except ModuleNotFoundError:
    structlog = None  # type: ignore[assignment]

_configured = False


class _FallbackLogger:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(self, event: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._log(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, event, **kwargs)

    def _log(self, level: int, event: str, **kwargs: Any) -> None:
        if kwargs:
            context = " ".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
            self._logger.log(level, "%s %s", event, context)
            return
        self._logger.log(level, event)


def configure_logging(config: AppConfig) -> None:
    global _configured

    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    if structlog is not None:
        shared_processors: list[structlog.types.Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
        ]

        if config.is_local:
            processors: list[structlog.types.Processor] = [
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        else:
            processors = [
                *shared_processors,
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    _configured = True


def get_logger(name: str) -> Any:
    if not _configured:
        configure_logging(get_config())
    if structlog is not None:
        return structlog.get_logger(name)
    return _FallbackLogger(logging.getLogger(name))
