"""CLI interfaces for git actions."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

import click
import inject
from rich import print as rprint

from emm.services.git_branch_service import GitBranchService
from emm.services.git_commit_service import GitCommitService
from emm.services.validation_service import ValidationService

STATUS_STAGED_SIGNATURE = "Changes to be committed:"
STATUS_NOT_STAGED_SIGNATURE = "Changes not staged for commit:"
STATUS_UNTRACKED_SIGNATURE = "Untracked files:"
STATUS_TRANSITION_SIGNATURES = [
    STATUS_STAGED_SIGNATURE,
    STATUS_NOT_STAGED_SIGNATURE,
    STATUS_UNTRACKED_SIGNATURE,
]


class StatusState(Enum):
    """State of the output of the status command."""

    STAGED = "staged"
    NOT_STAGED = "not_staged"
    UNTRACKED = "untracked"
    NONE = "none"

    def next_state(self, line: str) -> StatusState:
        """
        Get the next state of the status output.

        :param line: Next line of output.
        :return: State of output based on given line
        """
        if line.startswith(STATUS_STAGED_SIGNATURE):
            return StatusState.STAGED
        if line.startswith(STATUS_NOT_STAGED_SIGNATURE):
            return StatusState.NOT_STAGED
        if line.startswith(STATUS_UNTRACKED_SIGNATURE):
            return StatusState.UNTRACKED
        return self

    def annotate_color(self, line: str) -> str:
        """
        Annotate the given line with a color based on the state.

        :param line: Line to annotate.
        :return: Line with a color annotated.
        """
        if any(line.startswith(sig) for sig in STATUS_TRANSITION_SIGNATURES):
            return line

        if line.strip().startswith("(") and line.strip().endswith(")"):
            return line

        if self == StatusState.STAGED:
            return f"[green]{line}[/green]"
        if self == StatusState.NOT_STAGED:
            return f"[red]{line}[/red]"
        if self == StatusState.UNTRACKED:
            return f"[red]{line}[/red]"

        return line


class GitOrchestrator:
    """Orchestrator for git subcommands."""

    @inject.autoparams()
    def __init__(
        self, git_branch_service: GitBranchService, git_commit_service: GitCommitService
    ) -> None:
        """
        Initialize the orchestrator.

        :param git_branch_service: Service to work with git branches.
        :param git_commit_service: Service to work with git commits.
        """
        self.git_branch_service = git_branch_service
        self.git_commit_service = git_commit_service

    def create_branch(self, branch_name: str, revision: str) -> None:
        """
        Create a branch on all repositories.

        :param branch_name: Name of branch to create.
        :param revision: Revision to base branch off.
        """
        modules = self.git_branch_service.create_branch(branch_name, revision)
        rprint(f"Branch [green]'{branch_name}'[/green] created on: ")
        for module in modules:
            rprint(f" - [yellow]{module}[/yellow]")

    def view_branches(self) -> None:
        """View branches on all enabled repositories."""
        branches = self.git_branch_service.branch_list()
        for module in branches:
            rprint(f"Branches in [yellow]'{module.module_name}'[/yellow]:")
            for branch in module.output.splitlines():
                branch_name = branch
                if branch.startswith("*"):
                    branch_name = f"[green]{branch}[/green]"
                rprint(branch_name)

    def switch_branch(self, branch_name: str) -> None:
        """
        Switch to the given branch from all repositories.

        :param branch_name: Name of branch to switch to.
        """
        modules = self.git_branch_service.switch_branch(branch_name)
        rprint(f"Switched to [green]'{branch_name}'[/green] in: ")
        for module in modules:
            rprint(f" - [yellow]{module}[/yellow]")

    def delete_branch(self, branch_name: str) -> None:
        """
        Delete branch from all repositories.

        :param branch_name: Name of branch to delete.
        """
        modules = self.git_branch_service.delete_branch(branch_name)
        rprint(f"Branch [red]'{branch_name}'[/red] deleted from: ")
        for module in modules:
            rprint(f" - [yellow]{module}[/yellow]")

    def update_branch(self, branch: str, rebase: bool) -> None:
        """
        Pull in changes from the specified branch.

        :param branch: Branch to pull changes from.
        :param rebase: If True, rebase on top of changes, else merge changes in.
        """
        modules = self.git_branch_service.update_branch(branch, rebase)
        rprint(f"[yellow]Base[/yellow]: updated to latest '{branch}'")
        for module in modules:
            rprint(f"- [yellow]{module.module_name}[/yellow]: {module.output}")

    def pull(self, rebase: bool) -> None:
        """
        Pull the latest changes from origin.

        :param rebase: If True, rebase on top of changes, else merge changes in.
        """
        modules = self.git_branch_service.pull(rebase)
        rprint("[yellow]Base[/yellow]: pulled to latest")
        for module in modules:
            rprint(f"- [yellow]{module.module_name}[/yellow]: {module.output}")

    def status(self) -> None:
        """Get the status of all repositories."""
        status_list = self.git_commit_service.status()
        for status in status_list:
            rprint(f"Status of [yellow]{status.module_name}[/yellow]:")
            state = StatusState.NONE
            for line in status.output.splitlines():
                state = state.next_state(line)
                rprint(f"  {state.annotate_color(line)}")
            print()

    def add(self, pathspecs: List[str]) -> None:
        """Add the given pathspecs to staging."""
        file_lists = self.git_commit_service.add(pathspecs)
        for file_list in file_lists:
            rprint(f"Files added to [yellow]{file_list.module_name}[/yellow].")

    def restore(self, pathspecs: List[str], staged: bool) -> None:
        """Add the given pathspecs to staging."""
        file_lists = self.git_commit_service.restore(pathspecs, staged)
        for file_list in file_lists:
            rprint(f"Files restored from [yellow]{file_list.module_name}[/yellow].")

    def commit(self, message: Optional[str], amend: bool, add: bool) -> None:
        """
        Commit changes to git.

        :param message: Message to use for commit.
        :param amend: If true,  amend changes to previous commit.
        :param add: If true, add all tracked changes to commit.
        """
        module_list = self.git_commit_service.commit(message, amend, add)
        action = "amended" if amend else "created"
        print(f"Commit {action} in the following modules:")
        for module in module_list:
            rprint(f" - [yellow]{module}[/yellow]")


@click.group(name="git")
def git_cli() -> None:
    """Perform git actions against the base repo and enabled modules."""
    pass


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("-b", "--branch", required=True, help="Name of branch to create.")
@click.option("-r", "--revision", default="HEAD", help="Revision to base created branch off.")
@click.pass_context
def branch_create(ctx: click.Context, revision: str, branch: str) -> None:
    """Create a new git branch on all enabled repositories."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.create_branch(branch, revision)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
