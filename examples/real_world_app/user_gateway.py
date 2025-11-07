import json
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adaptix import Retort

from .db_models import Post, User


class UserNotFoundError(Exception):
    pass


class UserCache:
    """This class demonstrates how adaptix can be used in combination with caching systems such as Redis.

    In databases of this kind, both keys and values are typically stored as strings (or byte strings).
    Adaptix handles the conversion of models into dictionaries,
    which you can then serialize into strings using any JSON library.
    """
    _retort = Retort()

    def __init__(self) -> None:
        self._dict: dict[str, str] = {}

    # [HINT] Note that what's being returned here is an SQLAlchemy model.
    # Adaptix can natively work with many different model kinds,
    # eliminating the need to create multiple identical copies of your model classes.
    async def get_user_by_id(self, user_id: int) -> User:
        try:
            record = self._dict[f"user:{user_id}"]
        except KeyError:
            raise UserNotFoundError

        return self._retort.load(json.loads(record), User)

    async def set_user_by_id(self, user: User) -> None:
        record = json.dumps(self._retort.dump(user))
        self._dict[f"user:{user.id}"] = record


class UserGateway:
    def __init__(self, session: AsyncSession, cache: UserCache):
        self._session = session
        self._cache = cache

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            return await self._cache.get_user_by_id(user_id)
        except UserNotFoundError:
            pass

        user = await self._session.get(User, user_id)
        if user is None:
            raise UserNotFoundError
        await self._cache.set_user_by_id(user)
        return user

    async def get_paginated_users(self, *, start_id: int, limit: int) -> Sequence[User]:
        result = await self._session.scalars(
            select(User).where(User.id > start_id).limit(limit).order_by(User.id),
        )
        return result.all()

    async def count_posts(self, user_id: int) -> int:
        result = await self._session.scalar(
            select(func.count("*")).select_from(Post).where(Post.user_id == user_id),
        )
        assert result is not None
        return result
