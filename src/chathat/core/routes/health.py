from fastapi import APIRouter, HTTPException, Request

from chathat.core.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"description": "Application unavailable"}},
)
async def health(request: Request) -> HealthResponse:
    if not getattr(request.app.state, "started", False):
        raise HTTPException(status_code=503, detail="Application unavailable")
    return HealthResponse(status="ok")
