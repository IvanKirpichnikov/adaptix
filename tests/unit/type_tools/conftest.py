from typing import Union

import pytest
from tests_helpers import pretty_typehint_test_id

from .local_helpers import UnionOpMaker

pytest_make_parametrize_id = pretty_typehint_test_id


@pytest.fixture(params=[Union, UnionOpMaker()])
def make_union(request):
    return request.param
