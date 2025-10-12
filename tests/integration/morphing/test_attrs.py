from attr import Factory, define, field
from tests_helpers.morphing import JSONSchemaOptItem, assert_morphing

from adaptix import Retort, name_mapping


def test_coordinates(accum):
    @define
    class Coordinates:
        x: int
        y: int

    retort = Retort(recipe=[accum])

    assert_morphing(
        retort=retort,
        tp=Coordinates,
        data={"x": 1, "y": 2},
        loaded=Coordinates(x=1, y=2),
        dumped={"x": 1, "y": 2},
        json_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {
                "test_coordinates._locals_.Coordinates": {
                    "type": "object",
                    "title": Coordinates.__qualname__,
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                    },
                    "required": ["x", "y"],
                    "additionalProperties": JSONSchemaOptItem(input=True),
                },
            },
            "$ref": "#/$defs/test_coordinates._locals_.Coordinates",
        },
    )


@define
class WithDependentFactory:
    x = field(default=Factory(list))
    y = field(default=Factory(lambda self: set(self.x), takes_self=True))


def test_with_dependent_factory(accum):
    retort = Retort(recipe=[accum])

    loader = retort.get_loader(WithDependentFactory)
    assert loader({}) == WithDependentFactory()

    loader = retort.get_loader(WithDependentFactory)
    assert loader({"x": [1, 2, 3]}) == WithDependentFactory(x=[1, 2, 3], y={1, 2, 3})

    loader = retort.get_loader(WithDependentFactory)
    assert loader({"x": [1, 2, 3], "y": {2, 3}}) == WithDependentFactory(x=[1, 2, 3], y={2, 3})

    dumper = retort.get_dumper(WithDependentFactory)
    assert dumper(WithDependentFactory()) == {"x": [], "y": set()}

    dumper = retort.get_dumper(WithDependentFactory)
    assert dumper(WithDependentFactory(x=[1, 2, 3], y={2, 3})) == {"x": [1, 2, 3], "y": {2, 3}}


def test_with_dependent_factory_skipping(accum):
    retort = Retort(recipe=[accum, name_mapping(omit_default=True)])

    dumper = retort.get_dumper(WithDependentFactory)
    assert dumper(WithDependentFactory(x=[1, 2, 3], y={2, 3})) == {"x": [1, 2, 3], "y": {2, 3}}

    dumper = retort.get_dumper(WithDependentFactory)
    assert dumper(WithDependentFactory(x=[1, 2, 3], y={1, 2, 3})) == {"x": [1, 2, 3]}
