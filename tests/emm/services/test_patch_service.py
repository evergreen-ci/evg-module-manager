"""Unit tests for patch_service.py."""
from unittest.mock import MagicMock

import pytest
from shrub.v3.evg_project import EvgModule

import emm.services.patch_service as under_test
from emm.options import EmmOptions
from emm.services.evg_cli_service import EvgCliService
from emm.services.evg_service import EvgService
from emm.services.file_service import FileService


@pytest.fixture()
def file_service():
    return MagicMock(spec_set=FileService)


@pytest.fixture()
def evg_cli_service():
    return MagicMock(spec_set=EvgCliService)


@pytest.fixture()
def evg_service():
    return MagicMock(spec_set=EvgService)


@pytest.fixture()
def emm_options():
    return MagicMock(spec=EmmOptions)


@pytest.fixture()
def patch_service(file_service, evg_cli_service, evg_service, emm_options):
    patch_service = under_test.PatchService(file_service, evg_cli_service, evg_service, emm_options)
    return patch_service


def build_module_data(i):
    return EvgModule(
        name=f"mock_module_{i}",
        repo=f"git@github.com:org/mock-module-{i}.git",
        branch="main",
        prefix="src/modules",
    )


class TestCreatePatch:
    def test_a_patch_with_no_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service
    ):
        evg_service.get_module_map.return_value = {}

        patch_info = patch_service.create_patch([])

        assert patch_info == evg_cli_service.create_patch.return_value
        evg_cli_service.add_module_to_patch.assert_not_called()

    def test_a_patch_with_no_enabled_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(10)
        }
        file_service.path_exists.return_value = False

        patch_info = patch_service.create_patch([])

        assert patch_info == evg_cli_service.create_patch.return_value
        evg_cli_service.add_module_to_patch.assert_not_called()

    def test_a_patch_with_enabled_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]

        patch_info = patch_service.create_patch([])

        assert patch_info == evg_cli_service.create_patch.return_value
        assert 3 == evg_cli_service.add_module_to_patch.call_count

    def test_patches_should_pass_along_extra_args(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]
        extra_args = ["-u", "-d", "hello world"]

        patch_info = patch_service.create_patch(extra_args)

        assert patch_info == evg_cli_service.create_patch.return_value
        evg_cli_service.create_patch.assert_called_with(extra_args)
        assert 3 == evg_cli_service.add_module_to_patch.call_count


class TestCreateCqPatch:
    def test_a_patch_with_no_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service
    ):
        evg_service.get_module_map.return_value = {}

        patch_info = patch_service.create_cq_patch([])

        assert patch_info == evg_cli_service.create_cq_patch.return_value
        evg_cli_service.finalize_cq_patch.assert_called_with(patch_info.patch_id)
        evg_cli_service.add_module_to_cq_patch.assert_not_called()

    def test_a_patch_with_no_enabled_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(10)
        }
        file_service.path_exists.return_value = False

        patch_info = patch_service.create_cq_patch([])

        assert patch_info == evg_cli_service.create_cq_patch.return_value
        evg_cli_service.finalize_cq_patch.assert_called_with(patch_info.patch_id)
        evg_cli_service.add_module_to_cq_patch.assert_not_called()

    def test_a_patch_with_enabled_modules_should_be_created_and_finalized(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]

        patch_info = patch_service.create_cq_patch([])

        assert patch_info == evg_cli_service.create_cq_patch.return_value
        evg_cli_service.finalize_cq_patch.assert_called_with(patch_info.patch_id)
        assert 3 == evg_cli_service.add_module_to_cq_patch.call_count

    def test_a_patch_should_pass_extra_args_to_commands(
        self, patch_service, evg_cli_service, evg_service, file_service
    ):
        evg_service.get_module_map.return_value = {
            f"module_{i}": build_module_data(i) for i in range(5)
        }
        file_service.path_exists.side_effect = [True, False, True, False, True]

        patch_info = patch_service.create_cq_patch(["--large"])

        assert patch_info == evg_cli_service.create_cq_patch.return_value
        evg_cli_service.finalize_cq_patch.assert_called_with(patch_info.patch_id)
        assert 3 == evg_cli_service.add_module_to_cq_patch.call_count
        evg_cli_service.create_cq_patch.assert_called_with(["--large"])
