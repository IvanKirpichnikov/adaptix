import collections
import typing
from typing import Annotated, Callable, Generic, List, Optional, TypeVar, Union

import pytest
from tests_helpers.misc import cond_list

from adaptix._internal.feature_requirement import HAS_PARAM_SPEC, HAS_TV_TUPLE, HAS_TYPE_UNION_OP
from adaptix._internal.type_tools.type_rendering import TypeHintRenderer

T = TypeVar("T")


class MyGeneric(Generic[T]):
    pass


class OuterClass:
    class InnerClass:
        pass


if HAS_PARAM_SPEC:
    P = typing.ParamSpec("P")

if HAS_TV_TUPLE:
    Tv = typing.TypeVarTuple("Tv")


@pytest.mark.parametrize(
    ["tp", "output", "uri_output"],
    [
        (list, "list", "list"),
        (List, "List", "List"),
        (int, "int", "int"),
        (list[int], "list[int]", "list_int"),
        (List[int], "List[int]", "List_int"),
        (Annotated[int, "zoo"], "Annotated[int, 'zoo']", "Annotated_int_'zoo'"),
        (MyGeneric, "MyGeneric", "MyGeneric"),
        (MyGeneric[int], "MyGeneric[int]", "MyGeneric_int"),
        (MyGeneric[list[int]], "MyGeneric[list[int]]", "MyGeneric_list_int"),
        (MyGeneric[MyGeneric[list[int]]], "MyGeneric[MyGeneric[list[int]]]", "MyGeneric_MyGeneric_list_int"),
        (Callable[[int], str], "Callable[[int], str]", "Callable_int_str"),
        (collections.abc.Callable[[int], str], "Callable[[int], str]", "Callable_int_str"),
        (Callable[..., str], "Callable[..., str]", "Callable_..._str"),
        (collections.abc.Callable[..., str], "Callable[..., str]", "Callable_..._str"),
        (Callable, "Callable", "Callable"),
        (collections.abc.Callable, "Callable", "Callable"),
        (Optional[int], "Optional[int]", "Optional_int"),
        (Optional[MyGeneric[int]], "Optional[MyGeneric[int]]", "Optional_MyGeneric_int"),
        (Optional[Annotated[int, "zoo"]], "Optional[Annotated[int, 'zoo']]", "Optional_Annotated_int_'zoo'"),
        (OuterClass.InnerClass, "OuterClass.InnerClass", "OuterClass.InnerClass"),
        (Union[str, int], "Union[str, int]", "Union_str_int"),
        (Union[str, None], "Optional[str]", "Optional_str"),
        (Union[None, str], "Optional[str]", "Optional_str"),
        *cond_list(
            HAS_TYPE_UNION_OP,
            lambda: [
                (str | int, "str | int", "str_or_int"),
                (str | None, "str | None", "str_or_None"),
                (None | str, "None | str", "None_or_str"),
                (str | str, "str", "str"),
            ],
        ),
        *cond_list(
            HAS_PARAM_SPEC,
            lambda: [
                (P, "P", "P"),
                (Callable[P, int], "Callable[P, int]", "Callable_P_int"),
                (collections.abc.Callable[P, int], "Callable[P, int]", "Callable_P_int"),
            ],
        ),
        *cond_list(
            HAS_TV_TUPLE,
            lambda: [
                (eval("list[*Tv]"), "list[*Tv]", "list_Tv"),  # noqa: S307
            ],
        ),
    ],
)
def test_render_type(tp, output, uri_output):
    assert TypeHintRenderer(uri_faced=False).render_type(tp) == output
    assert TypeHintRenderer(uri_faced=True).render_type(tp) == uri_output
