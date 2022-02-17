"""Service to orchestrate git branch actions across all repositories."""
from typing import List

import inject

from emm.clients.git_proxy import GitProxy
from emm.models.repository import GitCommandOutput
from emm.services.modules_service import ModulesService, UpdateStrategy


class GitBranchService:
    """Service to orchestrate git branch actions across all module repositories."""

    @inject.autoparams()
    def __init__(
        self,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ) -> None:
        """
        Initialize the service.

        :param modules_service: Service for working with modules.
        :param git_proxy: Service for working with git.
        """
        self.git_proxy = git_proxy
        self.modules_service = modules_service

    def create_branch(self, branch_name: str, branch_base: str) -> List[str]:
        """
        Create a branch in all modules.

        :param branch_name: Name of branch to create.
        :param branch_base: Revision to base branch off.
        """
        # First checkout the desired revision in the base module and sync all the
        # other modules to it.
        self.git_proxy.checkout(branch_base)
        self.modules_service.sync_all_modules(enabled=True)

        # Now create the branch in all the modules.
        repository_list = self.modules_service.collect_repositories()
        for repo in repository_list:
            self.git_proxy.checkout(branch_name=branch_name, directory=repo.directory)

        return [repo.name for repo in repository_list]

    def branch_list(self) -> List[GitCommandOutput]:
        """List all existing branches for each module."""
        repository_list = self.modules_service.collect_repositories()
        branch_status = [
            GitCommandOutput(
                module_name=repo.name, output=self.git_proxy.branch(directory=repo.directory)
            )
            for repo in repository_list
        ]
        return branch_status

    def switch_branch(self, branch_name: str) -> List[str]:
        """
        Checkout the given branch in each module.

        :param branch_name: Name of branch to checkout.
        :return: All modules where branch was checked out.
        """
        repository_list = self.modules_service.collect_repositories()
        for repo in repository_list:
            self.git_proxy.checkout(revision=branch_name, directory=repo.directory)

        return [repo.name for repo in repository_list]

    def delete_branch(self, branch_name: str) -> List[str]:
        """
        Delete the given branch in each module.

        :param branch_name: Name of branch to delete.
        :return: All modules where branch was deleted.
        """
        repository_list = self.modules_service.collect_repositories()
        for repo in repository_list:
            self.git_proxy.branch(delete=branch_name, directory=repo.directory)

        return [repo.name for repo in repository_list]

    def update_branch(self, branch: str, rebase: bool) -> List[GitCommandOutput]:
        """
        Update the current branch with commits from the given branch.

        :param branch: Branch to get updates from.
        :param rebase: If True, rebase on top of changes, else merge changes in.
        :return: List of what commit each module was checked out to.
        """
        repository_list = self.modules_service.collect_repositories()
        for repo in repository_list:
            self.git_proxy.fetch(directory=repo.directory)

        if rebase:
            self.git_proxy.rebase(branch)
            update_strategy = UpdateStrategy.REBASE
        else:
            self.git_proxy.merge(branch)
            update_strategy = UpdateStrategy.MERGE

        return [
            GitCommandOutput(module_name=module_name, output=revision)
            for module_name, revision in self.modules_service.sync_all_modules(
                enabled=True, update_strategy=update_strategy
            ).items()
        ]

    def pull(self, rebase: bool) -> List[GitCommandOutput]:
        """
        Perform a git pull on the base repository and sync all modules to it.

        :param rebase: If True, rebase on top of changes, else merge changes in.
        :return: List of what commit each module was checked out to.
        """
        self.git_proxy.pull(rebase)
        update_strategy = UpdateStrategy.REBASE if rebase else UpdateStrategy.MERGE
        return [
            GitCommandOutput(module_name=module_name, output=revision)
            for module_name, revision in self.modules_service.sync_all_modules(
                enabled=True, update_strategy=update_strategy
            ).items()
        ]
