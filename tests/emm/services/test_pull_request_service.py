"""Unit tests for pull_request_service.py."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from shrub.v3.evg_project import EvgModule

import emm.services.pull_request_service as under_test
from emm.services.evg_service import EvgService
from emm.services.git_service import GitService
from emm.services.github_service import GithubService
from emm.services.modules_service import ModulesService


@pytest.fixture()
def git_service():
    git_service = MagicMock(spec_set=GitService)
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
        name=f"module {i}", directory=Path(f"prefix/{i}"), target_branch=f"branch_{i}"
    )


def build_mock_pull_request(i: int) -> under_test.PullRequest:
    return under_test.PullRequest(name=f"PR Name {i}", link=f"http://link.to.pr/{i}")


class TestCollectRepositories:
    def test_base_repository_should_be_included(
        self,
        pull_request_service: under_test.PullRequestService,
        modules_service: ModulesService,
        evg_service: EvgService,
    ):
        modules_service.get_all_modules.return_value = {}

        repo_list = pull_request_service.collect_repositories()

        assert len(repo_list) == 1
        repo = repo_list[0]
        assert repo.name == under_test.BASE_REPO
        assert repo.directory is None
        assert repo.target_branch == evg_service.get_project_branch.return_value

    def test_module_repositories_should_be_included(
        self,
        pull_request_service: under_test.PullRequestService,
        modules_service: ModulesService,
        evg_service: EvgService,
    ):
        n_modules = 3
        modules_service.get_all_modules.return_value = {
            f"module {i}": EvgModule(
                name=f"module {i}", repo=f"repo {i}", branch=f"branch_{i}", prefix=f"prefix/{i}"
            )
            for i in range(n_modules)
        }

        repo_list = pull_request_service.collect_repositories()

        assert len(repo_list) == n_modules + 1  # +1 for the base repository.
        for i in range(n_modules):
            assert build_mock_repository(i) in repo_list


class TestCreatePullRequest:
    def test_pull_request_should_be_orchestrated(
        self,
        pull_request_service: under_test.PullRequestService,
        modules_service: ModulesService,
        git_service: GitService,
        github_service: GithubService,
    ):
        n_modules = 5
        modules_service.get_all_modules.return_value = {
            f"module {i}": EvgModule(
                name=f"module {i}", repo=f"repo {i}", branch=f"branch_{i}", prefix=f"prefix/{i}"
            )
            for i in range(n_modules)
        }
        git_service.check_changes.side_effect = [True, False, True, False, True, False]

        pr_links = pull_request_service.create_pull_request(None, None)

        assert len(pr_links) == 3
        assert github_service.pull_request.call_count == 3
        assert github_service.pr_comment.call_count == 3


class TestPushChangesToOrigin:
    def test_all_repositories_should_have_their_changes_pushed(
        self, pull_request_service: under_test.PullRequestService, git_service: GitService
    ):
        n_repos = 4
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]

        pull_request_service.push_changes_to_origin(changed_repos)

        assert git_service.push_branch_to_remote.call_count == n_repos


class TestCreatePrs:
    def test_prs_should_be_created_for_all_repos(
        self, pull_request_service: under_test.PullRequestService, github_service: GithubService
    ):
        n_repos = 3
        changed_repos = [build_mock_repository(i) for i in range(n_repos)]

        pr_links = pull_request_service.create_prs(changed_repos, ["arguments", "to", "gh"])

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


class TestCreatePrArguments:
    @pytest.mark.parametrize(
        "title,body,arguments",
        [
            (None, None, ["--fill"]),
            ("my title", None, ["--title", "my title", "--body", "''"]),
            ("my title", "my body", ["--title", "my title", "--body", "my body"]),
        ],
    )
    def test_arguments_should_work_correctly(
        self, title, body, arguments, pull_request_service: under_test.PullRequestService
    ):
        assert pull_request_service.create_pr_arguments(title, body) == arguments


class TestRepoHasChanges:
    def test_repo_with_changes_should_return_true(
        self, pull_request_service: under_test.PullRequestService, git_service: GitService
    ):
        git_service.check_changes.return_value = True
        mock_repository = build_mock_repository(3)

        assert pull_request_service.repo_has_changes(mock_repository)

        git_service.check_changes.assert_called_with(
            mock_repository.target_branch, mock_repository.directory
        )

    def test_repo_without_changes_should_return_true(
        self, pull_request_service: under_test.PullRequestService, git_service: GitService
    ):
        git_service.check_changes.return_value = False
        mock_repository = build_mock_repository(3)

        assert not pull_request_service.repo_has_changes(mock_repository)

        git_service.check_changes.assert_called_with(
            mock_repository.target_branch, mock_repository.directory
        )
