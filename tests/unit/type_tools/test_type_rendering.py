import collections
import typing
from typing import Annotated, Callable, Generic, List, Optional, ParamSpec, TypeVar, Union

import pytest
from tests_helpers import cond_list

from adaptix import TypeHint
from adaptix._internal.feature_requirement import HAS_TV_TUPLE, HAS_UNION_TYPE_MERGED
from adaptix._internal.type_tools.type_rendering import TypeHintRenderer

T = TypeVar("T")


class MyGeneric(Generic[T]):
    pass


class OuterClass:
    class InnerClass:
        pass


P = ParamSpec("P")

if HAS_TV_TUPLE:
    Tv = typing.TypeVarTuple("Tv")


def case(tp: TypeHint, output: str, uri_output: str, *, py314: Optional[tuple[str, str]] = None):
    if HAS_UNION_TYPE_MERGED and py314 is not None:
        return pytest.param(tp, py314[0], py314[1], id=output)
    return pytest.param(tp, output, uri_output, id=output)


@pytest.mark.parametrize(
    ["tp", "output", "uri_output"],
    [
        case(list, "list", "list"),
        case(List, "List", "List"),
        case(int, "int", "int"),
        case(list[int], "list[int]", "list_int"),
        case(List[int], "List[int]", "List_int"),
        case(Annotated[int, "zoo"], "Annotated[int, 'zoo']", "Annotated_int_'zoo'"),
        case(MyGeneric, "MyGeneric", "MyGeneric"),
        case(MyGeneric[int], "MyGeneric[int]", "MyGeneric_int"),
        case(MyGeneric[list[int]], "MyGeneric[list[int]]", "MyGeneric_list_int"),
        case(MyGeneric[MyGeneric[list[int]]], "MyGeneric[MyGeneric[list[int]]]", "MyGeneric_MyGeneric_list_int"),
        case(Callable[[int], str], "Callable[[int], str]", "Callable_int_str"),
        case(collections.abc.Callable[[int], str], "Callable[[int], str]", "Callable_int_str"),
        case(Callable[..., str], "Callable[..., str]", "Callable_..._str"),
        case(collections.abc.Callable[..., str], "Callable[..., str]", "Callable_..._str"),
        case(Callable, "Callable", "Callable"),
        case(collections.abc.Callable, "Callable", "Callable"),
        case(
            Optional[int],
            "Optional[int]", "Optional_int",
            py314=("int | None", "int_or_None"),
        ),
        case(
            Optional[MyGeneric[int]],
            "Optional[MyGeneric[int]]", "Optional_MyGeneric_int",
            py314=("MyGeneric[int] | None", "MyGeneric_int_or_None"),
        ),
        case(
            Optional[Annotated[int, "zoo"]],
            "Optional[Annotated[int, 'zoo']]", "Optional_Annotated_int_'zoo'",
            py314=("Annotated[int, 'zoo'] | None", "Annotated_int_'zoo'_or_None"),
        ),
        case(OuterClass.InnerClass, "OuterClass.InnerClass", "OuterClass.InnerClass"),
        case(
            Union[str, int],
            "Union[str, int]", "Union_str_int",
            py314=("str | int", "str_or_int"),
        ),
        case(
            Union[str, None],
            "Optional[str]", "Optional_str",
            py314=("str | None", "str_or_None"),
        ),
        case(
            Union[None, str],
            "Optional[str]", "Optional_str",
            py314=("None | str", "None_or_str"),
        ),
        case(str | int, "str | int", "str_or_int"),
        case(str | None, "str | None", "str_or_None"),
        case(None | str, "None | str", "None_or_str"),
        case(str | str, "str", "str"),
        case(P, "P", "P"),
        case(Callable[P, int], "Callable[P, int]", "Callable_P_int"),
        case(collections.abc.Callable[P, int], "Callable[P, int]", "Callable_P_int"),
        *cond_list(
            HAS_TV_TUPLE,
            lambda: [
                case(eval("list[*Tv]"), "list[*Tv]", "list_Tv"),  # noqa: S307
            ],
        ),
    ],
)
def test_render_type(tp, output, uri_output):
    assert TypeHintRenderer(uri_faced=False).render_type(tp) == output
    assert TypeHintRenderer(uri_faced=True).render_type(tp) == uri_output
