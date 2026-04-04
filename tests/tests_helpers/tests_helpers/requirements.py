from functools import reduce

import pytest

from adaptix._internal.feature_requirement import HAS_PY_314, DistributionVersionRequirement, Requirement


def requires(requirement: Requirement):
    def wrapper(func):
        return pytest.mark.skipif(
            not requirement,
            reason=requirement.fail_reason,
        )(func)

    return wrapper


class FailedRequirement(Requirement):
    def __init__(self, fail_reason: str):
        self._fail_reason = fail_reason
        super().__init__()

    def _evaluate(self) -> bool:
        return False

    @property
    def fail_reason(self) -> str:
        return self._fail_reason


class AndRequirement(Requirement):
    def __init__(self, *requirements: Requirement):
        self._requirements = requirements
        super().__init__()

    def _evaluate(self) -> bool:
        return reduce(lambda a, b: bool(a) and bool(b), self._requirements)

    @property
    def fail_reason(self) -> str:
        return " AND ".join(requirement.fail_reason for requirement in self._requirements)


class NotRequirement(Requirement):
    def __init__(self, requirement: Requirement):
        self._requirement = requirement
        super().__init__()

    def _evaluate(self) -> bool:
        return not self._requirement

    @property
    def fail_reason(self) -> str:
        return f"NOT {self._requirement.fail_reason}"


ATTRS_WITH_ALIAS = DistributionVersionRequirement("attrs", "22.2.0")
BEFORE_PY_314 = NotRequirement(HAS_PY_314)
