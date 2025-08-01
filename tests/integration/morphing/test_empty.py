from dataclasses import dataclass

from tests_helpers.morphing import JSONSchemaOptItem, assert_morphing

from adaptix import Retort


@dataclass
class Empty:
    pass


def test_simple(accum):
    retort = Retort(recipe=[accum])

    assert_morphing(
        retort=retort,
        tp=Empty,
        data={"some_field": 1},
        loaded=Empty(),
        dumped={},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {
                "Empty": {
                    "additionalProperties": JSONSchemaOptItem(input=True),
                    "properties": {},
                    "required": [],
                    "type": "object",
                },
            },
            "$ref": "#/$defs/Empty",
        },
    )
