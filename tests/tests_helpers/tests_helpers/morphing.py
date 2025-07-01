from dataclasses import dataclass
from typing import Any

from adaptix import Direction, Omitted, Retort, TypeHint
from adaptix._internal.morphing.facade.func import DumpedJSONSchema, generate_json_schema

try:
    import jsonschema
except ImportError:
    jsonschema = None


try:
    import jsonschema_rs
except ImportError:
    jsonschema_rs = None


def _validate_json_schema(json_schema: DumpedJSONSchema) -> DumpedJSONSchema:
    if jsonschema is not None:
        jsonschema.Draft202012Validator.check_schema(json_schema)
    if jsonschema_rs is not None:
        jsonschema_rs.meta.validate(json_schema)
    return json_schema


def _validate_by_json_schema(data, json_schema: DumpedJSONSchema) -> None:
    if jsonschema is not None:
        jsonschema.Draft202012Validator(json_schema).validate(data)
    if jsonschema_rs is not None:
        jsonschema_rs.validate(json_schema, data)


@dataclass
class JSONSchemaFork:
    input: Any
    output: Any


class JSONSchemaOptItem:
    def __init__(self, input: Any = Omitted(), output: Any = Omitted()): # noqa: A002
        assert isinstance(input, Omitted) ^ isinstance(output, Omitted)
        self.value = input if not isinstance(input, Omitted) else output
        self.direction = Direction.INPUT if not isinstance(input, Omitted) else Direction.OUTPUT


def _keep_item(data, direction: Direction) -> bool:
    if not isinstance(data, JSONSchemaOptItem):
        return True
    return data.direction == direction


def _resolve_json_schema(data, direction: Direction):
    if isinstance(data, JSONSchemaFork):
        if direction == Direction.INPUT:
            return data.input
        if direction == Direction.OUTPUT:
            return data.output
        raise ValueError
    if isinstance(data, JSONSchemaOptItem):
        return data.value
    if isinstance(data, dict):
        return {
            _resolve_json_schema(k, direction): _resolve_json_schema(v, direction)
            for k, v in data.items()
            if _keep_item(k, direction) and _keep_item(v, direction)
        }
    if isinstance(data, list):
        return [
            _resolve_json_schema(element, direction)
            for element in data
            if _keep_item(element, direction)
        ]
    return data


def assert_morphing(
    *,
    retort: Retort,
    tp: TypeHint,
    data: Any,
    loaded: Any,
    dumped: Any = Omitted(),
    json_schema: DumpedJSONSchema,
) -> None:
    produced_loaded = retort.load(data, tp)
    assert produced_loaded == loaded
    produced_dumped = retort.dump(produced_loaded, tp)
    expected_dumped = data if dumped == Omitted() else dumped
    assert produced_dumped == expected_dumped

    input_json_schema = generate_json_schema(retort, tp, direction=Direction.INPUT)
    output_json_schema = generate_json_schema(retort, tp, direction=Direction.OUTPUT)
    _validate_json_schema(input_json_schema)
    _validate_json_schema(output_json_schema)

    expected_input_json_schema = _resolve_json_schema(json_schema, Direction.INPUT)
    expected_output_json_schema = _resolve_json_schema(json_schema, Direction.OUTPUT)
    assert input_json_schema == expected_input_json_schema
    assert output_json_schema == expected_output_json_schema

    _validate_by_json_schema(data, input_json_schema)
    _validate_by_json_schema(produced_dumped, output_json_schema)
