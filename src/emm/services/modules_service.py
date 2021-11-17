"""Service for working with evergreen modules."""
from pathlib import Path
from typing import Dict

import inject
from shrub.v3.evg_project import EvgModule

from emm.options import EmmOptions
from emm.services.evg_service import EvgService
from emm.services.file_service import FileService
from emm.services.git_service import GitService


class ModulesService:
    """A service for working with evergreen modules."""

    @inject.autoparams()
    def __init__(
        self,
        emm_options: EmmOptions,
        evg_service: EvgService,
        git_service: GitService,
        file_service: FileService,
    ) -> None:
        """
        Initialize the service.

        :param emm_options: Configuration options for modules.
        :param evg_service: Service for working with evergreen.
        :param git_service: Service for working with git.
        :param file_service: Service for working with files.
        """
        self.emm_options = emm_options
        self.evg_service = evg_service
        self.git_service = git_service
        self.file_service = file_service

    def enable(self, module_name: str, sync_commit: bool = True) -> None:
        """
        Enable the given module.

        :param module_name: Name of module to enable.
        :param sync_commit: If True, checkout the module commit associated with the base repo.
        """
        module_data = self.get_module_data(module_name)
        modules_dir = self.emm_options.modules_directory
        module_location = modules_dir / module_data.get_repository_name()

        target_dir = Path(module_data.prefix)

        if not self.file_service.path_exists(target_dir):
            self.file_service.mkdirs(target_dir)

        target_location = target_dir / module_name
        if self.file_service.path_exists(target_location):
            raise ValueError(f"Module {module_name} already exists at {target_location}")

        if not module_location.exists():
            self.git_service.clone(
                module_data.get_repository_name(), module_data.repo, modules_dir, module_data.branch
            )

        print(f"Create symlink: {target_location} -> {module_location.resolve()}")
        self.file_service.create_symlink(target_location, module_location.resolve())

        if sync_commit:
            self.sync_module(module_name, module_data)

    def disable(self, module_name: str) -> None:
        """Disable to specified module."""
        module_data = self.get_module_data(module_name)
        target_dir = Path(module_data.prefix)

        target_location = target_dir / module_name
        if not self.file_service.path_exists(target_location):
            raise ValueError(f"Module {module_name} does not exists at {target_location}")

        self.file_service.rm_symlink(target_location)

    def get_module_data(self, module_name: str) -> EvgModule:
        """
        Get data about the specified module.

        :param module_name: Module to query.
        :return: Details about the module.
        """
        modules_data = self.evg_service.get_module_map(self.emm_options.evg_project)
        if module_name not in modules_data:
            raise ValueError(f"Could not find module {module_name} in evergreen project config.")

        return modules_data[module_name]

    def get_all_modules(self, enabled: bool) -> Dict[str, EvgModule]:
        """
        Get a dictionary of all known modules.

        :param enabled: If True only return modules enabled locally.
        :return: Dictionary of module names to module information.
        """
        all_modules = self.evg_service.get_module_map(self.emm_options.evg_project)
        pred = self.is_module_enabled if enabled else lambda _name, _: True
        return {k: v for k, v in all_modules.items() if pred(k, v)}

    def is_module_enabled(self, module_name: str, module_data: EvgModule) -> bool:
        """
        Determine if the given module is enabled locally.

        :param module_name: Name of module to check.
        :param module_data: Data about the module being checked.
        :return: True if module is enabled locally.
        """
        module_location = Path(module_data.prefix) / module_name
        return self.file_service.path_exists(module_location)

    def sync_module(self, module_name: str, module_data: EvgModule) -> None:
        """
        Sync the given module to the commit associated with the base repo in evergreen.

        :param module_name: Name of module being synced.
        :param module_data: Data about the module.
        """
        project_branch = self.evg_service.get_project_branch(self.emm_options.evg_project)
        base_revision = self.git_service.merge_base(project_branch, "HEAD")
        manifest = self.evg_service.get_manifest(self.emm_options.evg_project, base_revision)
        manifest_modules = manifest.modules
        if manifest_modules is None:
            raise ValueError("Modules not found in manifest")

        module_manifest = manifest_modules.get(module_name)
        if module_manifest is None:
            raise ValueError(f"Module not found in manifest: {module_name}")

        module_revision = module_manifest.revision
        module_location = Path(module_data.prefix) / module_name

        self.git_service.fetch(module_location)
        self.git_service.checkout(module_revision, directory=module_location)
