from dataclasses import dataclass
from typing import Generic, TypeVar

from adaptix import Retort

T = TypeVar("T")


@dataclass
class MinMax(Generic[T]):
    min: T | None = None
    max: T | None = None


retort = Retort()

data = {"min": 10, "max": 20}
min_max = retort.load(data, MinMax[int])
assert min_max == MinMax(min=10, max=20)
assert retort.dump(min_max, MinMax[int]) == data