def branch_show(ctx: click.Context) -> None:
    """Show existing branches on all enabled repositories."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.view_branches()


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("-b", "--branch", required=True, help="Name of branch to delete.")
@click.pass_context
def branch_switch(ctx: click.Context, branch: str) -> None:
    """Checkout the specified branch in all enabled modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.switch_branch(branch)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("-b", "--branch", required=True, help="Name of branch to delete.")
@click.pass_context
def branch_delete(ctx: click.Context, branch: str) -> None:
    """Delete given branch in all enabled modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.delete_branch(branch)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option(
    "--rebase",
    is_flag=True,
    default=False,
    help="Rebase on top of any changes instead of merging changes.",
)
@click.pass_context
def branch_pull(ctx: click.Context, rebase: bool) -> None:
    """Pull the latest updates from remote repositories."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.pull(rebase)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("-b", "--branch", type=str, required=True, help="Branch to pull updates from.")
@click.option(
    "--rebase",
    is_flag=True,
    default=False,
    help="Rebase on top of any changes instead of merging changes.",
)
@click.pass_context
def branch_update(ctx: click.Context, branch: str, rebase: bool) -> None:
    """Get the latest changes from remote repositories and update the current branch with them."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.update_branch(branch, rebase)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
def status(ctx: click.Context) -> None:
    """Get the git status of all modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.status()


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("-m", "--message", help="Git commit message to use.")
@click.option("--amend", is_flag=True, default=False, help="Amend changes to the previous commit.")
@click.option(
    "-a",
    "--add",
    is_flag=True,
    default=False,
    help="Add change to any tracked file in the created commit.",
)
@click.pass_context
def commit(ctx: click.Context, message: Optional[str], amend: bool, add: bool) -> None:
    """Get the git status of all modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.commit(message, amend, add)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.argument("pathspec", nargs=-1)
@click.pass_context
def add(ctx: click.Context, pathspec: List[str]) -> None:
    """Perform git add on all matching files in all modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.add(pathspec)


@git_cli.command(context_settings=dict(max_content_width=100))
@click.option("--staged", is_flag=True, default=False, help="Restore file from the staging area.")
@click.argument("pathspec", nargs=-1)
@click.pass_context
def restore(ctx: click.Context, pathspec: List[str], staged: bool) -> None:
    """Perform git restore on all matching files in all modules."""
    validation_service = inject.instance(ValidationService)
    validation_service.validate_git_command()
    orchestrator = inject.instance(GitOrchestrator)
    orchestrator.restore(pathspec, staged)
