# mypy: disable-error-code="call-arg"
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class Book:
    title: str
    author: str


class BookDTO(BaseModel):
    title: str
    writer: str | None = None  # alias is forgotten!


book = Book(title="Fahrenheit 451", author="Ray Bradbury")
book_dto = BookDTO.model_validate(book, from_attributes=True)
assert book_dto == BookDTO(title="Fahrenheit 451", author=None)
