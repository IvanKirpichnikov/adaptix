from dataclasses import dataclass, field
from decimal import Decimal

from adaptix import Retort
from adaptix.json_schema import Direction, generate_json_schema


@dataclass
class Product:
    id: int
    name: str
    price: Decimal
    tags: list[str] = field(default_factory=list)


retort = Retort()

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$ref": "#/$defs/Product",
    "$defs": {
        "Product": {
            "type": "object",
            "required": ["id", "name", "price", "tags"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}, "default": []},
                "price": {"type": "string"},
            },
        },
    },
}
assert generate_json_schema(retort, Product, Direction.OUTPUT) == schema
