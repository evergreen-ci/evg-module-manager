"""Unit tests for git_service.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import emm.services.git_service as under_test

NAMESPACE = "emm.services.git_service"


def ns(local_path: str) -> str:
    return f"{NAMESPACE}.{local_path}"


def make_fake_path() -> Path:
    return Path("./fake/path")


@pytest.fixture()
def mock_git():
    git_mock = MagicMock()
    git_mock.assert_git_call = lambda args: git_mock.__getitem__.assert_any_call(args)
    return git_mock


@pytest.fixture()
def git_service(mock_git) -> under_test.GitService:
    git_service = under_test.GitService(mock_git)
    return git_service


class TestPerformGitAction:
    @pytest.mark.parametrize(
        "action,git_cmd",
        [
            (under_test.GitAction.CHECKOUT, "checkout"),
            (under_test.GitAction.MERGE, "merge"),
            (under_test.GitAction.REBASE, "rebase"),
        ],
    )
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_action_with_revision_should_call_git_action(
        self, path_mock, local_mock, git_service, mock_git, action, git_cmd
    ):
        git_service.perform_git_action(action, "abc123")

        mock_git.assert_git_call([git_cmd, "abc123"])

    @pytest.mark.parametrize(
        "action,git_cmd",
        [
            (under_test.GitAction.CHECKOUT, "checkout"),
            (under_test.GitAction.MERGE, "merge"),
            (under_test.GitAction.REBASE, "rebase"),
        ],
    )
    @patch(ns("local"))
    def test_action_with_revision_and_dir_should_switch_directories(
        self, local_mock, git_service, mock_git, action, git_cmd
    ):
        path = Path("/a/absolute/path").absolute()
        git_service.perform_git_action(action, "abc123", directory=path)

        mock_git.assert_git_call([git_cmd, "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestClone:
    @patch(ns("local"))
    def test_clone_should_call_git_clone(self, local_mock, git_service, mock_git):
        path = Path("/path/to/modules").absolute()
        git_service.clone("module_name", "repo", path, branch=None)

        mock_git.assert_git_call(["clone", "repo", "module_name"])
        local_mock.cwd.assert_called_with(path)

    @patch(ns("local"))
    def test_clone_with_branch_should_call_git_clone_with_branch(
        self, local_mock, git_service, mock_git
    ):
        path = Path("/path/to/modules").absolute()
        git_service.clone("module_name", "repo", path, branch="main")

        mock_git.assert_git_call(["clone", "--branch", "main", "repo", "module_name"])
        local_mock.cwd.assert_called_with(path)


class TestFetch:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_fetch_should_call_git_clone(self, path_mock, local_mock, git_service, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_service.fetch()

        mock_git.assert_git_call(["fetch", "origin"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_fetch_with_directory_should_call_git_fetch_from_dir(
        self, local_mock, git_service, mock_git
    ):
        path = Path("/path/to/modules").absolute()
        git_service.fetch(directory=path)

        mock_git.assert_git_call(["fetch", "origin"])
        local_mock.cwd.assert_called_with(path)


class TestCheckout:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_checkout_should_call_git_checkout(self, path_mock, local_mock, git_service, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_service.checkout("abc123", directory=None, branch_name=None)

        mock_git.assert_git_call(["checkout", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_checkout_with_branch_should_call_git_checkout_with_branch(
        self, path_mock, local_mock, git_service, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_service.checkout("abc123", directory=None, branch_name="main")

        mock_git.assert_git_call(["checkout", "-b", "main", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_checkout_with_directory_should_call_git_checkout_from_directory(
        self, local_mock, git_service, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_service.checkout("abc123", directory=path, branch_name=None)

        mock_git.assert_git_call(["checkout", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestRebase:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_rebase_with_no_directory_should_call_git_rebase(
        self, path_mock, local_mock, git_service, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_service.rebase("abc123")

        mock_git.assert_git_call(["rebase", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_rebase_with_directory_should_switch_directories(
        self, local_mock, git_service, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_service.rebase("abc123", directory=path)

        mock_git.assert_git_call(["rebase", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestMerge:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_merge_with_no_directory_should_call_git_rebase(
        self, path_mock, local_mock, git_service, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_service.merge("abc123")

        mock_git.assert_git_call(["merge", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_merge_with_directory_should_switch_directories(
        self, local_mock, git_service, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_service.merge("abc123", directory=path)

        mock_git.assert_git_call(["merge", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestCurrentCommit:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_current_commit_with_no_directory_should_return_git_hash(
        self, path_mock, local_Mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        git_commit = git_service.current_commit()

        mock_git.assert_git_call(["rev-parse", "HEAD"])
        assert git_commit == "abc123"

    @patch(ns("local"))
    def test_current_commit_with_directory_should_switch_directories(
        self, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        path = Path("/path/to/repo").absolute()
        git_commit = git_service.current_commit(directory=path)

        mock_git.assert_git_call(["rev-parse", "HEAD"])
        assert git_commit == "abc123"
        local_mock.cwd.assert_called_with(path)


class TestMergeBase:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_merge_base_with_no_directory_should_return_merge_base(
        self, path_mock, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        git_commit = git_service.merge_base("commit_1", "HEAD")

        mock_git.assert_git_call(["merge-base", "commit_1", "HEAD"])
        assert git_commit == "abc123"

    @patch(ns("local"))
    def test_merge_base_with_directory_should_switch_directories(
        self, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        path = Path("/path/to/repo").absolute()
        git_commit = git_service.merge_base("commit_1", "HEAD", directory=path)

        mock_git.assert_git_call(["merge-base", "commit_1", "HEAD"])
        assert git_commit == "abc123"
        local_mock.cwd.assert_called_with(path)


class TestGetBaseName:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_get_base_name_should_return_default_basename(
        self, path_mock, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "origin/master"

        basename = git_service.get_mergebase_branch_name()
        mock_git.assert_git_call(["symbolic-ref", "refs/remotes/origin/HEAD"])
        assert basename == "master"


class TestPushBranchToRemote:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_check_changes_should_return_changes(
        self, path_mock, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "diff --git aaa bbb\n"

        diff = git_service.check_changes("master")

        mock_git.assert_git_call(["diff", "master..HEAD"])
        assert diff is True

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_current_branch_should_return_branch_name(
        self, path_mock, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "branch\n"

        diff = git_service.current_branch()

        mock_git.assert_git_call(["rev-parse", "--abbrev-ref", "HEAD"])
        assert diff == "branch"

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_branch_exist_on_remote_should_return_remote_branch(
        self, path_mock, local_mock, git_service, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "origin/branch\n"

        remote_branch = git_service.current_branch_exist_on_remote("branch")

        mock_git.assert_git_call(["branch", "--remotes", "--contains", "branch"])
        assert remote_branch == "origin/branch"


class TestDetermineDirectory:
    @patch(ns("local"))
    def test_directory_of_none_should_return_cwd(self, local_mock, git_service):
        local_mock.cwd = "fake"
        assert git_service._determine_directory(None) == Path(local_mock.cwd)

    @patch(ns("local"))
    def test_relative_directory_should_return_full_path(self, local_mock, git_service):
        directory = Path("a/relative/path")
        local_mock.cwd = "fake"
        assert git_service._determine_directory(directory) == Path(local_mock.cwd / directory)

    @patch(ns("local"))
    def test_absolute_directory_should_return_directory(self, local_mock, git_service):
        directory = Path("/a/absolute/path").absolute()
        assert git_service._determine_directory(directory) == directory
