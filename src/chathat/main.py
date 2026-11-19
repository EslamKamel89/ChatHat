from fastapi import FastAPI

from chathat.core.application.lifespan import lifespan
from chathat.core.application.state import AppState
from chathat.core.database.sessions import create_database
from chathat.core.routes.health import router as health_router
from chathat.core.settings.config import Config


def create_app(*, config: Config | None = None) -> FastAPI:
    resolved_config = config if config is not None else Config()  # type: ignore
    app = FastAPI(lifespan=lifespan, debug=resolved_config.debug)
    database = (
        create_database(resolved_config.database_url)
        if resolved_config.database_url is not None
        else None
    )
    app.state.resources = AppState(
        config=resolved_config,
        database=database,
    )
    app.include_router(health_router)
    return app
