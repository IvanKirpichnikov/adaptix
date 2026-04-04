from dataclasses import dataclass

from adaptix import Retort
from adaptix.json_schema import Direction, generate_json_schemas_namespace


@dataclass
class Tag:
    id: int
    label: str


@dataclass
class Product:
    id: int
    tags: list[Tag]


@dataclass
class Category:
    id: int
    tags: list[Tag]


retort = Retort()

defs, schemas = generate_json_schemas_namespace(
    [
        (retort, Direction.INPUT, Category),
        (retort, Direction.INPUT, Product),
    ],
)
assert defs == {
    "Category": {
        "title": "Category",
        "type": "object",
        "required": ["id", "tags"],
        "properties": {
            "id": {"type": "integer"},
            "tags": {"type": "array", "items": {"$ref": "#/$defs/Tag"}},
        },
        "additionalProperties": True,
    },
    "Tag": {
        "title": "Tag",
        "type": "object",
        "required": ["id", "label"],
        "properties": {
            "id": {"type": "integer"},
            "label": {"type": "string"},
        },
        "additionalProperties": True,
    },
    "Product": {
        "title": "Product",
        "type": "object",
        "required": ["id", "tags"],
        "properties": {
            "id": {"type": "integer"},
            "tags": {"type": "array", "items": {"$ref": "#/$defs/Tag"}},
        },
        "additionalProperties": True,
    },
}
assert list(schemas) == [
    {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/$defs/Category",
    },
    {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/$defs/Product",
    },
]
