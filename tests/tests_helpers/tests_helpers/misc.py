from collections.abc import Reversible, Sequence
from dataclasses import dataclass
from typing import TypeVar, Union

from adaptix import DebugTrail, Provider, Request, Retort
from adaptix._internal.morphing.model.basic_gen import CodeGenAccumulator
from adaptix._internal.provider.essential import Mediator, RequestHandlerRegisterRecord
from adaptix._internal.retort.operating_retort import OperatingRetort
from adaptix._internal.struct_trail import TrailElement, extend_trail, render_trail_as_note
from adaptix._internal.utils import add_note


@dataclass
class DebugCtx:
    accum: CodeGenAccumulator

    @property
    def source(self):
        return self.accum.list[-1][1].source

    @property
    def source_namespace(self):
        return self.accum.list[-1][1].namespace


@dataclass
class PlaceholderProvider(Provider):
    value: int

    def get_request_handlers(self) -> Sequence[RequestHandlerRegisterRecord]:
        return []


T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")


class ByTrailSelector:
    def __init__(self, debug_trail: DebugTrail):
        self.debug_trail = debug_trail

    def __call__(self, *, disable: T1, first: T2, all: T3) -> Union[T1, T2, T3]:  # noqa: A002
        if self.debug_trail == DebugTrail.DISABLE:
            return disable
        if self.debug_trail == DebugTrail.FIRST:
            return first
        if self.debug_trail == DebugTrail.ALL:
            return all
        raise ValueError


E = TypeVar("E", bound=Exception)


def with_notes(exc: E, *notes: Union[str, list[str]]) -> E:
    for note_or_list in notes:
        if isinstance(note_or_list, list):
            for note in note_or_list:
                add_note(exc, note)
        else:
            add_note(exc, note_or_list)
    return exc


def with_trail(exc: E, sub_trail: Reversible[TrailElement]) -> E:
    return render_trail_as_note(extend_trail(exc, sub_trail))


def with_cause(exc: E, cause: BaseException) -> E:
    exc.__cause__ = cause
    return exc


class StubRequest(Request):
    pass


_stub_retort = Retort()


def create_mediator(retort: OperatingRetort = _stub_retort) -> Mediator:
    return retort._create_mediator(StubRequest())
