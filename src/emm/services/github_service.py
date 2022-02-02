"""Service for working with github CLI."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from plumbum import TF, local
from plumbum.machines.local import LocalCommand


class GithubService:
    """A service for interacting with github CLI."""

    def __init__(self, gh_cli: LocalCommand) -> None:
        """
        Initialize the service.

        :param gh_cli: Github CLI in command line.
        """
        self.gh_cli = gh_cli

    @classmethod
    def create(cls) -> GithubService:
        """Initialize the github cli in command line."""
        if not shutil.which("gh"):
            raise SystemExit(
                "Please make sure you've installed the Github CLI. "
                "Instructions on how to do so can be found at https://cli.github.com/."
            )
        return cls(local.cmd.gh)

    def pull_request(self, extra_args: List[str], directory: Optional[Path] = None) -> str:
        """
        Create the pull request using Github CLI.

        :param extra_args: Extra arguments to pass to the github CLI.
        :param directory: Directory to execute command at.
        :return: Url of the created pull request.
        """
        args = ["pr", "create"]
        args.extend(extra_args)
        with local.cwd(self._determine_directory(directory)):
            return self.gh_cli[args]().strip()

    def pr_comment(self, pr_url: str, comment: str, directory: Optional[Path] = None) -> None:
        """
        Add Pull Request url as comments for each repo.

        :param pr_url: Pull request url to add the comment.
        :param comment: Comment to add for the given pull request.
        :param directory: Directory to execute command at.
        """
        args = ["pr", "comment", pr_url, "--body", comment]
        with local.cwd(self._determine_directory(directory)):
            self.gh_cli[args]()

    def validate_github_authentication(self, directory: Optional[Path] = None) -> bool:
        """
        Validate the github CLI is authenticated.

        :param directory: Directory to execute command at.
        :return The authentication result from github CLI.
        """
        args = ["auth", "status"]
        with local.cwd(self._determine_directory(directory)):
            res = self.gh_cli[args] & TF(FG=True)
            return res

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
