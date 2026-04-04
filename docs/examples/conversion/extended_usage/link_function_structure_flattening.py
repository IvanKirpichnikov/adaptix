from dataclasses import dataclass

from adaptix import P
from adaptix.conversion import get_converter, link_function


@dataclass
class Position:
    id: int
    title: str


@dataclass
class Employee:
    id: int
    name: str
    last_name: str
    position: Position


@dataclass
class OutTrainer:
    id: int
    name: str
    last_name: str
    position: str


make_out_trainer = get_converter(
    Employee, OutTrainer,
    recipe=[
        link_function(
            lambda trainer: trainer.position.title,
            P[OutTrainer].position,
        ),
    ],
)

assert (
    make_out_trainer(
        Employee(
            id=354,
            name="Name",
            last_name="LastName",
            position=Position(
                id=200,
                title="Position",
            ),
        ),
    )
    ==
    OutTrainer(
        id=354,
        name="Name",
        last_name="LastName",
        position="Position",
    )
)
