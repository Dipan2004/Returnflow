from __future__ import annotations

from dependency_injector import containers, providers

from app.config import AppConfig, get_config


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["app.api.routers"],
    )

    config: providers.Singleton[AppConfig] = providers.Singleton(get_config)