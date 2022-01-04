"""Command line entry point to application."""
import logging
import os.path
import sys
from pathlib import Path
from typing import List

import click
import inject
import structlog
from evergreen import EvergreenApi, RetryingEvergreenApi
from structlog.stdlib import LoggerFactory

from emm.options import DEFAULT_EVG_CONFIG, DEFAULT_EVG_PROJECT, DEFAULT_MODULES_PATH, EmmOptions
from emm.services.git_service import GitAction
from emm.services.modules_service import ModulesService
from emm.services.patch_service import PatchService

LOGGER = structlog.get_logger(__name__)

EXTERNAL_LOGGERS = [
    "evergreen",
    "inject",
    "urllib3",
]


class EmmOrchestrator:
    """An orchestrator for evg-module-manager."""

    @inject.autoparams()
    def __init__(self, modules_service: ModulesService, patch_service: PatchService) -> None:
        """Initialize the orchestrator."""
        self.modules_service = modules_service
        self.patch_service = patch_service

    def enable(self, module_name: str, sync_commit: bool) -> None:
        """
        Enable the specified module.

        :param module_name: Name of module to enable.
        :param sync_commit: If True, checkout the commit associated with the base repo.
        """
        self.modules_service.enable(module_name, sync_commit)

    def disable(self, module_name: str) -> None:
        """Disable the specified module."""
        self.modules_service.disable(module_name)

    def submit_patch(self, extra_args: List[str]) -> None:
        """
        Submit a patch with all the enabled modules.

        :param extra_args: Extra arguments to pass to the patch command.
        """
        patch_info = self.patch_service.create_patch(extra_args)
        print(f"Patch Submitted: {patch_info.patch_url}")

    def submit_cq_patch(self, extra_args: List[str]) -> None:
        """
        Submit a patch to the commit-queue with all the enabled modules.

        :param extra_args: Extra arguments to pass to the patch command.
        """
        patch_info = self.patch_service.create_cq_patch(extra_args)
        print(f"Patch Submitted: {patch_info.patch_url}")

    def display_modules(self, enabled: bool, details: bool) -> None:
        """
        Display the available modules.

        :param enabled: Only display enabled modules.
        :param details: Display module details.
        """
        modules = self.modules_service.get_all_modules(enabled)
        for module_name, module_data in modules.items():
            print(f"- {module_name}")
            if details:
                print(f"\tprefix: {module_data.prefix}")
                print(f"\trepo: {module_data.repo}")
                print(f"\tbranch: {module_data.branch}")

    def git_operate_base(self, revision: str, operation: GitAction, branch: str) -> None:
        """
        Git checkout|rebase|merge modules to the specific revision.

        :param revision: Dictionary of module names and git revision to check out.
        :param operation: Git operation to perform.
        :param branch: Name of branch for git checkout.
        """
        self.modules_service.git_operate_base(operation, revision, branch)

    def git_commit_modules(self, commit_message: str) -> None:
        """
        Git commit all changes to all modules.

        :param commit_message: Commit content for all changes.
        """
        self.modules_service.git_commit_modules(commit_message)

    def git_pull_request(self, args: List[str]) -> None:
        """
        Create pull request to all modules.

        :param args: Arguments pass to the github CLI.
        """
        authenticated = self.modules_service.validate_github_authentication()
        if not authenticated:
            # Note: github CLI is running on Front Process, it would display:
            # You are not logged into any GitHub hosts. Run **gh auth login** to authenticate.
            # Also github CLI would exit with a non-zero code if authenticated is true.
            raise click.ClickException("Please authenticate github CLI.")
        else:
            # Note: we would pass args to github CLI to handle cases when option title&body or fill
            # are not provided. Github CLI would error out and prompt error message that require user
            # to fill those fields.
            all_pull_requests = self.modules_service.git_pull_request(args)
            print(all_pull_requests)


def configure_logging(verbose: bool) -> None:
    """
    Configure logging.

    :param verbose: Enable verbose logging.
    """
    structlog.configure(logger_factory=LoggerFactory())
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        level=level,
        stream=sys.stderr,
    )
    for log_name in EXTERNAL_LOGGERS:
        logging.getLogger(log_name).setLevel(logging.WARNING)


@click.group(context_settings=dict(auto_envvar_prefix="EMM", max_content_width=100))
@click.option(
    "--modules-dir",
    default=DEFAULT_MODULES_PATH,
    type=click.Path(),
    help=f"Directory to store module repositories [default='{DEFAULT_MODULES_PATH}']",
)
@click.option(
    "--evg-config-file",
    default=DEFAULT_EVG_CONFIG,
    type=click.Path(exists=True),
    help=f"Path to file with evergreen auth configuration [default='{DEFAULT_EVG_CONFIG}']",
)
@click.option(
    "--evg-project",
    default=DEFAULT_EVG_PROJECT,
    help=f"Name of Evergreen project [default='{DEFAULT_EVG_PROJECT}']",
)
@click.pass_context
def cli(ctx: click.Context, modules_dir: str, evg_config_file: str, evg_project: str) -> None:
    """Evergreen Module Manager is a tool help simplify the local workflows of evergreen modules."""
    ctx.ensure_object(EmmOptions)
    ctx.obj.modules_directory = Path(modules_dir)
    ctx.obj.evg_config = Path(evg_config_file)
    ctx.obj.evg_project = evg_project

    configure_logging(False)

    evg_config_file = os.path.expanduser(evg_config_file)
    evg_api = RetryingEvergreenApi.get_api(config_file=evg_config_file)

    def dependencies(binder: inject.Binder) -> None:
        binder.bind(EvergreenApi, evg_api)
        binder.bind(EmmOptions, ctx.obj)

    inject.configure(dependencies)


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
@click.option("-m", "--module", required=True, help="Name of module to enable.")
@click.option(
    "--sync-commit/--no-sync-commit",
    default=True,
    help="When true, checkout the commit associated with the base repo in evergreen.",
)
def enable(ctx: click.Context, module: str, sync_commit: bool) -> None:
    """
    Enable the specified module in the current repo.

    If the module does not exist locally, it will be cloned.
    """
    orchestrator = EmmOrchestrator()
    orchestrator.enable(module, sync_commit)


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
@click.option("-m", "--module", required=True, help="Name of module to enable.")
def disable(ctx: click.Context, module: str) -> None:
    """Disable the specified module in the current repo."""
    orchestrator = EmmOrchestrator()
    orchestrator.disable(module)


