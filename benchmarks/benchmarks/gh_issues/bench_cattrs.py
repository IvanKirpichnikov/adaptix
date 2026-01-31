from datetime import datetime
from typing import List

from attr import define
from cattr import Converter
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override

from benchmarks.gh_issues.common import (
    AuthorAssociation,
    IssueState,
    StateReason,
    create_dumped_response,
    create_response,
)
from benchmarks.pybench.bench_api import benchmark_plan


@define
class SimpleUser:
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str | None
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: str | None = None
    email: str | None = None
    starred_at: datetime | None = None


@define
class Label:
    id: int
    node_id: str
    url: str
    name: str
    description: str | None
    color: str
    default: bool


@define
class Reactions:
    url: str
    total_count: int
    plus_one: int
    minus_one: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


@define
class PullRequest:
    diff_url: str | None
    html_url: str | None
    patch_url: str | None
    url: str | None
    merged_at: datetime | None = None


@define
class Issue:
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    number: int
    state: IssueState
    state_reason: StateReason | None
    title: str
    user: SimpleUser | None
    labels: List[Label]
    assignee: SimpleUser | None
    assignees: List[SimpleUser] | None
    locked: bool
    active_lock_reason: str | None
    comments: int
    closed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    author_association: AuthorAssociation
    reactions: Reactions | None = None
    pull_request: PullRequest | None = None
    body_html: str | None = None
    body_text: str | None = None
    timeline_url: str | None = None
    body: str | None = None


@define
class GetRepoIssuesResponse:
    data: List[Issue]


converter = Converter(omit_if_default=True)
converter.register_structure_hook(
    datetime,
    lambda v, tp: datetime.fromisoformat(v),
)
converter.register_unstructure_hook(
    datetime,
    datetime.isoformat,
)
converter.register_unstructure_hook(
    Reactions,
    make_dict_unstructure_fn(
        Reactions,
        converter,
        plus_one=override(rename="+1"),
        minus_one=override(rename="-1"),
    ),
)
converter.register_structure_hook(
    Reactions,
    make_dict_structure_fn(
        Reactions,
        converter,
        plus_one=override(rename="+1"),
        minus_one=override(rename="-1"),
    ),
)


def test_loading():
    assert (
        converter.structure(create_dumped_response(), GetRepoIssuesResponse)
        ==
        create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    )


def test_dumping():
    assert (
        converter.unstructure(create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser))
        ==
        create_dumped_response()
    )


def bench_loading(detailed_validation: bool):
    bench_converter = converter.copy(detailed_validation=detailed_validation)

    data = create_dumped_response()
    return benchmark_plan(bench_converter.structure, data, GetRepoIssuesResponse)


def bench_dumping(detailed_validation: bool):
    bench_converter = converter.copy(detailed_validation=detailed_validation)

    data = create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    return benchmark_plan(bench_converter.unstructure, data, GetRepoIssuesResponse)
