from collections.abc import Iterable
from copy import copy, deepcopy
from dataclasses import fields, replace
from typing import Any, Callable, TypeVar

from ...provider.provider_wrapper import Chain
from ...utils import Omitted
from .definitions import JSONSchema

S = TypeVar("S", bound="JSONSchemaPatch")
Patcher = Callable[[JSONSchema], JSONSchema]


class JSONSchemaPatch:
    def __init__(self) -> None:
        self._patchers: list[Patcher] = []

    def _append_with_patcher(self: S, patcher: Callable[[JSONSchema], JSONSchema]) -> S:
        self_copy = copy(self)
        self_copy._patchers.append(patcher)
        return self_copy

    def mutate_copy(
        self: S,
        target: str,
        mutator: Callable[[Any], Any],
    ) -> S:
        """Creates patcher that received a copy of specified attribute

        :param target: Attribute of :class:`.JSONSchema` object
        :param mutator: Function mutating value of attribute. Return value if ignored
        """
        return self._append_with_patcher(
            self._create_mutator_patcher(target, mutator, copy),
        )

    def mutate_deepcopy(self: S, target: str, mutator: Callable[[Any], Any]) -> S:
        return self._append_with_patcher(
            self._create_mutator_patcher(target, mutator, deepcopy),
        )

    def _create_mutator_patcher(
        self,
        target: str,
        mutator: Callable[[Any], Any],
        copy_function: Callable[[Any], Any],
    ):
        def patcher(json_schema: JSONSchema) -> JSONSchema:
            value_copy = copy_function(getattr(json_schema, target))
            mutator(value_copy)
            return replace(json_schema, **{target: value_copy})

        return patcher

    def merge_with(self: S, json_schema: JSONSchema, chain: Chain = Chain.FIRST) -> S:
        def patcher(input_json_schema: JSONSchema) -> JSONSchema:
            if chain == Chain.FIRST:
                first = json_schema
                second = input_json_schema
            else:
                first = input_json_schema
                second = json_schema

            return replace(
                second,
                **{
                    field.name: getattr(first, field.name)
                    for field in fields(first)
                    if getattr(first, field.name) != Omitted()
                },
            )

        return self._append_with_patcher(patcher)

    def get_patchers(self) -> Iterable[Patcher]:
        return self._patchers
