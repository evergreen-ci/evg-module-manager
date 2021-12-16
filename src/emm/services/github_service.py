"""Service for working with github CLI."""
from pathlib import Path
from typing import List, Optional

from plumbum import local


class GithubService:
    """A service for interacting with github CLI."""

    def __init__(self) -> None:
        """Initialize the service."""
        pass

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
            return local.cmd.gh[args]().strip()

    def pr_comment(self, pr_url: str, pr_links: str, directory: Optional[Path] = None) -> None:
        """
        Add Pull Request url as comments for each repo.

        :param pr_url: Pull request url to add the comment.
        :param pr_links: Other modules pull request url.
        :param directory: Directory to execute command at.
        """
        args = ["pr", "comment", pr_url, "--body", pr_links]
        with local.cwd(self._determine_directory(directory)):
            local.cmd.gh[args]()

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
