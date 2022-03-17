"""Service for working with git."""
from __future__ import annotations

from os import path
from pathlib import Path
from typing import List, Optional

import structlog
from click import UsageError
from plumbum import local
from plumbum.machines.local import LocalCommand

LOGGER = structlog.get_logger(__name__)
PROTECTED_BRANCHES = {"main", "master"}


class GitProxy:
    """A service for interacting with git."""

    def __init__(self, git: LocalCommand) -> None:
        """Initialize the service."""
        self.git = git

    @classmethod
    def create(cls) -> GitProxy:
        """Create evergreen CLI service instance."""
        return cls(local.cmd.git)

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

    def pull(self, rebase: bool = False, directory: Optional[Path] = None) -> None:
        """
        Pull latest changes to branch.

        :param rebase: If True, rebase on top of changes, else merge changes in.
        :param directory: Path to root of repo to operate on.
        """
        args = ["pull"]
        if rebase:
            args.append("--rebase")
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def checkout(
        self,
        revision: Optional[str] = None,
        directory: Optional[Path] = None,
        branch_name: Optional[str] = None,
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
        if revision is not None:
            args.append(revision)
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def branch(self, delete: Optional[str] = None, directory: Optional[Path] = None) -> str:
        """
        Run the branch command against the specified repository.

        :param delete: Execute the delete version of branch against the provided branch.
        :param directory: Directory where the repository lives.
        """
        args = ["branch"]
        if delete is not None:
            args.extend(["-D", delete])
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]()

    def status(self, short: bool = False, directory: Optional[Path] = None) -> str:
        """
        Run the status command against the specified repository.

        :param directory: Directory where the repository lives.
        """
        args = ["status"]
        if short:
            args.append("--short")
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]()

    def ls_files(
        self,
        pathspecs: List[str],
        cached: bool = False,
        others: bool = False,
        ignore_file: Optional[str] = None,
        directory: Optional[Path] = None,
    ) -> List[str]:
        """
        Run the ls-files command against the specified repository.

        :param pathspecs: List of path specs to search.
        :param cached: If True, report on cached files.
        :param others: If True, report on untracked files.
        :param ignore_file: File describing which files to ignore.
        :param directory: Directory to execute command at.
        :return: List of files that match the given path specs.
        """
        args = ["ls-files"]
        if cached:
            args.append("--cached")
        if others:
            args.append("--others")
        if ignore_file is not None:
            args.append(f"--exclude-from={ignore_file}")
        args.extend(pathspecs)
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip().splitlines()

    def add(self, files: List[str], directory: Optional[Path] = None) -> None:
        """
        Run the add command against the specified repository.

        :param files: List of files to add.
        :param directory: Directory to execute command at.
        """
        args = ["add"]
        args.extend(files)
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def restore(
        self, files: List[str], staged: bool = False, directory: Optional[Path] = None
    ) -> None:
        """
        Run the add restore command against the specified repository.

        :param files: List of files to restore.
        :param staged: If true, the given files should be unstaged.
        :param directory: Directory to execute command at.
        """
        args = ["restore"]
        if staged:
            args.append("--staged")

        args.extend(files)
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def rebase(self, onto: str, directory: Optional[Path] = None) -> None:
        """
        Rebase on the given revision.

        :param onto: Revision to rebase on.
        :param directory: Directory to execute command at.
        """
        args = ["rebase", "--onto", onto]
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

    def commit(
        self,
        commit_message: Optional[str] = None,
        amend: bool = False,
        add: bool = False,
        directory: Optional[Path] = None,
    ) -> None:
        """
        Get the commit hash of the current HEAD of a repository.

        :param commit_message: Commit message for all the changes.
        :param amend: Amend the commit to previous commit instead of creating a new one.
        :param add: Make changes to tracked files part of commit.
        :param directory: Directory to execute command at.
        """
        args = ["commit"]
        if commit_message is not None:
            args.extend(["--message", commit_message])

        if amend:
            args.extend(["--amend", "--reuse-message=HEAD"])

        if add:
            args.append("--all")

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

        args = ["push", "-u", "origin", "HEAD"]
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
