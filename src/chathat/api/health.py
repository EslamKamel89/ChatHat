from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"description": "Application unavailable"}},
)
async def health(request: Request) -> HealthResponse:
    if not getattr(request.app.state, "started", False):
        raise HTTPException(status_code=503, detail="Application unavailable")
    return HealthResponse(status="ok")
