from collections.abc import Mapping
from dataclasses import dataclass

from adaptix import NameStyle, Retort, loader, name_mapping

# [NOTE] This example shows how adaptix can be used to load configuration data.
# By default, the settings are optimized for parsing from untrusted sources, with maximum validation enabled.
# The strict_coercion=False option allows implicit type conversions,
# which can be very useful when parsing configuration files.


@dataclass
class Config:
    log_level: str

    db_url: str
    db_pool_size: int
    debug_mode: bool = False


_config_retort = Retort(
    strict_coercion=False,
    recipe=[
        name_mapping(name_style=NameStyle.UPPER_SNAKE),
        loader(bool, lambda x: x.lower() in ("yes", "true", "t", "1")),
    ],
)


def load_config(environ: Mapping[str, str]) -> Config:
    return _config_retort.load(environ, Config)

