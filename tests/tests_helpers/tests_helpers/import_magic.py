import importlib.util
import inspect
import runpy
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Generator, Optional
from uuid import uuid4


def load_namespace(
    file_name: str,
    ns_id: Optional[str] = None,
    vars: Optional[dict[str, Any]] = None,  # noqa: A002
    run_name: Optional[str] = None,
    stack_offset: int = 1,
) -> SimpleNamespace:
    caller_file = inspect.getfile(inspect.stack()[stack_offset].frame)
    ns_dict = runpy.run_path(
        str(Path(caller_file).with_name(file_name)),
        init_globals=vars,
        run_name=run_name,
    )
    if ns_id is not None:
        ns_dict["__ns_id__"] = ns_id
    return SimpleNamespace(**ns_dict)


@contextmanager
def temp_module(module: ModuleType):
    sys.modules[module.__name__] = module
    try:
        yield
    finally:
        sys.modules.pop(module.__name__, None)


@contextmanager
def load_namespace_keeping_module(
    file_name: str,
    ns_id: Optional[str] = None,
    vars: Optional[dict[str, Any]] = None,  # noqa: A002
    run_name: Optional[str] = None,
) -> Generator[SimpleNamespace, None, None]:
    if run_name is None:
        run_name = "temp_module_" + uuid4().hex
    ns = load_namespace(file_name=file_name, ns_id=ns_id, vars=vars, run_name=run_name, stack_offset=3)
    module = ModuleType(run_name)
    for attr, value in ns.__dict__.items():
        setattr(module, attr, value)

    with temp_module(module):
        yield ns


def import_local_module(file_path: Path, name: Optional[str] = None) -> ModuleType:
    if name is None:
        name = file_path.stem

    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
