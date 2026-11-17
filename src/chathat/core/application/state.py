from dataclasses import dataclass
from typing import cast

from fastapi import FastAPI

from chathat.core.settings.config import Config


@dataclass(frozen=True, slots=True)
class AppState:
    config: Config


def get_app_state(app: FastAPI) -> AppState:
    return cast(AppState, app.state.resources)
