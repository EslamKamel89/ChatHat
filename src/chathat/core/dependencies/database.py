from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from chathat.core.dependencies.state import AppStateDependency


async def provide_session(state: AppStateDependency) -> AsyncGenerator[AsyncSession]:
    if state.database is None:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
    async with state.database.sessions() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(provide_session)]
