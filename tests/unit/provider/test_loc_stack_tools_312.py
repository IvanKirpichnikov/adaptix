

import pytest

from adaptix._internal.provider.loc_stack_tools import format_type

type MyIntAlias = int
type MyGenericAlias[T] = list[T]


@pytest.mark.parametrize(
    ["tp", "output", "uri_output"],
    [
        (MyIntAlias, "MyIntAlias", "MyIntAlias"),
        (MyGenericAlias, "MyGenericAlias", "MyGenericAlias"),
        (MyGenericAlias[int], "MyGenericAlias[int]", "MyGenericAlias_int"),
        (MyGenericAlias[str], "MyGenericAlias[str]", "MyGenericAlias_str"),
        (MyGenericAlias[MyGenericAlias[int]], "MyGenericAlias[MyGenericAlias[int]]", "MyGenericAlias_MyGenericAlias_int"),
    ],
)
def test_format_type(tp, output, uri_output):
    assert format_type(tp, brackets=False) == output
    assert format_type(tp, brackets=False, uri_faced=True) == uri_output
