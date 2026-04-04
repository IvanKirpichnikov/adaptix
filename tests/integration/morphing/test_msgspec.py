from typing import ClassVar, Generic, TypeVar

from msgspec import Struct, field
from tests_helpers.morphing import JSONSchemaOptItem, assert_morphing

from adaptix import Retort


def test_basic(accum):
    class MyModel(Struct):
        f1: int
        f2: str

    retort = Retort(recipe=[accum])

    assert_morphing(
        retort=retort,
        tp=MyModel,
        data={"f1": 0, "f2": "a"},
        loaded=MyModel(f1=0, f2="a"),
        dumped={"f1": 0, "f2": "a"},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {
                "test_basic._locals_.MyModel": {
                    "additionalProperties": JSONSchemaOptItem(input=True),
                    "properties": {
                        "f1": {"type": "integer"},
                        "f2": {"type": "string"},
                    },
                    "required": ["f1", "f2"],
                    "type": "object",
                    "title": MyModel.__qualname__,
                },
            },
            "$ref": "#/$defs/test_basic._locals_.MyModel",
        },
    )


T = TypeVar("T")


def test_all_field_kinds(accum):
    class MyModel(Struct, Generic[T]):
        a: int
        b: T
        c: str = field(default="c", name="_c")
        d: ClassVar[float] = 2.11

    retort = Retort(recipe=[accum])
    assert retort.load({"a": 0, "b": 3}, MyModel[int]) == MyModel(a=0, b=3)
    assert retort.dump(MyModel(a=0, b=True), MyModel[bool]) == {"a": 0, "b": True, "c": "c"}
