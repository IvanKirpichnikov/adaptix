from dataclasses import dataclass

from adaptix import Retort
from adaptix.json_schema import (
    Direction,
    JSONSchema,
    JSONSchemaPatch,
    generate_json_schema,
    json_schema,
)


@dataclass
class Product:
    id: int


retort = Retort(
    recipe=[
        json_schema(
            Product,
            JSONSchemaPatch().merge_with(
                JSONSchema(description="My custom description"),
            ),
        ),
    ],
)

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$ref": "#/$defs/Product",
    "$defs": {
        "Product": {
            "type": "object",
            "description": "My custom description",
            "required": ["id"],
            "properties": {
                "id": {"type": "integer"},
            },
            "additionalProperties": True,
        },
    },
}
assert generate_json_schema(retort, Product, Direction.INPUT) == schema
