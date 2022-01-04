"""Service for working with evergreen modules."""
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

import inject
import structlog
from plumbum import ProcessExecutionError
from shrub.v3.evg_project import EvgModule

from emm.options import EmmOptions
from emm.services.evg_service import EvgService, Manifest
from emm.services.file_service import FileService
from emm.services.git_service import GitAction, GitService
from emm.services.github_service import GithubService

LOGGER = structlog.get_logger(__name__)

BASE_REPO = "base"
PROTECTED_BRANCHES = {"main", "master"}
PULL_REQUEST_INFORMATION = (
    "This code review is spread across multiple repositories. "
    "Links to the other components of this review can be found:\n "
)


class PullRequestInfo(NamedTuple):
    """
    Information about a created pull request.

    * module: The module name of this pull request.
    * pr_url: URL to pull request in github.
    * pr_links: The link of string to all enabled modules.
    """

    module: str
    pr_url: str
    pr_links: str


class ModulesService:
    """A service for working with evergreen modules."""

    @inject.autoparams()
    def __init__(
        self,
        emm_options: EmmOptions,
        evg_service: EvgService,
        git_service: GitService,
        github_service: GithubService,
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
        self.github_service = github_service
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

    def get_evg_manifest(self, evg_project: str) -> Manifest:
        """
        Get the evergreen manifest base on evergreen project.

        :param evg_project: The project to retrieve manifest.
        :return: The manifest modules in evergreen associate with the latest commit in evergreen history.
        """
        project_branch = self.evg_service.get_project_branch(evg_project)
        base_revision = self.git_service.merge_base(project_branch, "HEAD")
        return self.evg_service.get_manifest(evg_project, base_revision)

    def sync_module(self, module_name: str, module_data: EvgModule) -> None:
        """
        Sync the given module to the commit associated with the base repo in evergreen.

        :param module_name: Name of module being synced.
        :param module_data: Data about the module.
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
        self.git_service.checkout(module_revision, directory=module_location)

    def attempt_git_operation(
        self,
        operation: GitAction,
        revision: str,
        branch_name: Optional[str] = None,
        directory: Optional[Path] = None,
    ) -> Optional[str]:
        """
        Attempt to perform the specified git operation.

        :param operation: Git operation to perform.
        :param revision: Git revision to perform operation on.
        :param branch_name: Name of branch for git checkout.
        :param directory: Directory of git repository.
        :return: Error message if an error was encountered.
        """
        try:
            self.git_service.perform_git_action(operation, revision, branch_name, directory)
        except ProcessExecutionError:
            LOGGER.warning(
                f"Error encountered during git operation {operation} on {revision}", exc_info=True
            )
            return f"Encountered error performing '{operation}' on '{revision}'"
        return None

    def git_operate_modules(
        self, operation: GitAction, branch: str, enabled_modules: Dict[str, EvgModule]
    ) -> Dict[str, str]:
        """
        Git operate modules to the specific revisions.

        :param operation: Git operation to perform.
        :param branch: Name of branch for git checkout.
        :param enabled_modules: Dictionary of enabled modules.
        :return: Dictionary of error encountered.
        """
        error_encountered = {}
        manifest = self.get_evg_manifest(self.emm_options.evg_project)
        manifest_modules = manifest.modules
        if manifest_modules is None:
            raise ValueError("Modules not found in manifest")

        for module, module_data in enabled_modules.items():
            module_manifest = manifest_modules.get(module)
            if module_manifest is None:
                raise ValueError(f"Module not found in manifest: {module}")

            module_rev = module_manifest.revision
            module_location = Path(module_data.prefix) / module
            errmsg = self.attempt_git_operation(operation, module_rev, branch, module_location)
            if errmsg:
                error_encountered[module] = errmsg
        return error_encountered

    def git_operate_base(self, operation: GitAction, revision: str, branch: str) -> Dict[str, str]:
        """
        Git operate base to the specific revisions.

        :param operation: Git operation to perform.
        :param revision: Dictionary of module names and git revision to check out.
        :param branch: Name of branch for git checkout.
        :return: Dictionary of error encountered.
        """
        errmsg = self.attempt_git_operation(operation, revision, branch)
        enabled_modules = self.get_all_modules(True)
        error_encountered = self.git_operate_modules(operation, branch, enabled_modules)
        if errmsg:
            error_encountered["BASE"] = errmsg
        return error_encountered

    def git_commit_modules(self, commit: str) -> None:
        """
        Git commit all changes to all modules.

        :param commit: Commit content for all changes.
        """
        self.git_service.commit_all(commit)
        enabled_modules = self.get_all_modules(True)
        for module in enabled_modules:
            module_data = self.get_module_data(module)
            module_location = Path(module_data.prefix) / module
            self.git_service.commit_all(commit, module_location)

    def validate_github_authentication(self) -> bool:
        """Check if github CLI already authenticated."""
        return self.github_service.validate_github_authentication()

    def combine_pr_comments(self, comments: Dict[str, str]) -> List[PullRequestInfo]:
        """
        Combine the pull request comment string for each module.

        :param comments: Dictionary of module and its pull request url.
        :return: List of pull request information object.
        """
        pr_list: List[PullRequestInfo] = []
        new_line = "\n"
        for module, pr_url in comments.items():
            pr_links = new_line.join(
                f"* {repo} pr: {link}" for repo, link in comments.items() if repo != module
            )
            pr_list.append(PullRequestInfo(module=module, pr_url=pr_url, pr_links=pr_links))
        return pr_list

    def update_pr_links(self, pr_list: List[PullRequestInfo]) -> List[str]:
        """
        Update link to each module.

        :param pr_list: List of pull request information object.
        :return: List of pull requests being created associate with its link.
        """
        all_pull_requests = []
        for pr_info in pr_list:
            pr_url = pr_info.pr_url
            if pr_info.module != BASE_REPO:
                module_data = self.get_module_data(pr_info.module)
                module_location = Path(module_data.prefix) / pr_info.module
                pr_links = PULL_REQUEST_INFORMATION + pr_info.pr_links
                self.github_service.pr_comment(pr_url, pr_links, module_location)
                all_pull_requests.append(pr_url)
                all_pull_requests.append(pr_links)
            else:
                pr_links = PULL_REQUEST_INFORMATION + pr_info.pr_links
                self.github_service.pr_comment(pr_url, pr_links)
                all_pull_requests.append(pr_url)
                all_pull_requests.append(pr_links)

        return all_pull_requests

    def push_branch_to_remote(self, directory: Optional[Path] = None) -> None:
        """
        Push current branch to remote if current branch is not protected branch.

        :param directory: Directory to execute the command at.
        """
        branch = self.git_service.current_branch(directory)
        if branch in PROTECTED_BRANCHES:
            raise ValueError("Cannot push unreviewed modification to master.")

        if not self.git_service.current_branch_exist_on_remote(branch, directory):
            self.git_service.push_branch_to_remote(directory)

    def module_pull_request(self, args: List[str]) -> Dict[str, str]:
        """
        Create pull request for each module.

        :param args: Arguments to pass to the github CLi.
        :return: Dictionary of module and its pull request url.
        """
        comment_dict = {}
        changed_modules = []
        enabled_modules = self.get_all_modules(True)
        for module in enabled_modules:
            module_data = self.get_module_data(module)
            module_location = Path(module_data.prefix) / module
            basename = self.git_service.get_mergebase_branch_name(module_location)
            if basename and self.git_service.check_changes(basename, module_location):
                self.push_branch_to_remote(module_location)
                changed_modules.append(module)

        for module in changed_modules:
            module_data = self.get_module_data(module)
            module_location = Path(module_data.prefix) / module
            link = self.github_service.pull_request(args, module_location)
            comment_dict[module] = link
        return comment_dict

    def base_pull_request(self, args: List[str]) -> Dict[str, str]:
        """
        Create pull request for base repo.

        :param args: Arguments to pass to the github CLi.
        :return: Dictionary of base repo and its pull request url.
        """
        comment_dict = {}
        self.push_branch_to_remote()
        pr_link = self.github_service.pull_request(args)
        comment_dict[BASE_REPO] = pr_link
        return comment_dict

    def git_pull_request(self, args: List[str]) -> List[str]:
        """
        Create pull request for each module.

        :param args: Arguments to pass to the github CLi.
        :return: List of pull requests being created associate with its link.
        """
        comment_dict = self.base_pull_request(args)
        comment_dict = {**comment_dict, **self.module_pull_request(args)}

        comment_links = self.combine_pr_comments(comment_dict)
        return self.update_pr_links(comment_links)
