from fastapi import FastAPI

from chathat.core.application.lifespan import lifespan
from chathat.core.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.chathat.main:create_app", host="127.0.0.1", port=8000, reload=True)
