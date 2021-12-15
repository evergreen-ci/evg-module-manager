"""Unit tests for modules_service.py."""
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from shrub.v3.evg_project import EvgModule

import emm.services.modules_service as under_test
from emm.options import EmmOptions
from emm.services.evg_service import EvgService
from emm.services.file_service import FileService
from emm.services.git_service import GitAction, GitService


@pytest.fixture()
def emm_options():
    emm_options = MagicMock(spec=EmmOptions)
    emm_options.modules_directory = Path("target_directory")
    return emm_options


@pytest.fixture()
def evg_service():
    evg_service = MagicMock(spec_set=EvgService)
    return evg_service


@pytest.fixture()
def git_service():
    git_service = MagicMock(spec_set=GitService)
    return git_service


@pytest.fixture()
def file_service():
    file_service = MagicMock(spec_set=FileService)
    return file_service


@pytest.fixture()
def modules_service(emm_options, evg_service, git_service, file_service):
    modules_service = under_test.ModulesService(emm_options, evg_service, git_service, file_service)
    return modules_service


def build_module_data():
    return EvgModule(
        name="mock module",
        repo="git@github.com:org/mock-module.git",
        branch="main",
        prefix="src/modules",
    )


class TestEnable:
    def test_an_already_enabled_modules_should_raise_an_exception(
        self, modules_service, evg_service, file_service
    ):
        module_name = "mock_module"
        mock_module = build_module_data()
        evg_service.get_module_map.return_value = {module_name: mock_module}
        file_service.path_exists.return_value = True

        with pytest.raises(ValueError):
            modules_service.enable(module_name)
            expected_path = Path(mock_module.get_repository_name()) / module_name
            file_service.path_exists.assert_called_with(expected_path)

    def test_non_existing_target_dir_should_be_created(
        self, modules_service, evg_service, file_service
    ):
        module_name = "mock_module"
        mock_module = build_module_data()
        evg_service.get_module_map.return_value = {module_name: mock_module}
        file_service.path_exists.side_effect = [False, False, True]

        modules_service.enable(module_name)

        expected_path = Path(mock_module.prefix)
        file_service.mkdirs.assert_called_with(expected_path)

    def test_symlink_should_be_created(
        self, modules_service, evg_service, file_service, emm_options
    ):
        module_name = "mock_module"
        mock_module = build_module_data()
        evg_service.get_module_map.return_value = {module_name: mock_module}
        file_service.path_exists.side_effect = [False, False, True]

        modules_service.enable(module_name)

        expected_target = Path(mock_module.prefix) / module_name
        expected_source = emm_options.modules_directory / mock_module.get_repository_name()
        file_service.create_symlink.assert_called_with(expected_target, expected_source.resolve())

    def test_non_existing_module_should_be_cloned(
        self, modules_service, evg_service, file_service, emm_options, git_service
    ):
        module_name = "mock_module"
        mock_module = build_module_data()
        evg_service.get_module_map.return_value = {module_name: mock_module}
        file_service.path_exists.return_value = False

        modules_service.enable(module_name)

        git_service.clone.assert_called_with(
            mock_module.get_repository_name(),
            mock_module.repo,
            emm_options.modules_directory,
            mock_module.branch,
        )


class TestDisable:
    def test_disabling_a_disabled_module_should_raise_an_exception(
        self, modules_service, file_service, evg_service
    ):
        module_name = "mock_module"
        evg_service.get_module_map.return_value = {module_name: build_module_data()}
        file_service.path_exists.return_value = False

        with pytest.raises(ValueError):
            modules_service.disable(module_name)

    def test_disabling_a_module_should_rm_the_symlink(
        self, modules_service, file_service, evg_service
    ):
        module_name = "mock_module"
        mock_module = build_module_data()
        evg_service.get_module_map.return_value = {module_name: mock_module}
        file_service.path_exists.return_value = True

        modules_service.disable(module_name)

        expected_path = Path(mock_module.prefix) / module_name
        file_service.rm_symlink.assert_called_with(expected_path)


class TestGetModuleData:
    def test_missing_modules_should_raise_an_exception(self, modules_service, evg_service):
        evg_service.get_module_map.return_value = {}

        with pytest.raises(ValueError):
            modules_service.get_module_data("a missing modules")

    def test_existing_modules_should_be_returned(self, modules_service, evg_service):
        module_name = "my module"
        module_data = build_module_data()
        evg_service.get_module_map.return_value = {module_name: module_data}

        returned_module = modules_service.get_module_data(module_name)

        assert returned_module == module_data


