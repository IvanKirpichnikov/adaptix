from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from .config import Config
from .routes import router
from .user_gateway import UserCache


def create_app(config: Config) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.state.engine = create_async_engine(config.db_url, pool_size=config.db_pool_size)
    app.state.user_cache = UserCache()
    return app
