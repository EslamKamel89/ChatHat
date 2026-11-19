from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from chathat.core.application.state import get_app_state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.started = True
    resources = get_app_state(app)

    try:
        yield
    finally:
        app.state.started = False
        if resources.database is not None:
            await resources.database.engine.dispose()
