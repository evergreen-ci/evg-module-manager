"""unit tests for git_commit_service.py."""

import textwrap
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

import emm.services.git_commit_service as under_test
from emm.clients.git_proxy import GitProxy
from emm.models.repository import Repository
from emm.services.modules_service import ModulesService


@pytest.fixture()
def modules_service():
    modules_service = MagicMock(spec_set=ModulesService)
    return modules_service


@pytest.fixture()
def git_service():
    git_service = MagicMock(spec_set=GitProxy)
    return git_service


@pytest.fixture()
def git_commit_service(git_service, modules_service):
    git_commit_service = under_test.GitCommitService(git_service, modules_service)
    return git_commit_service


def build_mock_repository(index: int, directory: Optional[Path] = None):
    return Repository(
        name=f"repo_name_{index}",
        directory=directory,
        target_branch=f"target_branch_{index}",
    )


class TestStatus:
    def test_status_should_call_git_status_on_all_repos(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        repos = git_commit_service.status()

        assert len(repos) == len(module_list)
        assert git_service.status.call_count == len(module_list)
        for repo in repos:
            assert repo.module_name in [module.name for module in module_list]
            assert repo.output == git_service.status.return_value


class TestAdd:
    def test_add_should_return_results_for_all_modules(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        results = git_commit_service.add(["."])

        assert len(results) == len(module_list)
        assert git_service.add.call_count == len(module_list)


class TestAddToRepo:
    def test_added_files_should_be_reported(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        repo = build_mock_repository(0)
        n_files = 5
        git_service.ls_files.return_value = [f"file {i}" for i in range(n_files)]
        git_service.status.return_value = "\n".join([f"M  file {i}" for i in range(n_files)])

        result = git_commit_service.add_to_repo(["."], repo)

        assert result.module_name == repo.name
        assert len(result.output.splitlines()) == n_files

    def test_no_added_files_should_be_reported_empty_string(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        repo = build_mock_repository(0)
        git_service.ls_files.return_value = []
        git_service.status.return_value = "\n".join([f"M  file {i}" for i in range(5)])

        result = git_commit_service.add_to_repo(["."], repo)

        assert result.module_name == repo.name
        assert result.output == ""


class TestRestore:
    def test_restore_should_return_results_for_all_modules(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        results = git_commit_service.restore(["."], staged=False)

        assert len(results) == len(module_list)
        assert git_service.restore.call_count == len(module_list)


class TestRestoreFromRepo:
    def test_restored_files_should_be_reported(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        repo = build_mock_repository(0)
        n_files = 5
        git_service.ls_files.return_value = [f"file {i}" for i in range(n_files)]
        git_service.status.return_value = "\n".join([f"M  file {i}" for i in range(n_files)])

        result = git_commit_service.restore_from_repo(["."], True, repo)

        assert result.module_name == repo.name
        assert len(result.output.splitlines()) == n_files

    def test_no_restored_files_should_be_reported_empty_string(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        repo = build_mock_repository(0)
        git_service.ls_files.return_value = []
        git_service.status.return_value = "\n".join([f"M  file {i}" for i in range(5)])

        result = git_commit_service.restore_from_repo(["."], False, repo)

        assert result.module_name == repo.name
        assert result.output == ""


class TestFilesToTrack:
    def test_ignore_file_should_be_specified_if_it_exists(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        directory = MagicMock(spec_set=Path)
        repo = build_mock_repository(0, directory)
        git_service.ls_files.return_value = [f"file {i}" for i in range(5)]

        file_set = git_commit_service.files_to_track(["."], repo)

        assert len(file_set) == 5
        git_service.ls_files.assert_called_with(
            ["."], cached=True, others=True, ignore_file=".gitignore", directory=directory
        )

    def test_ignore_file_should_not_be_specified_if_it_does_not_exists(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        directory = MagicMock(spec_set=Path)
        repo = build_mock_repository(0, directory)
        directory.__truediv__.return_value.exists.return_value = False
        git_service.ls_files.return_value = [f"file {i}" for i in range(5)]

        file_set = git_commit_service.files_to_track(["."], repo)

        assert len(file_set) == 5
        git_service.ls_files.assert_called_with(
            ["."], cached=True, others=True, ignore_file=None, directory=directory
        )


class TestCommit:
    def test_commit_with_message_should_call_git_commit_on_all_repos(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        n_modules = 3
        module_list = [
            build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(n_modules)
        ]
        modules_service.collect_repositories.return_value = module_list
        git_service.status.return_value = """M  file1.txt"""

        repos = git_commit_service.commit("my message", False, False)

        assert len(repos) == n_modules
        assert git_service.commit.call_count == n_modules
        git_service.commit.assert_any_call(
            "my message", amend=False, add=False, directory=module_list[0].directory
        )

    def test_commit_with_append_should_call_git_commit_on_all_repos(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        n_modules = 3
        module_list = [
            build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(n_modules)
        ]
        modules_service.collect_repositories.return_value = module_list
        git_service.status.return_value = """M  file1.txt"""

        repos = git_commit_service.commit(None, amend=True, add=False)

        assert len(repos) == n_modules
        assert git_service.commit.call_count == n_modules
        git_service.commit.assert_any_call(
            None, amend=True, add=False, directory=module_list[0].directory
        )

    def test_commit_with_add_should_call_git_commit_on_all_repos(
        self,
        git_commit_service: under_test.GitCommitService,
        modules_service: ModulesService,
        git_service: GitProxy,
    ):
        n_modules = 3
        module_list = [
            build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(n_modules)
        ]
        modules_service.collect_repositories.return_value = module_list
        git_service.status.return_value = """M  file1.txt"""

        repos = git_commit_service.commit("my message", amend=False, add=True)

        assert len(repos) == n_modules
        assert git_service.commit.call_count == n_modules
        git_service.commit.assert_any_call(
            "my message", amend=False, add=True, directory=module_list[0].directory
        )


class TestGetStatusLines:
    def test_status_lines_should_be_returned_as_a_list(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = """
        M  file1.txt
        M  file2.txt
         M file3.txt
        """
        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        status_lines = git_commit_service.get_status_lines(repo)

        assert any("file1.txt" in line for line in status_lines)
        assert any("file2.txt" in line for line in status_lines)
        assert any("file3.txt" in line for line in status_lines)

        git_service.status.assert_called_with(short=True, directory=repo.directory)


class TestGetTouchedFiles:
    def test_touched_files_should_be_returned_as_a_list(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = textwrap.dedent(
            """
        M  file1.txt
        M  file2.txt
        M  file3.txt
        ?? file4.txt
        """
        )
        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        touched_files = git_commit_service.get_touched_files(repo)

        assert "file1.txt" in touched_files
        assert "file2.txt" in touched_files
        assert "file3.txt" in touched_files
        assert "file4.txt" in touched_files

        git_service.status.assert_called_with(short=True, directory=repo.directory)


class TestHasCommitableChange:
    def test_has_commitable_changes_should_return_true_if_there_are_staged_files(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = textwrap.dedent(
            """
        M  file1.txt
        M  file2.txt
        M  file3.txt
        ?? file4.txt
        """
        )
        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        assert git_commit_service.has_commitable_change(add=False, repo=repo)

    def test_has_commitable_changes_should_return_false_if_there_are_no_staged_files(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = """ M file1.txt
 M file2.txt
 M file3.txt
?? file4.txt"""

        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        assert not git_commit_service.has_commitable_change(add=False, repo=repo)

    def test_has_commitable_changes_should_return_true_if_there_are_no_staged_files_but_add_is_used(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = """ M file1.txt
 M file2.txt
 M file3.txt
?? file4.txt"""

        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        assert git_commit_service.has_commitable_change(add=True, repo=repo)

    def test_has_commitable_changes_should_not_consider_untracked_files(
        self,
        git_commit_service: under_test.GitCommitService,
        git_service: GitProxy,
    ):
        git_service.status.return_value = """?? file4.txt"""

        repo = build_mock_repository(0, directory=Path("/path/to/repo"))

        assert not git_commit_service.has_commitable_change(add=True, repo=repo)
