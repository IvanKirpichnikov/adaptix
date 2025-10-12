import collections.abc
import types
import typing
from collections.abc import Iterable
from typing import Any, Callable, Union

from ..common import TypeHint
from ..feature_requirement import HAS_PARAM_SPEC, HAS_PY_310, HAS_TYPE_ALIAS_SYNTAX, HAS_TYPE_UNION_OP, HAS_UNPACK
from ..type_tools import get_generic_args, strip_alias
from ..type_tools.normalize_type import NoneType
from ..utils import pairs
from .loc_stack_filtering import LocStack
from .location import AnyLoc, FieldLoc, InputFuncFieldLoc, TypeHintLoc


class TypeFormatter:
    __slots__ = ("_uri_faced", )

    def __init__(self, *, uri_faced: bool):
        self._uri_faced = uri_faced

    def _join_format(self, sep: str, objs: Iterable[Any]) -> str:
        return sep.join(self.format_type(obj) for obj in objs)

    def _format_union(self, tp, origin, args) -> str:
        if len(args) == 2:  # noqa: PLR2004
            if args[0] is NoneType:
                args = [args[1]]
            elif args[1] is NoneType:
                args = [args[0]]

        return self._format_parametrized_generic(tp, origin, args)

    def _format_union_op(self, tp, origin, args) -> str:
        if self._uri_faced:
            return self._join_format("_or_", args)
        return self._join_format(" | ", args)

    def _format_unpack(self, tp, origin, args) -> str:
        if self._uri_faced:
            return self.format_type(args[0])
        return f"*{self.format_type(args[0])}"

    def _get_repr_base(self, tp, origin) -> str:
        if HAS_TYPE_ALIAS_SYNTAX and isinstance(origin, typing.TypeAliasType):  # type: ignore[attr-defined]
            return tp.__name__
        if not HAS_PY_310:
            return self._get_repr_without_module(tp, origin).partition("[")[0]
        return tp.__qualname__

    def _format_callable(self, tp, origin, args) -> str:
        if HAS_PARAM_SPEC and isinstance(args[0], typing.ParamSpec):
            return self._format_parametrized_generic(tp, origin, args)
        base = self._get_repr_base(tp, origin)
        if args[0] == Ellipsis:
            if self._uri_faced:
                return f"{base}_..._{self.format_type(args[1])}"
            return f"{base}[..., {self.format_type(args[1])}]"
        if self._uri_faced:
            return f"{base}_{self._join_format('_', [*args[0], args[1]])}"
        return f"{base}[[{self._join_format(', ', args[0])}], {self.format_type(args[1])}]"

    def _format_parametrized_generic(self, tp, origin, args) -> str:
        base = self._get_repr_base(tp, origin)
        if self._uri_faced:
            return f"{base}_{self._join_format('_', args)}"
        return f"{base}[{self._join_format(', ', args)}]"

    def format_type(self, obj) -> str:  # noqa: PLR0911
        origin = strip_alias(obj)
        args = get_generic_args(obj)

        if obj == NoneType:
            return "None"
        if origin == Union:
            return self._format_union(obj, origin, args)
        if HAS_PARAM_SPEC and isinstance(obj, typing.ParamSpec):
            return obj.__name__
        if HAS_UNPACK and origin == typing.Unpack:
            return self._format_unpack(obj, origin, args)
        if HAS_TYPE_UNION_OP and origin == types.UnionType:
            return self._format_union_op(obj, origin, args)
        if args:
            if origin == collections.abc.Callable:
                return self._format_callable(obj, origin, args)
            return self._format_parametrized_generic(obj, origin, args)
        if isinstance(obj, type):
            return obj.__qualname__
        return self._get_repr_without_module(obj, origin)

    def _get_repr_without_module(self, obj, origin) -> str:
        module = (
            "typing"
            if not HAS_PY_310 and origin == typing.Annotated else
            getattr(obj, "__module__", None)
        )
        try:
            obj_repr = repr(obj)
        except Exception as ex:
            obj_repr = f"<repr failed: {type(ex)}>"
        if module is not None and obj_repr.startswith(module + "."):
            return obj_repr[len(module) + 1:]
        return obj_repr


def format_type(tp: TypeHint, *, brackets: bool = True, uri_faced=False) -> str:
    fmt = TypeFormatter(uri_faced=uri_faced).format_type(tp)
    return f"‹{fmt}›" if brackets else fmt


def get_callable_name(func: Callable) -> str:
    return getattr(func, "__qualname__", None) or repr(func)


def format_loc_stack(loc_stack: LocStack[AnyLoc], *, always_wrap_with_brackets: bool = False) -> str:
    fmt_tp = format_type(loc_stack.last.type, brackets=False)

    try:
        field_loc = loc_stack.last.cast(FieldLoc)
    except TypeError:
        return f"‹{fmt_tp}›" if always_wrap_with_brackets else fmt_tp
    else:
        fmt_field = f"{field_loc.field_id}: {fmt_tp}"

    if loc_stack.last.is_castable(InputFuncFieldLoc):
        return f"parameter ‹{fmt_field}›"

    if len(loc_stack) >= 2:  # noqa: PLR2004
        src_owner = format_type(loc_stack[-2].type, brackets=False)
        return f"‹{src_owner}.{fmt_field}›"

    return f"‹{fmt_field}›"


def find_owner_with_field(stack: LocStack) -> tuple[TypeHintLoc, FieldLoc]:
    for next_loc, prev_loc in pairs(reversed(stack)):
        if next_loc.is_castable(FieldLoc):
            return prev_loc, next_loc
    raise ValueError
