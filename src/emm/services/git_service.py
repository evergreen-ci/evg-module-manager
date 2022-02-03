"""Service for working with git."""
from __future__ import annotations

from enum import Enum
from os import path
from pathlib import Path
from typing import Optional

import structlog
from click import UsageError
from plumbum import local
from plumbum.machines.local import LocalCommand

LOGGER = structlog.get_logger(__name__)
PROTECTED_BRANCHES = {"main", "master"}


class GitAction(str, Enum):
    """Actions to perform on a git repository."""

    CHECKOUT = "checkout"
    REBASE = "rebase"
    MERGE = "merge"


class GitService:
    """A service for interacting with git."""

    def __init__(self, git: LocalCommand) -> None:
        """Initialize the service."""
        self.git = git

    @classmethod
    def create(cls) -> GitService:
        """Create evergreen CLI service instance."""
        return cls(local.cmd.git)

    def perform_git_action(
        self,
        git_action: GitAction,
        revision: str,
        branch_name: Optional[str] = None,
        directory: Optional[Path] = None,
    ) -> None:
        """
        Perform the given git action on a repository.

        :param git_action: Git action to perform.
        :param revision: Git revision to perform action against.
        :param branch_name: Branch name to create if running checkout.
        :param directory: Path to root of repo to operate on.
        """
        if git_action == GitAction.CHECKOUT:
            self.checkout(revision, directory, branch_name)
        elif git_action == GitAction.REBASE:
            self.rebase(revision, directory)
        elif git_action == GitAction.MERGE:
            self.merge(revision, directory)
        else:
            raise ValueError(f"Unknown git action: {git_action.value}")

    def clone(self, name: str, remote_repo: str, directory: Path, branch: Optional[str]) -> None:
        """
        Clone the specified repository to the given location.

        :param name: Local name to use for cloned repo.
        :param remote_repo: Remote repo location.
        :param directory: Directory to clone repo into.
        :param branch: Branch to checkout.
        """
        args = ["clone"]
        if branch is not None:
            args += ["--branch", branch]
        args += [remote_repo, name]

        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def fetch(self, directory: Optional[Path] = None) -> None:
        """
        Fetch commit from origin.

        :param directory: Path to root of repo to operate on.
        """
        args = ["fetch", "origin"]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def checkout(
        self, revision: str, directory: Optional[Path] = None, branch_name: Optional[str] = None
    ) -> None:
        """
        Checkout the given revision.

        :param revision: Revision to checkout.
        :param directory: Directory to execute command at.
        :param branch_name: Name of branch for git checkout.
        """
        args = ["checkout"]
        if branch_name is not None:
            args += ["-b", branch_name]
        args.append(revision)
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def rebase(self, revision: str, directory: Optional[Path] = None) -> None:
        """
        Rebase on the given revision.

        :param revision: Revision to rebase on.
        :param directory: Directory to execute command at.
        """
        args = ["rebase", revision]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def merge(self, revision: str, directory: Optional[Path] = None) -> None:
        """
        Merge the given revision.

        :param revision: Revision to merge.
        :param directory: Directory to execute command at.
        """
        args = ["merge", revision]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def current_commit(self, directory: Optional[Path] = None) -> str:
        """
        Get the commit hash of the current HEAD of a repository.

        :param directory: Path to repository to query.
        :return: Git hash of HEAD of repository.
        """
        args = ["rev-parse", "HEAD"]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def merge_base(self, commit_a: str, commit_b: str, directory: Optional[Path] = None) -> str:
        """
        Find the common ancestor of the given commits.

        :param commit_a: First commit to compare.
        :param commit_b: Second commit to compare.
        :param directory: Path to repository to query.
        :return: Git hash of common ancestor of the 2 commits.
        """
        args = ["merge-base", commit_a, commit_b]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def commit_all(self, commit_message: str, directory: Optional[Path] = None) -> None:
        """
        Get the commit hash of the current HEAD of a repository.

        :param commit_message: Commit message for all the changes.
        :param directory: Directory to execute command at.
        """
        args = ["commit", "--all", "--message", commit_message]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def get_mergebase_branch_name(self, directory: Optional[Path] = None) -> str:
        """
        Get the base branch name of current repo.

        :param directory: Directory to execute command at.
        :return: Default basename of current repo.
        """
        args = ["symbolic-ref", "refs/remotes/origin/HEAD"]
        with local.cwd(self._determine_directory(directory)):
            symbolic_ref = self.git[args]()
            return path.basename(symbolic_ref).strip()

    def check_changes(self, basename: str, directory: Optional[Path] = None) -> bool:
        """
        Check if module have made any active changes.

        :param basename: Basename of current repo.
        :param directory: Directory to execute command at.
        :return: Whether there are changes in the current branch.
        """
        args = ["diff", f"{basename}..HEAD"]
        with local.cwd(self._determine_directory(directory)):
            return True if self.git[args]().strip() else False

    def current_branch(self, directory: Optional[Path] = None) -> str:
        """
        Get the current branch.

        :param directory: Directory to execute command at.
        """
        args = ["rev-parse", "--abbrev-ref", "HEAD"]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def current_branch_exist_on_remote(self, branch: str, directory: Optional[Path] = None) -> str:
        """
        Check if current branch exist on remote.

        :param branch: Name of current branch.
        :param directory: Directory to execute command at.
        :return: Branch in remote.
        """
        args = ["branch", "--remotes", "--contains", branch]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def push_branch_to_remote(self, directory: Optional[Path] = None) -> str:
        """
        Push current branch to remote.

        :param directory: Directory to execute command at.
        :return: Errors that occur during push branch to remote.
        """
        current_branch = self.current_branch(directory)
        if current_branch in PROTECTED_BRANCHES:
            LOGGER.warning(
                "Attempting to push protected branch", branch=current_branch, directory=directory
            )
            raise UsageError(
                f"Refusing to push changes to protected branch '{current_branch}' "
                f"in directory '{self._determine_directory(directory)}'"
            )

        args = ["push", "origin", "HEAD"]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    @staticmethod
    def _determine_directory(directory: Optional[Path] = None) -> Path:
        """
        Determine which directory to run git command in.

        :param directory: Directory containing it repository.
        :return: Path to run git commands in.
        """
        if directory is None:
            return Path(local.cwd)
        elif not directory.is_absolute():
            return Path(local.cwd / directory)
        return directory
