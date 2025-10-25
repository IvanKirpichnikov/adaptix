from dataclasses import dataclass
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from adaptix import Retort
from adaptix.integrations.sqlalchemy import AdaptixJSON


class Base(DeclarativeBase):
    pass


@dataclass
class SignupMeta:
    source: str
    campaign: str
    referrer: str


@dataclass
class UserMetadata:
    signup: Optional[SignupMeta]
    imported_from: Optional[str]


_db_retort = Retort()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    # [NOTE] Adaptix can integrate with SQLAlchemy to handle JSON columns.
    # It seamlessly transforms your models to and from dictionaries.
    preferences: Mapped[UserMetadata] = mapped_column(AdaptixJSON(_db_retort, UserMetadata))


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    content: str
