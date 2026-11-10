from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from chathat.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.started = True
    try:
        yield
    finally:
        app.state.started = False


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.chathat.main:create_app", host="127.0.0.1", port=8000, reload=True)
