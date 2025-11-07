import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from starlette import status

from .app import create_app
from .config import Config, load_config
from .db_models import Base, Post, User, UserMetadata
from .dependencies import make_session_factory, make_user_gateway


@pytest.fixture
async def test_client():
    # This connection mode allows simulating a real world use case
    # with parallel and connection queue using inmemory db
    app = create_app(
        Config(
            log_level="DEBUG",
            db_url="sqlite+aiosqlite:///file:some_memdb?mode=memory&cache=shared&uri=true",
            db_pool_size=1,
            debug_mode=True,
        ),
    )
    with TestClient(app) as test_client:
        async with app.state.engine.connect() as connection:
            await connection.run_sync(Base.metadata.create_all)
            # We need to keep a single connection open so the database stays in memory.
            yield test_client


@pytest.fixture
def app(test_client):
    return test_client.app


@pytest.fixture
def session_factory(app):
    return make_session_factory(app.state.engine)


def test_config_loading():
    config = load_config(
        {
            "LOG_LEVEL": "DEBUG",
            "DB_URL": "sqlite+aiosqlite:///file:some_memdb?mode=memory&cache=shared&uri=true",
            "DB_POOL_SIZE": "10",
            "DEBUG_MODE": "yes",
            "EXTRA_KEY": "EXTRA_VALUE",  # Unknown fields are ignored
        },
    )
    assert config == Config(
        log_level="DEBUG",
        db_url="sqlite+aiosqlite:///file:some_memdb?mode=memory&cache=shared&uri=true",
        db_pool_size=10,
        debug_mode=True,
    )


async def test_sqlalchemy_insert_and_get(app, session_factory):
    async with session_factory() as session:
        user = User(
            first_name="Ursula",
            last_name="Kroeber Le Guin",
            meta=UserMetadata(
                signup=None,
                imported_from="auto",
            ),
        )
        session.add(user)
        await session.commit()

    async with session_factory() as session:
        user_gateway = make_user_gateway(session, app.state.user_cache)
        new_user = await user_gateway.get_user_by_id(user.id)

        assert new_user.first_name == "Ursula"
        assert new_user.last_name == "Kroeber Le Guin"
        assert (
            new_user.meta
            ==
            UserMetadata(
                signup=None,
                imported_from="auto",
            )
        )


async def test_cache_set_and_get(app, session_factory):
    async with session_factory() as session:
        user = User(
            first_name="Ursula",
            last_name="Kroeber Le Guin",
            meta=UserMetadata(
                signup=None,
                imported_from="auto",
            ),
        )
        session.add(user)
        await session.commit()

    async with session_factory() as session:
        user_gateway = make_user_gateway(session, app.state.user_cache)
        new_user = await user_gateway.get_user_by_id(user.id)
        assert new_user.first_name == "Ursula"

    async with session_factory() as session:
        await session.execute(delete(User).where(User.id == user.id))
        await session.commit()

        user_gateway = make_user_gateway(session, app.state.user_cache)
        new_user = await user_gateway.get_user_by_id(user.id)  # data is fetched from cache
        assert new_user.first_name == "Ursula"


async def test_route_get_user_by_id(test_client, session_factory):
    async with session_factory() as session:
        user = User(
            first_name="Ursula",
            last_name="Kroeber Le Guin",
            meta=UserMetadata(
                signup=None,
                imported_from="auto",
            ),
        )
        session.add(user)
        await session.flush()
        session.add(Post(user_id=user.id, content="text1"))
        session.add(Post(user_id=user.id, content="text2"))
        await session.commit()

    response = test_client.get(f"/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "full_name": "Ursula Kroeber Le Guin",
        "posts_count": 2,
    }


async def test_route_get_paginated_users(test_client: TestClient, session_factory):
    meta = UserMetadata(
        signup=None,
        imported_from="auto",
    )
    async with session_factory() as session:
        session.add_all(
            [
                User(
                    first_name="Ursula",
                    last_name="Kroeber Le Guin",
                    meta=meta,
                ),
                User(
                    first_name="Isaac",
                    last_name="Asimov",
                    meta=meta,
                ),
                User(
                    first_name="Stanislaw",
                    last_name="Lem",
                    meta=meta,
                ),
            ],
        )
        await session.commit()

    response = test_client.get("/admin/users", params={"limit": 10})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": 1, "first_name": "Ursula", "last_name": "Kroeber Le Guin"},
        {"id": 2, "first_name": "Isaac", "last_name": "Asimov"},
        {"id": 3, "first_name": "Stanislaw", "last_name": "Lem"},
    ]

    response = test_client.get("/admin/users", params={"start_id": 1, "limit": 10})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": 2, "first_name": "Isaac", "last_name": "Asimov"},
        {"id": 3, "first_name": "Stanislaw", "last_name": "Lem"},
    ]

    response = test_client.get("/admin/users", params={"start_id": 1, "limit": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": 2, "first_name": "Isaac", "last_name": "Asimov"},
    ]
