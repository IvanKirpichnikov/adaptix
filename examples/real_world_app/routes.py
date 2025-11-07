from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.responses import JSONResponse

from adaptix import P, Retort, name_mapping
from adaptix.conversion import impl_converter, link_function

from .db_models import User
from .dependencies import make_user_gateway
from .user_gateway import UserGateway, UserNotFoundError

router = APIRouter()


# [NOTE] This example demonstrates how adaptix can be useful within existing FastAPI applications.
# Adaptix acts as a glue layer between different parts of your system,
# translating your database (or business logic) models into Pydantic models.
#
# Unlike the .from_orm() mode, adaptix supports much more advanced functionality:
# 1) Validation of conversion correctness at configuration time
# 2) Interoperability with any type of model, supporting both directions — from and to Pydantic
# 3) Injection of additional data during conversion
# 4) Fine-grained customization options
# 5) Conversion configuration independent of parsing or dumping settings


class UserSchema(BaseModel):
    id: int
    full_name: str

    posts_count: int


@impl_converter(
    recipe=[
        link_function(
            lambda user: f"{user.first_name} {user.last_name}",
            P[UserSchema].full_name,
        ),
    ],
)
def db_user_to_schema(user: User, posts_count: int) -> UserSchema:  # type: ignore[empty-body]
    ...


@router.get(
    "/users/{user_id}",
)
async def get_user_by_id(
    user_id: int,
    user_gateway: Annotated[UserGateway, Depends(make_user_gateway)],
) -> UserSchema:
    try:
        db_user = await user_gateway.get_user_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_user_to_schema(db_user, await user_gateway.count_posts(user_id))


# [NOTE] This example illustrates how adaptix can be used for serialization in FastAPI applications.
# Here, you skip the declaration of intermediate classes and the creation of their instances,
# directly serializing objects from your database or business logic layer.
# This approach can significantly improve your application's performance.
#
# One downside of this method is the absence of an auto-generated JSON schema.
# However, this is usually not a major issue when following the Specification-First (API-First) approach,
# where the API specification is written before any code,
# serving as the single source of truth and being maintained separately.

retort = Retort(
    recipe=[
        name_mapping(User, skip=["meta"]),
    ],
)


@router.get(
    "/admin/users",
)
async def get_paginated_users(
    *,
    start_id: int = 0,
    limit: int,
    user_gateway: Annotated[UserGateway, Depends(make_user_gateway)],
):
    users = await user_gateway.get_paginated_users(start_id=start_id, limit=limit)
    return JSONResponse(
        content=retort.dump(users, Sequence[User]),
    )
