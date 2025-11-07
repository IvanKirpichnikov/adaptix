from tests_helpers import cond_list
from tests_helpers.misc import AndRequirement

from adaptix._internal.feature_requirement import DistributionRequirement

HAS_FASTAPI = DistributionRequirement("fastapi")
HAS_GREENLET = DistributionRequirement("greenlet")

collect_ignore_glob = [
    *cond_list(not AndRequirement(HAS_FASTAPI, HAS_GREENLET), ["*"]),
]
