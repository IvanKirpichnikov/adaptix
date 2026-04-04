import itertools
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, TypeVar

P = TypeVar("P", bound="Parametrizer")


class Parametrizer:
    def __init__(self, *, product: Mapping[str, Iterable[Any]] | None = None) -> None:
        self._product: dict[str, Iterable[Any]] = {} if product is None else dict(product)

    def product(self: P, variants: Mapping[str, Iterable[Any]]) -> P:
        self._product.update(variants)
        return self

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for case_values in itertools.product(*self._product.values()):
            yield dict(zip(self._product.keys(), case_values, strict=False))


def bool_tag_spec(key: str, tag: str | None = None) -> Mapping[str, Mapping[Any, str | None]]:
    if tag is None:
        tag = key
    return {
        key: {
            False: None,
            True: tag,
        },
    }


def tags_from_case(spec: Mapping[str, Mapping[Any, str | None]], case: Mapping[str, Any]) -> Iterable[str]:
    for key, value in case.items():
        result = spec[key][value]
        if result is not None:
            yield result
