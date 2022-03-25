"""Unit tests for git_proxy.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click import UsageError

import emm.clients.git_proxy as under_test

# TODO: Find a better way to handle the Path module when testing 3.7
# We shouldn't have to mock the entire Path module when testing

NAMESPACE = "emm.clients.git_proxy"


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
def git_proxy(mock_git) -> under_test.GitProxy:
    git_proxy = under_test.GitProxy(mock_git)
    return git_proxy


class TestClone:
    @patch(ns("local"))
    def test_clone_should_call_git_clone(self, local_mock, git_proxy, mock_git):
        path = Path("/path/to/modules").absolute()
        git_proxy.clone("module_name", "repo", path, branch=None)

        mock_git.assert_git_call(["clone", "repo", "module_name"])
        local_mock.cwd.assert_called_with(path)

    @patch(ns("local"))
    def test_clone_with_branch_should_call_git_clone_with_branch(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/modules").absolute()
        git_proxy.clone("module_name", "repo", path, branch="main")

        mock_git.assert_git_call(["clone", "--branch", "main", "repo", "module_name"])
        local_mock.cwd.assert_called_with(path)


class TestFetch:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_fetch_should_call_git_fetch(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.fetch()

        mock_git.assert_git_call(["fetch", "origin"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_fetch_with_directory_should_call_git_fetch_from_dir(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/modules").absolute()
        git_proxy.fetch(directory=path)

        mock_git.assert_git_call(["fetch", "origin"])
        local_mock.cwd.assert_called_with(path)


class TestPull:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_pull_should_call_git_pull(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.pull()

        mock_git.assert_git_call(["pull"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_pull_with_directory_should_call_git_pull_from_directory(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/modules").absolute()
        git_proxy.pull(directory=path)

        mock_git.assert_git_call(["pull"])
        local_mock.cwd.assert_called_with(path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_rebase_option_should_call_git_pull_with_rebase(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.pull(rebase=True)

        mock_git.assert_git_call(["pull", "--rebase"])
        local_mock.cwd.assert_called_with(test_path)


class TestCheckout:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_checkout_should_call_git_checkout(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.checkout("abc123", directory=None, branch_name=None)

        mock_git.assert_git_call(["checkout", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_checkout_with_branch_should_call_git_checkout_with_branch(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.checkout("abc123", directory=None, branch_name="main")

        mock_git.assert_git_call(["checkout", "-b", "main", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_checkout_with_directory_should_call_git_checkout_from_directory(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_proxy.checkout("abc123", directory=path, branch_name=None)

        mock_git.assert_git_call(["checkout", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestBranch:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_branch_should_call_git_branch(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.branch(directory=None)

        mock_git.assert_git_call(["branch"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_branch_with_delete_should_call_git_branch_delete(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.branch("abc123", directory=None)

        mock_git.assert_git_call(["branch", "-D", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_branch_with_directory_should_call_git_branch_from_directory(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_proxy.branch(directory=path)

        mock_git.assert_git_call(["branch"])
        local_mock.cwd.assert_called_with(path)


class TestStatus:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_status_should_call_git_status(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.status()

        mock_git.assert_git_call(["status"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_status_with_short_should_call_git_status_short(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.status(short=True)

        mock_git.assert_git_call(["status", "--short"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_status_with_directory_should_call_git_status_from_directory(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_proxy.status(directory=path)

        mock_git.assert_git_call(["status"])
        local_mock.cwd.assert_called_with(path)


class TestLsFiles:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_ls_files_should_call_git_ls_files(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.ls_files(["."])

        mock_git.assert_git_call(["ls-files", "."])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_ls_files_with_options_should_call_git_ls_files_with_options(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.ls_files(["."], cached=True, others=True, ignore_file="ignore-me")

        mock_git.assert_git_call(
            ["ls-files", "--cached", "--others", "--exclude-from=ignore-me", "."]
        )
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_ls_files_with_directory_should_call_git_ls_files_from_directory(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_proxy.ls_files(["."], directory=path)

        mock_git.assert_git_call(["ls-files", "."])
        local_mock.cwd.assert_called_with(path)


class TestAdd:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_add_with_no_directory_should_call_git_add(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.add(".")

        mock_git.assert_git_call(["add", "."])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_add_with_directory_should_switch_directories(self, local_mock, git_proxy, mock_git):
        path = Path("/path/to/repo").absolute()
        git_proxy.add(["."], directory=path)

        mock_git.assert_git_call(["add", "."])
        local_mock.cwd.assert_called_with(path)


class TestRestore:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_restore_with_no_directory_should_call_git_restore(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.restore(".")

        mock_git.assert_git_call(["restore", "."])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_restore_with_staged_should_call_git_with_staged_option(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.restore(".", staged=True)

        mock_git.assert_git_call(["restore", "--staged", "."])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_restore_with_directory_should_switch_directories(
        self, local_mock, git_proxy, mock_git
    ):
        path = Path("/path/to/repo").absolute()
        git_proxy.restore(["."], directory=path)

        mock_git.assert_git_call(["restore", "."])
        local_mock.cwd.assert_called_with(path)


class TestRebase:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_rebase_with_no_directory_should_call_git_rebase(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.rebase(onto="abc123")

        mock_git.assert_git_call(["rebase", "--onto", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_rebase_with_directory_should_switch_directories(self, local_mock, git_proxy, mock_git):
        path = Path("/path/to/repo").absolute()
        git_proxy.rebase(onto="abc123", directory=path)

        mock_git.assert_git_call(["rebase", "--onto", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestMerge:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_merge_with_no_directory_should_call_git_rebase(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.merge("abc123")

        mock_git.assert_git_call(["merge", "abc123"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_merge_with_directory_should_switch_directories(self, local_mock, git_proxy, mock_git):
        path = Path("/path/to/repo").absolute()
        git_proxy.merge("abc123", directory=path)

        mock_git.assert_git_call(["merge", "abc123"])
        local_mock.cwd.assert_called_with(path)


class TestCurrentCommit:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_current_commit_with_no_directory_should_return_git_hash(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        git_commit = git_proxy.current_commit()

        mock_git.assert_git_call(["rev-parse", "HEAD"])
        assert git_commit == "abc123"

    @patch(ns("local"))
    def test_current_commit_with_directory_should_switch_directories(
        self, local_mock, git_proxy, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        path = Path("/path/to/repo").absolute()
        git_commit = git_proxy.current_commit(directory=path)

        mock_git.assert_git_call(["rev-parse", "HEAD"])
        assert git_commit == "abc123"
        local_mock.cwd.assert_called_with(path)


class TestMergeBase:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_merge_base_with_no_directory_should_return_merge_base(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        git_commit = git_proxy.merge_base("commit_1", "HEAD")

        mock_git.assert_git_call(["merge-base", "commit_1", "HEAD"])
        assert git_commit == "abc123"

    @patch(ns("local"))
    def test_merge_base_with_directory_should_switch_directories(
        self, local_mock, git_proxy, mock_git
    ):
        mock_git.__getitem__.return_value.return_value = "abc123\n"

        path = Path("/path/to/repo").absolute()
        git_commit = git_proxy.merge_base("commit_1", "HEAD", directory=path)

        mock_git.assert_git_call(["merge-base", "commit_1", "HEAD"])
        assert git_commit == "abc123"
        local_mock.cwd.assert_called_with(path)


class TestCommit:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_commit_with_no_directory_should_call_git_commit(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.commit("commit message")

        mock_git.assert_git_call(["commit", "--message", "commit message"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_commit_with_amend_should_call_git_commit_with_amend(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.commit(amend=True)

        mock_git.assert_git_call(["commit", "--amend", "--reuse-message=HEAD"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_commit_with_add_should_call_git_commit_with_add(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.commit(amend=True, add=True)

        mock_git.assert_git_call(["commit", "--amend", "--reuse-message=HEAD", "--all"])
        local_mock.cwd.assert_called_with(test_path)

    @patch(ns("local"))
    def test_commit_with_directory_should_switch_directories(self, local_mock, git_proxy, mock_git):
        path = Path("/path/to/repo").absolute()
        git_proxy.commit("commit message", directory=path)

        mock_git.assert_git_call(["commit", "--message", "commit message"])
        local_mock.cwd.assert_called_with(path)


class TestGetBaseName:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_get_base_name_should_return_default_basename(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "origin/master"

        basename = git_proxy.get_mergebase_branch_name()
        mock_git.assert_git_call(["symbolic-ref", "refs/remotes/origin/HEAD"])
        assert basename == "master"


class TestCheckChanges:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_check_changes_should_return_changes(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "diff --git aaa bbb\n"

        diff = git_proxy.check_changes("master")

        mock_git.assert_git_call(["diff", "master..HEAD"])
        assert diff is True

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_current_branch_should_return_branch_name(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "branch\n"

        diff = git_proxy.current_branch()

        mock_git.assert_git_call(["rev-parse", "--abbrev-ref", "HEAD"])
        assert diff == "branch"

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_branch_exist_on_remote_should_return_remote_branch(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "origin/branch\n"

        remote_branch = git_proxy.current_branch_exist_on_remote("branch")

        mock_git.assert_git_call(["branch", "--remotes", "--contains", "branch"])
        assert remote_branch == "origin/branch"


class TestPushBranchToRemote:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_push_should_call_git_push(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "my-branch"

        git_proxy.push_branch_to_remote()

        mock_git.assert_git_call(["push", "-u", "origin", "HEAD"])

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_push_should_fail_on_protected_branch(self, path_mock, local_mock, git_proxy, mock_git):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "master"

        with pytest.raises(UsageError):
            git_proxy.push_branch_to_remote()

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_push_with_directory_should_switch_directories(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        path = Path("/path/to/repo").absolute()
        git_proxy.push_branch_to_remote(directory=path)

        mock_git.assert_git_call(["push", "-u", "origin", "HEAD"])
        local_mock.cwd.assert_called_with(path)

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_push_with_specified_remote_should_call_git_push(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        git_proxy.push_branch_to_remote(remote="remote")

        mock_git.assert_git_call(["push", "-u", "remote", "HEAD"])


class TestDetermineRemote:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_current_remote_should_return_remote_name(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = "remote\n"

        diff = git_proxy.current_remote(test_path)

        mock_git.assert_git_call(["config", "--get-regexp", ".url"])
        assert diff == ["remote"]

    @patch(ns("local"))
    @patch(ns("Path"))
    @pytest.mark.parametrize(
        "remote, current_remotes, urls",
        [
            ("origin", "remote.10gen 10gen_url\nremote.origin origin_url", "origin_url"),
            ("origin", "remote.origin origin_url", "origin"),
        ],
    )
    def test_determine_remote_should_return_remote_url_if_find(
        self, path_mock, local_mock, git_proxy, mock_git, remote, current_remotes, urls
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        mock_git.__getitem__.return_value.return_value = current_remotes

        remote_url = git_proxy.determine_remote(remote, test_path)

        assert urls == remote_url

    @patch(ns("local"))
    @patch(ns("Path"))
    def test_determine_remote_should_raise_error_if_remote_not_find(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        test_path = make_fake_path()
        path_mock.return_value = test_path
        current_remotes = "remote.10gen 10gen_url\nremote.tester tester_url\n"
        mock_git.__getitem__.return_value.return_value = current_remotes
        remote = "origin"

        with pytest.raises(UsageError):
            git_proxy.determine_remote(remote, test_path)


class TestGetRemoteUrl:
    @patch(ns("local"))
    @patch(ns("Path"))
    def test_get_remote_url_should_raise_error_if_push_to_protected_remote(
        self, path_mock, local_mock, git_proxy, mock_git
    ):
        current_remotes = ["remote.10gen 10gen_url", "remote.origin.mongodb mongodb/mongo.git"]
        remote = "origin"

        with pytest.raises(UsageError):
            git_proxy.get_remote_url(remote, current_remotes)

    @patch(ns("local"))
    @pytest.mark.parametrize(
        "remote, current_remotes, expected_url",
        [
            ("origin", ["remote.10gen 10gen_url", "remote.origin origin_url"], "origin_url"),
            ("origin", ["remote.other other_url"], None),
        ],
    )
    def test_get_remote_url_should_return_remote_url_if_find(
        self, local_mock, git_proxy, remote, current_remotes, expected_url
    ):
        url = git_proxy.get_remote_url(remote, current_remotes)

        assert url == expected_url


class TestDetermineDirectory:
    @patch(ns("local"))
    def test_directory_of_none_should_return_cwd(self, local_mock, git_proxy):
        local_mock.cwd = "fake"
        assert git_proxy._determine_directory(None) == Path(local_mock.cwd)

    @patch(ns("local"))
    def test_relative_directory_should_return_full_path(self, local_mock, git_proxy):
        directory = Path("a/relative/path")
        local_mock.cwd = "fake"
        assert git_proxy._determine_directory(directory) == Path(local_mock.cwd / directory)

    @patch(ns("local"))
    def test_absolute_directory_should_return_directory(self, local_mock, git_proxy):
        directory = Path("/a/absolute/path").absolute()
        assert git_proxy._determine_directory(directory) == directory
