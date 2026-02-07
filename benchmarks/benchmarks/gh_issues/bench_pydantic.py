from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from benchmarks.gh_issues.common import (
    AuthorAssociation,
    IssueState,
    StateReason,
    create_dumped_response,
    create_response,
)
from benchmarks.pybench.bench_api import benchmark_plan


class SimpleUser(BaseModel):
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


class Label(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    description: str | None
    color: str
    default: bool


class Reactions(BaseModel):
    url: str
    total_count: int
    plus_one: int = Field(alias="+1")
    minus_one: int = Field(alias="-1")
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int

    model_config = {
        "populate_by_name": True,
    }


class PullRequest(BaseModel):
    diff_url: str | None
    html_url: str | None
    patch_url: str | None
    url: str | None
    merged_at: datetime | None = None


class Issue(BaseModel):
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


class GetRepoIssuesResponse(BaseModel):
    data: List[Issue]


def test_loading():
    assert (
        GetRepoIssuesResponse.model_validate(create_dumped_response())
        ==
        create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    )


def test_dumping():
    assert (
        create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
        .model_dump(mode="json", by_alias=True, exclude_defaults=True)
        ==
        create_dumped_response()
    )


def bench_loading():
    data = create_dumped_response()
    return benchmark_plan(GetRepoIssuesResponse.model_validate, data)


def bench_dumping():
    data = create_response(GetRepoIssuesResponse, Issue, Reactions, PullRequest, Label, SimpleUser)
    return benchmark_plan(lambda: data.model_dump(mode="json", by_alias=True, exclude_defaults=True))
