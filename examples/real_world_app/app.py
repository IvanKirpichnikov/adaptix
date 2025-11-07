from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine

from .config import Config
from .routes import router
from .user_gateway import UserCache


def create_app(config: Config) -> FastAPI:
    @asynccontextmanager
    async def lifespan(internal_app: FastAPI):
        try:
            yield
        finally:
            await internal_app.state.engine.dispose()

    app = FastAPI(debug=config.debug_mode, lifespan=lifespan)
    app.include_router(router)
    app.state.engine = create_async_engine(
        config.db_url,
        pool_size=config.db_pool_size,
        poolclass=AsyncAdaptedQueuePool,
    )
    app.state.user_cache = UserCache()
    return app
