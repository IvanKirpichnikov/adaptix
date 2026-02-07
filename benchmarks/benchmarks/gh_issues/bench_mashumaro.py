from dataclasses import dataclass
from datetime import datetime
from typing import List

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

from benchmarks.gh_issues.common import (
    AuthorAssociation,
    IssueState,
    StateReason,
    create_dumped_response,
    create_response,
)
from benchmarks.pybench.bench_api import benchmark_plan


@dataclass
class SimpleUser(DataClassDictMixin):
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

    class Config:
        omit_default = True


@dataclass
class Label(DataClassDictMixin):
    id: int
    node_id: str
    url: str
    name: str
    description: str | None
    color: str
    default: bool


@dataclass
class Reactions(DataClassDictMixin):
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

    class Config(BaseConfig):
        aliases = {
            "plus_one": "+1",
            "minus_one": "-1",
        }
        serialize_by_alias = True


@dataclass
class PullRequest(DataClassDictMixin):
    diff_url: str | None
    html_url: str | None
    patch_url: str | None
    url: str | None
    merged_at: datetime | None = None

    class Config(BaseConfig):
        omit_default = True


@dataclass
class Issue(DataClassDictMixin):
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

    class Config(BaseConfig):
        omit_default = True


@dataclass
class GetRepoIssuesResponse(DataClassDictMixin):
    data: List[Issue]


@dataclass
class SimpleUserLC(DataClassDictMixin):
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

    class Config:
        omit_default = True
        lazy_compilation = True


@dataclass
class LabelLC(DataClassDictMixin):
    id: int
    node_id: str
    url: str
    name: str
    description: str | None
    color: str
    default: bool

    class Config:
        lazy_compilation = True


@dataclass
class ReactionsLC(DataClassDictMixin):
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

    class Config(BaseConfig):
        aliases = {
            "plus_one": "+1",
            "minus_one": "-1",
        }
        serialize_by_alias = True
        lazy_compilation = True


@dataclass
class PullRequestLC(DataClassDictMixin):
    diff_url: str | None
    html_url: str | None
    patch_url: str | None
    url: str | None
    merged_at: datetime | None = None

    class Config:
        omit_default = True
        lazy_compilation = True


@dataclass
class IssueLC(DataClassDictMixin):
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
    user: SimpleUserLC | None
    labels: List[LabelLC]
    assignee: SimpleUserLC | None
    assignees: List[SimpleUserLC] | None
    locked: bool
    active_lock_reason: str | None
    comments: int
    closed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    author_association: AuthorAssociation
    reactions: ReactionsLC | None = None
    pull_request: PullRequestLC | None = None
    body_html: str | None = None
    body_text: str | None = None
    timeline_url: str | None = None
    body: str | None = None

    class Config:
        omit_default = True
        lazy_compilation = True


@dataclass
class GetRepoIssuesResponseLC(DataClassDictMixin):
    data: List[IssueLC]

    class Config:
        lazy_compilation = True


def test_loading():
    assert (
        GetRepoIssuesResponse.from_dict(create_dumped_response())
        ==
        create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    )
    assert (
        GetRepoIssuesResponseLC.from_dict(create_dumped_response())
        ==
        create_response(GetRepoIssuesResponseLC, IssueLC, ReactionsLC, PullRequestLC, LabelLC, SimpleUserLC)
    )


def test_dumping():
    assert (
        create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser).to_dict()
        ==
        create_dumped_response()
    )
    assert (
        create_response(GetRepoIssuesResponseLC, IssueLC, ReactionsLC, PullRequestLC, LabelLC, SimpleUserLC).to_dict()
        ==
        create_dumped_response()
    )


def bench_loading(lazy_compilation: bool):
    data = create_dumped_response()
    if lazy_compilation:
        GetRepoIssuesResponseLC.from_dict(data)
    loader = GetRepoIssuesResponseLC.from_dict if lazy_compilation else GetRepoIssuesResponse.from_dict
    return benchmark_plan(loader, data)


def bench_dumping(lazy_compilation: bool):
    if lazy_compilation:
        data = create_response(GetRepoIssuesResponseLC, IssueLC, ReactionsLC, PullRequestLC, LabelLC, SimpleUserLC)
        data.to_dict()
    else:
        data = create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    return benchmark_plan(data.to_dict)
