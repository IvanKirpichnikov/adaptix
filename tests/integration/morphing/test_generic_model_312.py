from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from tests_helpers.morphing import JSONSchemaFork, JSONSchemaOptItem, assert_morphing

from adaptix import Retort


@dataclass
class MinMax[NumberT]:
    min_value: Optional[NumberT]
    max_value: Optional[NumberT]


def test_generic_model_312():
    retort = Retort()

    assert_morphing(
        retort=retort,
        tp=MinMax[int],
        data={"min_value": 1, "max_value": 2},
        loaded=MinMax(1, 2),
        dumped={"min_value": 1, "max_value": 2},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {},
            "additionalProperties": JSONSchemaOptItem(input=True),
            "properties": {
                "min_value": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
                "max_value": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
            },
            "required": JSONSchemaFork(
                input=["min_value", "max_value"],
                output=["min_value", "max_value"],
            ),
            "type": "object",
        },
    )

    assert_morphing(
        retort=retort,
        tp=MinMax[Decimal],
        data={"min_value": "1", "max_value": "2"},
        loaded=MinMax(Decimal(1), Decimal(2)),
        dumped={"min_value": "1", "max_value": "2"},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {},
            "additionalProperties": JSONSchemaOptItem(input=True),
            "properties": {
                "min_value": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "max_value": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
            "required": JSONSchemaFork(
                input=["min_value", "max_value"],
                output=["min_value", "max_value"],
            ),
            "type": "object",
        },
    )
