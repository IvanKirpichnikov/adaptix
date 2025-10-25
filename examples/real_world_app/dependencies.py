from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from starlette.requests import Request

from .user_gateway import UserCache, UserGateway


def make_engine(request: Request) -> AsyncEngine:
    return request.app.state.engine


async def make_session(engine: Annotated[AsyncEngine, Depends(make_engine)]):
    async with AsyncSession(engine) as session:
        yield session


def make_user_cache(request: Request) -> UserCache:
    return request.app.state.user_cache


def make_user_gateway(
    session: Annotated[AsyncSession, Depends(make_session)],
    user_cache: Annotated[UserCache, Depends(make_user_cache)],
):
    return UserGateway(session, user_cache)
