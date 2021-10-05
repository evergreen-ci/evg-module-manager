"""Unit tests for modules_service.py."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from shrub.v3.evg_project import EvgModule

import emm.services.modules_service as under_test
from emm.options import EmmOptions
from emm.services.evg_service import EvgService
from emm.services.file_service import FileService
from emm.services.git_service import GitService


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
