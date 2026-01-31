from dataclasses import dataclass

from adaptix import Retort


@dataclass
class Cat:
    name: str
    breed: str


@dataclass
class Dog:
    name: str
    breed: str


retort = Retort()
retort.load({"name": "Tardar Sauce", "breed": "mixed"}, Cat | Dog)
