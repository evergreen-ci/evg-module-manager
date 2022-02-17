"""Models for working with git repositories."""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple, Optional

from shrub.v3.evg_project import EvgModule

BASE_REPO = "base"


class GitCommandOutput(NamedTuple):
    """
    Output for the execution of a git command.

    * module_name: Name of module where git command was executed.
    * output: Output of git command.
    """

    module_name: str
    output: str


class Repository(NamedTuple):
    """
    Information about a repository.

    * name: Name of the repository.
    * directory: Path to the location of the repository.
    * target_branch: Branch that a PR should be created against.
    """

    name: str
    directory: Optional[Path]
    target_branch: str

    @classmethod
    def base_repo(cls, branch: str) -> Repository:
        """
        Create an instance representing the base repo.

        :param branch: Branch to target.
        :return: Instance of the base repository.
        """
        return cls(name=BASE_REPO, directory=None, target_branch=branch)

    @classmethod
    def from_module(cls, module: EvgModule) -> Repository:
        """
        Create an instance representing a module repo.

        :return: Instance of a module repository.
        """
        return cls(
            name=module.name,
            directory=Path(module.prefix) / module.name,
            target_branch=module.branch,
        )