class TestGetAllModules:
    def test_existing_modules_should_be_returned_when_enabled_requested(
        self, modules_service, file_service, evg_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_name_{i}": build_module_data() for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]

        modules = modules_service.get_all_modules(enabled=True)

        assert len(modules) == 3

    def test_all_modules_should_be_returned_when_enabled_not_requested(
        self, modules_service, file_service, evg_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_name_{i}": build_module_data() for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]

        modules = modules_service.get_all_modules(enabled=False)

        assert len(modules) == 5


class TestIsModuleEnabled:
    def test_existing_module_should_return_true(self, modules_service, file_service):
        module_name = "my module"
        module_data = build_module_data()
        file_service.path_exists.return_value = True

        assert modules_service.is_module_enabled(module_name, module_data) is True

        expected_path = Path(module_data.prefix) / module_name
        file_service.path_exists.assert_called_with(expected_path)

    def test_non_existing_module_should_return_false(self, modules_service, file_service):
        module_name = "my module"
        module_data = build_module_data()
        file_service.path_exists.return_value = False

        assert modules_service.is_module_enabled(module_name, module_data) is False

        expected_path = Path(module_data.prefix) / module_name
        file_service.path_exists.assert_called_with(expected_path)


class TestSyncModule:
    def test_sync_should_fetch_and_checkout_based_on_manifest(
        self, modules_service, evg_service, git_service
    ):
        module_name = "my module"
        module_data = build_module_data()
        module_revision = "abc123"
        evg_service.get_manifest.return_value.modules = {
            module_name: MagicMock(revision=module_revision)
        }

        modules_service.sync_module(module_name, module_data)

        expected_location = Path(module_data.prefix) / module_name
        git_service.fetch.assert_called_with(expected_location)
        git_service.checkout.assert_called_with(module_revision, directory=expected_location)

    def test_sync_with_no_manifest_modules_should_raise_exception(
        self, modules_service, evg_service, git_service
    ):
        module_name = "my module"
        module_data = build_module_data()
        evg_service.get_manifest.return_value.modules = None

        with pytest.raises(ValueError):
            modules_service.sync_module(module_name, module_data)

    def test_sync_with_no_module_should_raise_exception(
        self, modules_service, evg_service, git_service
    ):
        module_name = "my module"
        module_data = build_module_data()
        evg_service.get_manifest.return_value.modules = {}

        with pytest.raises(ValueError):
            modules_service.sync_module(module_name, module_data)


class TestGitOperateBase:
    def test_checkout_should_call_git_checkout(self, modules_service, evg_service, git_service):
        revision = "test_revision"
        modules_service.git_operate_base(GitAction.CHECKOUT, revision, None)

        git_service.perform_git_action.assert_called_with(GitAction.CHECKOUT, revision, None, None)

    def test_checkout_should_create_branch_if_specified(
        self, modules_service, evg_service, git_service
    ):
        revision = "test_revision"
        branch = "test_branch"
        modules_service.git_operate_base(GitAction.CHECKOUT, revision, branch)
        git_service.perform_git_action.assert_called_with(
            GitAction.CHECKOUT, revision, branch, None
        )

    def test_rebase_should_call_git_rebase(self, modules_service, evg_service, git_service):
        revision = "test_revision"
        modules_service.git_operate_base(GitAction.REBASE, revision, None)
        git_service.perform_git_action.assert_called_with(GitAction.REBASE, revision, None, None)

    def test_merge_should_should_call_git_merge(self, modules_service, evg_service, git_service):
        revision = "test_revision"
        modules_service.git_operate_base(GitAction.MERGE, revision, None)
        git_service.perform_git_action.assert_called_with(GitAction.MERGE, revision, None, None)


class TestGitOperateModule:
    def test_operate_module_with_no_manifest_should_raise_exception(
        self, modules_service, evg_service, git_service
    ):
        evg_service.get_manifest.return_value.modules = None
        enabled_module = {"module_name": build_module_data()}

        with pytest.raises(ValueError):
            modules_service.git_operate_modules(GitAction.CHECKOUT, None, enabled_module)

    def test_operate_module_with_no_module_should_raise_exception(
        self, modules_service, evg_service, git_service
    ):
        evg_service.get_manifest.return_value.modules = {}
        enabled_module = {"module_name": build_module_data()}

        with pytest.raises(ValueError):
            modules_service.git_operate_modules(GitAction.CHECKOUT, None, enabled_module)

    def test_checkout_should_apply_revision_and_directory_to_each_module(
        self, modules_service, evg_service, git_service
    ):
        evg_service.get_manifest.return_value.modules = {
            f"module_name_{i}": MagicMock(revision=f"revision_{i}") for i in range(5)
        }
        enabled_module = {f"module_name_{i}": build_module_data() for i in range(5)}

        modules_service.git_operate_modules(GitAction.CHECKOUT, None, enabled_module)
        calls = [
            call(
                GitAction.CHECKOUT, f"revision_{i}", None, Path("src/modules") / f"module_name_{i}"
            )
            for i in range(5)
        ]
        git_service.perform_git_action.assert_has_calls(calls, any_order=True)


class TestCommitModule:
    def test_commit_should_call_git_commit_all(
        self,
        modules_service,
        evg_service,
        git_service,
    ):
        commit = "test_commit"
        modules_service.git_commit_modules(commit)
        git_service.commit_all.assert_called_with(commit)

    def test_commit_should_apply_path_to_each_module(
        self,
        modules_service,
        evg_service,
        git_service,
    ):
        commit = "test_commit"
        evg_service.get_module_map.return_value = {
            f"module_name_{i}": build_module_data() for i in range(3)
        }
        modules_service.git_commit_modules(commit)
        calls = [
            call(commit),
            call(commit, Path("src/modules") / "module_name_1"),
            call(commit, Path("src/modules") / "module_name_2"),
        ]
        git_service.commit_all.assert_has_calls(calls, any_order=True)


class TestPullRequestModule:
    def test_pull_request_should_call_git_pull_request(
        self,
        modules_service,
        evg_service,
        git_service,
    ):
        args = ["--title", "Test title", "--body", "Test body"]
        modules_service.git_pull_request(args)

        git_service.pull_request.assert_called_with(args)

    def test_pull_request_comment_should_call_git_pr_comment(
        self,
        modules_service,
        evg_service,
        git_service,
    ):
        comments = {"base": "github.com/pull/123", "module_name_1": "github.com/pull/234"}
        evg_service.get_module_map.return_value = {"module_name_1": build_module_data()}
        modules_service.add_pr_link(comments)

        calls = [
            call("github.com/pull/123", "module_name_1 pr: github.com/pull/234"),
            call(
                "github.com/pull/234",
                "base pr: github.com/pull/123",
                Path("src/modules") / "module_name_1",
            ),
        ]

        git_service.pr_comment.assert_has_calls(calls, any_order=True)
