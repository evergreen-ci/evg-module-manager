"""A service to working with git commits."""
from pathlib import Path
from typing import List, Optional, Set

import inject

from emm.clients.git_proxy import GitProxy
from emm.models.repository import GitCommandOutput, Repository
from emm.services.modules_service import ModulesService

GIT_IGNORE_FILE = ".gitignore"


class GitCommitService:
    """A service for working with git commits."""

    @inject.autoparams()
    def __init__(self, git_service: GitProxy, modules_service: ModulesService) -> None:
        """
        Initialize the service.

        :param git_service: Service for working with git.
        :param modules_service: Service for working with modules.
        """
        self.git_service = git_service
        self.modules_service = modules_service

    def status(self) -> List[GitCommandOutput]:
        """Get the status of all repositories."""
        repository_list = self.modules_service.collect_repositories()
        branch_status = [
            GitCommandOutput(
                module_name=repo.name, output=self.git_service.status(directory=repo.directory)
            )
            for repo in repository_list
        ]
        return branch_status

    def add(self, pathspecs: List[str]) -> List[GitCommandOutput]:
        """
        Add any files in any repositories that match the given pathspecs to the staging area.

        :param pathspecs: Pathspecs to match against.
        :return: List of repositories and files that were added.
        """
        repository_list = self.modules_service.collect_repositories()
        return [self.add_to_repo(pathspecs, repo) for repo in repository_list]

    def add_to_repo(self, pathspecs: List[str], repo: Repository) -> GitCommandOutput:
        """
        Add any files in the given repository that match the given pathspecs to the staging area.

        :param pathspecs: Pathspecs to match against.
        :return: Files that were added to the repository.
        """
        files_in_repo = self.files_to_track(pathspecs, repo)
        touched_files = self.get_touched_files(repo)
        files_to_add = [tf for tf in touched_files if tf in files_in_repo]
        self.git_service.add(files_to_add, directory=repo.directory)
        return GitCommandOutput(module_name=repo.name, output="\n".join(files_to_add))

    def restore(self, pathspecs: List[str], staged: bool) -> List[GitCommandOutput]:
        """
        Restore any files in any repositories that match the given pathspecs.

        :param pathspecs: Pathspecs to match against.
        :param staged: If true, unstage matching files.
        :return: List of repositories and files that were restored.
        """
        repository_list = self.modules_service.collect_repositories()
        return [self.restore_from_repo(pathspecs, staged, repo) for repo in repository_list]

    def restore_from_repo(
        self, pathspecs: List[str], staged: bool, repo: Repository
    ) -> GitCommandOutput:
        """
        Restore any files in the given repository that match the given pathspecs.

        :param pathspecs: Pathspecs to match against.
        :param staged: If true, unstage matching files.
        :return: Files that were restored to the repository.
        """
        files_in_repo = self.files_to_track(pathspecs, repo)
        touched_files = self.get_touched_files(repo)
        files_to_restore = [tf for tf in touched_files if tf in files_in_repo]
        self.git_service.restore(files_to_restore, staged, directory=repo.directory)
        return GitCommandOutput(module_name=repo.name, output="\n".join(files_to_restore))

    def files_to_track(self, pathspecs: List[str], repo: Repository) -> Set[str]:
        """
        Determine which files match the given pathspecs.

        :param pathspecs: Pathspecs to search.
        :param repo: Repository to search.
        :return: Set of file paths that match the given pathspecs.
        """
        repo_base = repo.directory if repo.directory is not None else Path(".")
        ignore_file = None
        potential_ignore_file = repo_base / GIT_IGNORE_FILE
        if potential_ignore_file.exists():
            ignore_file = GIT_IGNORE_FILE
        return set(
            self.git_service.ls_files(
                pathspecs,
                cached=True,
                others=True,
                ignore_file=ignore_file,
                directory=repo.directory,
            )
        )

    def commit(self, message: Optional[str], amend: bool, add: bool) -> List[str]:
        """
        Commit the current changes in all modules.

        :param message: Commit message to use.
        :param amend: If true, amend changes to previous commit.
        :param add: If true, add all tracked changes as part of commit.
        :return: List of repos which had changes committed.
        """
        repository_list = self.modules_service.collect_repositories()
        repos_with_changes = [
            repo for repo in repository_list if self.has_commitable_change(add, repo)
        ]
        for repo in repos_with_changes:
            self.git_service.commit(message, amend=amend, add=add, directory=repo.directory)
        return [repo.name for repo in repos_with_changes]

    def get_status_lines(self, repo: Repository) -> List[str]:
        """
        Get a list of status lines from the specified repository.

        :param repo: Repository to query.
        :return: List of status lines for given repository.
        """
        return self.git_service.status(short=True, directory=repo.directory).splitlines()

    def get_touched_files(self, repo: Repository) -> List[str]:
        """
        Get a list of files that contain changes in the given repository.

        :param repo: Repository to query.
        :return: List of files with changes.
        """
        touched_files = self.get_status_lines(repo)
        touched_files = [tf[2:].strip() for tf in touched_files]
        return touched_files

    def has_commitable_change(self, add: bool, repo: Repository) -> bool:
        """
        Determine if the given repository has any changes that are ready for commit.

        :param add: If true, include any tracked changes in check.
        :param repo: Repository to check.
        :return: True if repository has changes ready for commit.
        """
        status_lines = self.get_status_lines(repo)
        items = [line for line in status_lines if not line.startswith("??")]
        if add:
            return len(items) > 0
        return len([item for item in items if not item.startswith(" ")]) > 0
