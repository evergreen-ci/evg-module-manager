"""Unit tests for pull_request_service.py."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import emm.services.pull_request_service as under_test
from emm.clients.evg_service import EvgService
from emm.clients.git_proxy import GitProxy
from emm.clients.github_service import GithubService
from emm.services.modules_service import ModulesService


@pytest.fixture()
def git_service():
    git_service = MagicMock(spec_set=GitProxy)
    return git_service


@pytest.fixture()
def github_service():
    github_service = MagicMock(spec_set=GithubService)
    return github_service


@pytest.fixture()
def modules_service():
    modules_service = MagicMock(spec_set=ModulesService)
    return modules_service


@pytest.fixture()
def evg_service():
    evg_service = MagicMock(spec_set=EvgService)
    return evg_service


@pytest.fixture()
def emm_options():
    emm_options = MagicMock(evg_project="my project")
    return emm_options


@pytest.fixture()
def pull_request_service(git_service, github_service, modules_service, evg_service, emm_options):
    pull_request_service = under_test.PullRequestService(
        git_service, github_service, modules_service, evg_service, emm_options
    )
    return pull_request_service


def build_mock_repository(i: int) -> under_test.Repository:
    return under_test.Repository(
        name=f"module {i}", directory=Path(f"prefix/{i}/module {i}"), target_branch=f"branch_{i}"
    )


def build_mock_pull_request(i: int) -> under_test.PullRequest:
    return under_test.PullRequest(name=f"PR Name {i}", link=f"http://link.to.pr/{i}")


def build_mock_pull_request_option(remote: str) -> under_test.PullRequestOption:
    return under_test.PullRequestOption(
        title="title", body="body", branch="branch", remote_url=remote
    )


class TestCreatePullRequest:
    def test_pull_request_should_be_orchestrated(
        self,
        pull_request_service: under_test.PullRequestService,
        modules_service: ModulesService,
        git_service: GitProxy,
        github_service: GithubService,
    ):
        n_modules = 5
        remote = "origin"
        modules_service.collect_repositories.return_value = [
            build_mock_repository(i) for i in range(n_modules)
        ]
        git_service.check_changes.side_effect = [True, False, True, False, True, False]

        pr_links = pull_request_service.create_pull_request(None, None, remote)

        assert len(pr_links) == 3
        assert github_service.pull_request.call_count == 3
        assert github_service.pr_comment.call_count == 3


class TestDetermineRemote:
    def test_all_repositories_should_have_their_own_remote(
        self, pull_request_service: under_test.PullRequestService, git_service: GitProxy
    ):
        n_repos = 4
        remote = "origin"
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]

        pull_request_service.determine_remote(remote, changed_repos)

        assert git_service.determine_remote.call_count == n_repos


class TestPushChangesToRemote:
    def test_all_repositories_should_have_their_changes_pushed(
        self, pull_request_service: under_test.PullRequestService, git_service: GitProxy
    ):
        n_repos = 4
        remote = "origin"
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]
        mock_remotes = [None, None, remote, remote]

        pull_request_service.push_changes_to_remote(mock_remotes, changed_repos)

        assert git_service.push_branch_to_remote.call_count == n_repos


class TestCreatePrs:
    def test_prs_should_be_created_for_all_repos(
        self, pull_request_service: under_test.PullRequestService, github_service: GithubService
    ):
        n_repos = 3
        remote = "origin"
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]
        pr_arguements = [
            build_mock_pull_request_option(remote).option_list() for i in range(n_repos)
        ]

        pr_links = pull_request_service.create_prs(changed_repos, pr_arguements)

        assert len(pr_links) == n_repos
        for repo in changed_repos:
            assert any(link.name == repo.name for link in pr_links.values())
        assert github_service.pull_request.call_count == n_repos


class TestAnnotatePrs:
    def test_nothing_should_be_annotated_if_only_one_pr(
        self, pull_request_service: under_test.PullRequestService, github_service: GithubService
    ):
        changed_repos = [build_mock_repository(0)]

        pull_request_service.annotate_prs(changed_repos, {})

        github_service.pr_comment.assert_not_called()

    def test_all_given_repos_should_be_annotated_if_more_than_one_pr(
        self, pull_request_service: under_test.PullRequestService, github_service: GithubService
    ):
        n_repos = 5
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]
        pr_links = {repo.name: build_mock_pull_request(i) for i, repo in enumerate(changed_repos)}

        pull_request_service.annotate_prs(changed_repos, pr_links)

        assert github_service.pr_comment.call_count == n_repos


class TestCreateComment:
    def test_comment_should_include_pr_links(
        self, pull_request_service: under_test.PullRequestService
    ):
        n_links = 5
        pr_links = [build_mock_pull_request(i) for i in range(n_links)]

        pr_comment = pull_request_service.create_comment(pr_links, "PR Name 3")

        for pr in pr_links:
            if pr.name == "PR Name 3":
                assert pr.name not in pr_comment
                assert pr.link not in pr_comment
            else:
                assert pr.name in pr_comment
                assert pr.link in pr_comment


class TestCombinePRArugments:
    @pytest.mark.parametrize(
        "title,body,remote,arguments",
        [
            (
                None,
                None,
                ["origin", "origin"],
                [
                    ["--title", "commit message", "--body", "''"],
                    ["--title", "commit message", "--body", "''"],
                ],
            ),
            (
                "my title",
                None,
                ["origin", "origin"],
                [["--title", "my title", "--body", "''"], ["--title", "my title", "--body", "''"]],
            ),
            (
                "my title",
                "my body",
                ["origin", "origin"],
                [
                    ["--title", "my title", "--body", "my body"],
                    ["--title", "my title", "--body", "my body"],
                ],
            ),
            (
                None,
                None,
                ["url", "origin"],
                [
                    [
                        "--title",
                        "commit message",
                        "--body",
                        "''",
                        "--head",
                        "branch",
                        "--repo",
                        "url",
                    ],
                    ["--title", "commit message", "--body", "''"],
                ],
            ),
            (
                None,
                None,
                ["url", "url"],
                [
                    [
                        "--title",
                        "commit message",
                        "--body",
                        "''",
                        "--head",
                        "branch",
                        "--repo",
                        "url",
                    ],
                    [
                        "--title",
                        "commit message",
                        "--body",
                        "''",
                        "--head",
                        "branch",
                        "--repo",
                        "url",
                    ],
                ],
            ),
            (
                None,
                "my body",
                ["url", "url"],
                [
                    [
                        "--title",
                        "commit message",
                        "--body",
                        "my body",
                        "--head",
                        "branch",
                        "--repo",
                        "url",
                    ],
                    [
                        "--title",
                        "commit message",
                        "--body",
                        "my body",
                        "--head",
                        "branch",
                        "--repo",
                        "url",
                    ],
                ],
            ),
        ],
    )
    def test_arguements_should_generate_corretly(
        self,
        title,
        body,
        remote,
        arguments,
        pull_request_service: under_test.PullRequestService,
        git_service: GitProxy,
    ):
        n_repos = 2
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]
        git_service.commit_message.return_value = "commit message"
        git_service.current_branch.return_value = "branch"

        assert (
            pull_request_service.combine_pr_arugments(title, body, remote, changed_repos)
            == arguments
        )


class TestRepoHasChanges:
    def test_repo_with_changes_should_return_true(
        self, pull_request_service: under_test.PullRequestService, git_service: GitProxy
    ):
        git_service.check_changes.return_value = True
        mock_repository = build_mock_repository(3)

        assert pull_request_service.repo_has_changes(mock_repository)

        git_service.check_changes.assert_called_with(
            mock_repository.target_branch, mock_repository.directory
        )

    def test_repo_without_changes_should_return_true(
        self, pull_request_service: under_test.PullRequestService, git_service: GitProxy
    ):
        git_service.check_changes.return_value = False
        mock_repository = build_mock_repository(3)

        assert not pull_request_service.repo_has_changes(mock_repository)

        git_service.check_changes.assert_called_with(
            mock_repository.target_branch, mock_repository.directory
        )
