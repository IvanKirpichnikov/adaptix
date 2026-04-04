from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, PositiveInt


class UserPydantic(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]


@dataclass(kw_only=True)
class UserDataclass:
    id: int
    name: str = "John Doe"
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]
