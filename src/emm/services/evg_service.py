"""A service for working with evergreen data."""
from functools import lru_cache
from pathlib import Path
from typing import Dict

import inject
from evergreen import EvergreenApi, Manifest, Project
from shrub.v3.evg_project import EvgModule

from emm.services.file_service import FileService


class EvgService:
    """A service for working with evergreen data."""

    @inject.autoparams()
    def __init__(self, evg_api: EvergreenApi, file_service: FileService) -> None:
        """Initialize the service."""
        self.evg_api = evg_api
        self.file_service = file_service

    def get_project_config_location(self, project_id: str) -> str:
        """
        Get the path to the evergreen config file for this project.

        :param project_id: ID of Evergreen project being queried.
        :return: Path to project config file.
        """
        return self.get_evg_project(project_id).remote_path

    def get_project_branch(self, project_id: str) -> str:
        """
        Get the git branch a project works from.

        :param project_id: ID of project to lookup.
        :return: Branch name a project works from.
        """
        return self.get_evg_project(project_id).branch_name

    @lru_cache(maxsize=None)
    def get_evg_project(self, project_id: str) -> Project:
        """
        Get the project configuration for the given evergreen project.

        :param project_id: ID of project to lookup.
        :return: Project configuration for specified project.
        """
        project_config_list = self.evg_api.all_projects(
            project_filter_fn=lambda p: p.identifier == project_id
        )
        if len(project_config_list) != 1:
            raise ValueError(f"Could not find unique project configuration for : '{project_id}'.")
        return project_config_list[0]

    def get_module_locations(self, project_id: str) -> Dict[str, str]:
        """
        Get the paths that project modules are stored.

        :param project_id: ID of project to query.
        :return: Dictionary of modules and their paths.
        """
        module_map = self.get_module_map(project_id)
        return {module.name: module.prefix for module in module_map.values()}

    def get_module_map(self, project_id: str) -> Dict[str, EvgModule]:
        """
        Get a dictionary of known modules and data about them.

        :param project_id: Evergreen ID of project being queried.
        :return: Dictionary of module names to module data.
        """
        project_config_location = self.get_project_config_location(project_id)
        project_config = self.file_service.read_yaml_file(Path(project_config_location))
        return {module["name"]: EvgModule(**module) for module in project_config.get("modules", [])}

    def get_manifest(self, project_id: str, commit_hash: str) -> Manifest:
        """
        Get the manifest for the given commit and evergreen project.

        :param project_id: Evergreen project to query.
        :param commit_hash: Evergreen commit to query.
        :return: Evergreen manifest for given commit.
        """
        return self.evg_api.manifest(project_id, commit_hash)
