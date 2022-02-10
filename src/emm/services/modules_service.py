"""Service for working with evergreen modules."""
from enum import Enum
from pathlib import Path
from typing import Dict, List

import inject
import structlog
from shrub.v3.evg_project import EvgModule

from emm.clients.evg_service import EvgService, Manifest
from emm.clients.git_proxy import GitProxy
from emm.models.repository import Repository
from emm.options import EmmOptions
from emm.services.file_service import FileService

LOGGER = structlog.get_logger(__name__)


class UpdateStrategy(str, Enum):
    """
    How branch updates should be resolved.

    * merge: Create a merge commit with the changes.
    * rebase: Rebase changes on top of specified commit.
    * checkout: Checkout the specified commit.
    """

    MERGE = "merge"
    REBASE = "rebase"
    CHECKOUT = "checkout"


class ModulesService:
    """A service for working with evergreen modules."""

    @inject.autoparams()
    def __init__(
        self,
        emm_options: EmmOptions,
        evg_service: EvgService,
        git_service: GitProxy,
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

    def collect_repositories(self) -> List[Repository]:
        """
        Create a list of potential repositories for the base and all enabled modules.

        :param project_id: Evergreen Project ID of base repository.
        :return: List of repositories associated the base repository.
        """
        enabled_modules = self.get_all_modules(enabled=True)
        repository_list = [Repository.from_module(module) for module in enabled_modules.values()]
        evg_project_id = self.emm_options.evg_project
        repository_list.append(
            Repository.base_repo(self.evg_service.get_project_branch(evg_project_id))
        )
        return repository_list

    def is_module_enabled(self, module_name: str, module_data: EvgModule) -> bool:
        """
        Determine if the given module is enabled locally.

        :param module_name: Name of module to check.
        :param module_data: Data about the module being checked.
        :return: True if module is enabled locally.
        """
        module_location = Path(module_data.prefix) / module_name
        return self.file_service.path_exists(module_location)

    def get_evg_manifest(self, evg_project: str) -> Manifest:
        """
        Get the evergreen manifest base on evergreen project.

        :param evg_project: The project to retrieve manifest.
        :return: The manifest modules in evergreen associate with the latest commit.
        """
        project_branch = self.evg_service.get_project_branch(evg_project)
        base_revision = self.git_service.merge_base(project_branch, "HEAD")
        return self.evg_service.get_manifest(evg_project, base_revision)

    def sync_module(
        self,
        module_name: str,
        module_data: EvgModule,
        update_strategy: UpdateStrategy = UpdateStrategy.CHECKOUT,
    ) -> str:
        """
        Sync the given module to the commit associated with the base repo in evergreen.

        :param module_name: Name of module being synced.
        :param module_data: Data about the module.
        :param update_strategy: How module should be synced to target commit.
        :return: Git hash that module was synced to.
        """
        manifest = self.get_evg_manifest(self.emm_options.evg_project)
        manifest_modules = manifest.modules
        if manifest_modules is None:
            raise ValueError("Modules not found in manifest")

        module_manifest = manifest_modules.get(module_name)
        if module_manifest is None:
            raise ValueError(f"Module not found in manifest: {module_name}")

        module_revision = module_manifest.revision
        module_location = Path(module_data.prefix) / module_name

        self.git_service.fetch(module_location)
        if update_strategy == UpdateStrategy.REBASE:
            self.git_service.rebase(module_revision, directory=module_location)
        elif update_strategy == UpdateStrategy.CHECKOUT:
            self.git_service.checkout(module_revision, directory=module_location)
        elif update_strategy == UpdateStrategy.MERGE:
            self.git_service.merge(module_revision, directory=module_location)
        else:
            raise NotImplementedError(f"Update strategy '{update_strategy}' not supported.")
        return module_revision

    def sync_all_modules(
        self, enabled: bool, update_strategy: UpdateStrategy = UpdateStrategy.CHECKOUT
    ) -> Dict[str, str]:
        """
        Sync all modules with the current commit of the base module.

        :param active: Only sync enabled modules.
        :param update_strategy: How module should be synced to target commit.
        :return: Dictionary of modules synced and git hash modules were synced to.
        """
        modules = self.get_all_modules(enabled)
        return {
            module_name: self.sync_module(module_name, module_data, update_strategy)
            for module_name, module_data in modules.items()
        }
