from dataclasses import dataclass, field

from adaptix import Retort, name_mapping


@dataclass
class Book:
    title: str
    sub_title: str | None = None
    authors: list[str] = field(default_factory=list)


retort = Retort(
    recipe=[
        name_mapping(
            Book,
            omit_default="authors",
        ),
    ],
)

book = Book(title="Fahrenheit 451")
assert retort.dump(book) == {"title": "Fahrenheit 451", "sub_title": None}
