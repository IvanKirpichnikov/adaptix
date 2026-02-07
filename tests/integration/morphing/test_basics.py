from dataclasses import dataclass
from typing import Any

import pytest
from tests_helpers import with_trail
from tests_helpers.morphing import JSONSchemaOptItem, assert_load_error, assert_morphing, json_schema_error

from adaptix import DebugTrail, Retort, loader as loader_recipe
from adaptix._internal.morphing.json_schema.schema_model import JSONSchemaType
from adaptix.load_error import AggregateLoadError, TypeLoadError
from adaptix.struct_trail import get_trail


def test_any(accum):
    @dataclass
    class ExampleAny:
        field1: Any
        field2: Any

    retort = Retort(recipe=[accum])

    loader = retort.get_loader(ExampleAny)
    assert loader({"field1": 1, "field2": 1}) == ExampleAny(field1=1, field2=1)

    dumper = retort.get_dumper(ExampleAny)
    assert dumper(ExampleAny(field1=1, field2=1)) == {"field1": 1, "field2": 1}


def test_object(accum):
    @dataclass
    class ExampleObject:
        field1: object
        field2: object

    retort = Retort(recipe=[accum])

    loader = retort.get_loader(ExampleObject)
    assert loader({"field1": 1, "field2": 1}) == ExampleObject(field1=1, field2=1)

    dumper = retort.get_dumper(ExampleObject)
    assert dumper(ExampleObject(field1=1, field2=1)) == {"field1": 1, "field2": 1}


@dataclass
class ExampleInt:
    field1: int
    field2: int


def test_int(accum):
    retort = Retort(recipe=[accum])

    assert_morphing(
        retort=retort,
        tp=ExampleInt,
        data={"field1": 1, "field2": 1},
        loaded=ExampleInt(field1=1, field2=1),
        dumped={"field1": 1, "field2": 1},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {
                "ExampleInt": {
                    "additionalProperties": JSONSchemaOptItem(input=True),
                    "properties": {
                        "field1": {"type": "integer"},
                        "field2": {"type": "integer"},
                    },
                    "required": ["field1", "field2"],
                    "type": "object",
                    "title": "ExampleInt",
                },
            },
            "$ref": "#/$defs/ExampleInt",
        },
    )

    assert_load_error(
        retort=retort,
        tp=ExampleInt,
        data={"field1": 1, "field2": "1"},
        exc=AggregateLoadError(
            f"while loading model {ExampleInt}",
            [
                with_trail(
                    TypeLoadError(int, "1"),
                    ["field2"],
                ),
            ],
        ),
        json_schema_errors=[
            json_schema_error.at("field2").type(expected=JSONSchemaType.INTEGER),
        ],
    )


def test_int_lax_coercion(accum):
    retort = Retort(recipe=[accum], strict_coercion=False)
    loader = retort.get_loader(ExampleInt)

    assert loader({"field1": 1, "field2": 1}) == ExampleInt(field1=1, field2=1)
    assert loader({"field1": 1, "field2": "1"}) == ExampleInt(field1=1, field2=1)


def test_int_dt_disable(accum):
    retort = Retort(recipe=[accum], debug_trail=DebugTrail.DISABLE)
    loader = retort.get_loader(ExampleInt)

    assert loader({"field1": 1, "field2": 1}) == ExampleInt(field1=1, field2=1)

    with pytest.raises(TypeLoadError) as exc_info:
        loader({"field1": 1, "field2": "1"})

    assert list(get_trail(exc_info.value)) == []

    dumper = retort.get_dumper(ExampleInt)
    assert dumper(ExampleInt(field1=1, field2=1)) == {"field1": 1, "field2": 1}


def test_int_child():
    class CustomInt(int):
        pass

    default = CustomInt(0)

    @dataclass
    class Model:
        field1: CustomInt = default

    retort = Retort(recipe=[loader_recipe(CustomInt, CustomInt)])
    assert retort.load({}, Model).field1 is default
