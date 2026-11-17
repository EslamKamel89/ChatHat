from typing import Annotated

from fastapi import Depends, Request

from chathat.core.application.state import AppState, get_app_state


def provide_app_state(request: Request) -> AppState:
    return get_app_state(request.app)


AppStateDependency = Annotated[AppState, Depends(provide_app_state)]
