"""Unit tests for github_service.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import emm.services.github_service as under_test

NAMESPACE = "emm.services.github_service"


def ns(local_path: str) -> str:
    return f"{NAMESPACE}.{local_path}"


@pytest.fixture()
def mock_github_cli():
    github_mock = MagicMock()
    github_mock.assert_gh_call = lambda args: github_mock.__getitem__.assert_any_call(args)
    return github_mock


@pytest.fixture()
def github_service(mock_github_cli) -> under_test.GithubService:
    github_service = under_test.GithubService()
    github_service.github = mock_github_cli
    return github_service


class TestPullRequest:
    @patch(ns("local"))
    def test_pull_request_with_correct_args_should_return_pr_url(
        self, local_mock, github_service, mock_github_cli
    ):
        mock_github_cli.__getitem__.return_value.return_value = "github.com/pull/123"
        pr_link = github_service.pull_request(["--title", "Test title", "--body", "Test Body"])

        mock_github_cli.assert_gh_call(
            ["pr", "create", "--title", "Test title", "--body", "Test Body"]
        )
        assert pr_link == "github.com/pull/123"

    @patch(ns("local"))
    def test_pr_comment_should_call_gh_commit(self, local_mock, github_service, mock_github_cli):
        github_service.pr_comment("github.com/pull/123", "module_repo: github/pull/234")

        mock_github_cli.assert_gh_call(
            ["pr", "comment", "github.com/pull/123", "--body", "module_repo: github/pull/234"]
        )

    @patch(ns("local"))
    def test_pr_comment_with_directory_should_switch_directory(
        self, local_mock, github_service, mock_github_cli
    ):
        path = Path("/path/to/repo").absolute()
        github_service.pr_comment(
            "github.com/pull/234", "base_repo: github/pull/123", directory=path
        )

        mock_github_cli.assert_gh_call(
            ["pr", "comment", "github.com/pull/234", "--body", "base_repo: github/pull/123"]
        )
        local_mock.cwd.assert_called_with(path)
