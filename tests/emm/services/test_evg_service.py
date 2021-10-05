"""Unit tests for evg_service.py."""
from unittest.mock import MagicMock

import pytest
from evergreen import EvergreenApi, Project

import emm.services.evg_service as under_test
from emm.services.file_service import FileService


@pytest.fixture()
def evg_api():
    mock_evg_api = MagicMock(spec_set=EvergreenApi)
    return mock_evg_api


@pytest.fixture()
def file_service():
    mock_file_service = MagicMock(spec_set=FileService)
    return mock_file_service


@pytest.fixture()
def evg_service(evg_api, file_service):
    evg_service = under_test.EvgService(evg_api, file_service)
    return evg_service


class TestGetProjectConfigLocation:
    def test_config_location_should_return_remote_path(self, evg_service, evg_api):
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]

        path = evg_service.get_project_config_location("my-project")

        assert path == "path/to/config.yml"


class TestGetProjectBranch:
    def test_get_project_branch_should_return_branch_name(self, evg_service, evg_api):
        mock_project = MagicMock(spec=Project, branch_name="main")
        evg_api.all_projects.return_value = [mock_project]

        branch = evg_service.get_project_branch("my-project")

        assert branch == "main"


class TestGetEvgProject:
    def test_project_that_cant_be_found_should_throw_error(self, evg_service, evg_api):
        evg_api.all_projects.return_value = []

        with pytest.raises(ValueError):
            evg_service.get_evg_project("my-project")

    def test_project_that_can_be_found_should_return_remote_path(self, evg_service, evg_api):
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]

        project = evg_service.get_evg_project("my-project")

        assert project == mock_project


class TestGetModuleLocations:
    def test_project_with_no_modules_should_return_empty_dict(
        self, evg_service, evg_api, file_service
    ):
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]
        file_service.read_yaml_file.return_value = {}

        module_dict = evg_service.get_module_locations("my-project")

        assert module_dict == {}

    def test_project_with_modules_should_return_all_modules(
        self, evg_service, evg_api, file_service
    ):
        n_modules = 5
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]
        file_service.read_yaml_file.return_value = {
            "modules": [
                {
                    "name": f"module_name_{i}",
                    "repo": f"git@github.com:myorg/mymodule_{i}.git",
                    "branch": "main",
                    "prefix": "src/modules",
                }
                for i in range(n_modules)
            ]
        }

        module_dict = evg_service.get_module_locations("my-project")

        assert len(module_dict) == 5
        for i in range(n_modules):
            assert module_dict[f"module_name_{i}"] == "src/modules"


class TestGetModuleMap:
    def test_project_with_no_modules_should_return_empty_dict(
        self, evg_service, evg_api, file_service
    ):
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]
        file_service.read_yaml_file.return_value = {}

        module_dict = evg_service.get_module_map("my-project")

        assert module_dict == {}

    def test_project_with_modules_should_return_all_modules(
        self, evg_service, evg_api, file_service
    ):
        n_modules = 5
        mock_project = MagicMock(spec=Project, remote_path="path/to/config.yml")
        evg_api.all_projects.return_value = [mock_project]
        file_service.read_yaml_file.return_value = {
            "modules": [
                {
                    "name": f"module_name_{i}",
                    "repo": f"git@github.com:myorg/mymodule_{i}.git",
                    "branch": "main",
                    "prefix": "src/modules",
                }
                for i in range(n_modules)
            ]
        }

        module_dict = evg_service.get_module_map("my-project")

        assert len(module_dict) == 5
        for i in range(n_modules):
            assert module_dict[f"module_name_{i}"].repo == f"git@github.com:myorg/mymodule_{i}.git"


class TestGetManifest:
    def test_get_manifest_should_call_evg_api(self, evg_service, evg_api):
        manifest = evg_service.get_manifest("project_id", "abc123")

        assert manifest == evg_api.manifest.return_value
        evg_api.manifest.assert_called_with("project_id", "abc123")
