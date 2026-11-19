from dataclasses import dataclass
from typing import cast

from fastapi import FastAPI

from chathat.core.database.sessions import Database
from chathat.core.settings.config import Config


@dataclass(frozen=True, slots=True)
class AppState:
    config: Config
    database: Database | None = None


def get_app_state(app: FastAPI) -> AppState:
    return cast(AppState, app.state.resources)