@cli.command(
    context_settings=dict(max_content_width=100, ignore_unknown_options=True, allow_extra_args=True)
)
@click.pass_context
def patch(ctx: click.Context) -> None:
    """
    Create an Evergreen patch with changes from the base repo and any enabled modules.

    Any options passed to this command was be forwarded to the `evergreen patch` command. However,
    the following options are already included and should not be added:

    * --skip_confirm, --yes, -y
    * --project, -p
    """
    orchestrator = EmmOrchestrator()
    orchestrator.submit_patch(ctx.args)


@cli.command(
    context_settings=dict(max_content_width=100, ignore_unknown_options=True, allow_extra_args=True)
)
@click.pass_context
def commit_queue(ctx: click.Context) -> None:
    """
    Submit changes from the base repository and any enabled modules to the Evergreen commit queue.

    Any enabled modules with changes with be submitted to the commit queue along with changes
    to the base repository.

    Any options passed to this command was be forwarded to the `evergreen patch` command. However,
    the following options are already included and should not be added:

    * --skip_confirm, --yes, -y
    * --project, -p
    """
    orchestrator = EmmOrchestrator()
    orchestrator.submit_cq_patch(ctx.args)


@cli.command(context_settings=dict(max_content_width=100))
@click.option("--enabled", is_flag=True, default=False, help="Only list enabled modules.")
@click.option("--show-details", is_flag=True, default=False, help="Show details about modules.")
@click.pass_context
def list_modules(ctx: click.Context, enabled: bool, show_details: bool) -> None:
    """List the modules available for the current repo."""
    orchestrator = EmmOrchestrator()
    orchestrator.display_modules(enabled, show_details)


@cli.command(context_settings=dict(max_content_width=100))
@click.option("-b", "--branch", default=None, help="Name of branch for git checkout.")
@click.option("-r", "--revision", default="HEAD", help="Revision to be checked out.")
@click.pass_context
def create_branch(ctx: click.Context, revision: str, branch: str) -> None:
    """Perform git checkout operation to create the branch."""
    orchestrator = EmmOrchestrator()
    orchestrator.git_operate_base(revision, GitAction.CHECKOUT, branch)


@cli.command(context_settings=dict(max_content_width=100))
@click.option(
    "-o",
    "--operation",
    type=click.Choice([GitAction.MERGE, GitAction.REBASE]),
    default=GitAction.MERGE,
    help="Git operations to perform with the given revision[default=merge].",
)
@click.option("-r", "--revision", required=True, help="Revision to be updated the branch from.")
@click.pass_context
def update_branch(ctx: click.Context, revision: str, operation: GitAction) -> None:
    """Perform git merge|rebase operation to update the branch."""
    orchestrator = EmmOrchestrator()
    orchestrator.git_operate_base(revision, operation, None)


@cli.command(context_settings=dict(max_content_width=100))
@click.option("-m", "--commit-message", required=True, help="Commit message to apply.")
@click.pass_context
def git_commit(ctx: click.Context, commit_message: str) -> None:
    """
    Create a git commit of changes in each module.

    Any enabled modules with git tracked changes will be committed with the commit message
    along with changes to the base repository.

    The following options are already included in the git commit command:
    * --all, -a
    * --message, -m
    """
    orchestrator = EmmOrchestrator()
    orchestrator.git_commit_modules(commit_message)


@cli.command(
    context_settings=dict(max_content_width=100, ignore_unknown_options=True, allow_extra_args=True)
)
@click.pass_context
def pull_request(ctx: click.Context) -> None:
    """
    Create pull request for the changes in each module.

    Before use this command, you have to authenticate to github by 'gh auth login'.

    Any enabled modules with committed changes would create a pull request,
    each pull request would contain links of other modules' pull request as comment.

    Use --title and --body to create a pull request or use --fill autofill these values from git commits.:
    * -t, --title <string> Title for the pull request
    * -b, --body <string> Body for the pull request
    * -f, --fill Do not prompt for title/body and just use commit info


    Other options will be passed to github CLI and processed, the documentation is
    in following link:
       https://cli.github.com/manual/gh_pr_create
    """
    orchestrator = EmmOrchestrator()
    orchestrator.git_pull_request(ctx.args)


if __name__ == "__main__":
    cli(obj=EmmOptions(), auto_envvar_prefix="EMM")
