"""Command line entry point to application."""
import logging
import os.path
import sys
from functools import partial
from pathlib import Path
from typing import Optional

import click
import inject
import structlog
from evergreen import EvergreenApi, RetryingEvergreenApi
from structlog.stdlib import LoggerFactory

from emm.cli.evg_cli import evg_cli
from emm.cli.git_cli import git_cli
from emm.clients.evg_cli_service import EvgCliService
from emm.clients.git_proxy import GitProxy
from emm.clients.github_service import GithubService
from emm.options import DEFAULT_EVG_CONFIG, DEFAULT_EVG_PROJECT, DEFAULT_MODULES_PATH, EmmOptions
from emm.services.modules_service import ModulesService
from emm.services.patch_service import PatchService
from emm.services.pull_request_service import PullRequestService
from emm.services.validation_service import ValidationService

LOGGER = structlog.get_logger(__name__)

EXTERNAL_LOGGERS = [
    "evergreen",
    "inject",
    "urllib3",
]


class EmmOrchestrator:
    """An orchestrator for evg-module-manager."""

    @inject.autoparams()
    def __init__(
        self,
        modules_service: ModulesService,
        patch_service: PatchService,
        pull_request_service: PullRequestService,
    ) -> None:
        """
        Initialize the orchestrator.

        :param modules_service: Service for working with modules.
        :param patch_service: Service for creating patches.
        :param pull_request_service: Service for creating pull requests.
        """
        self.modules_service = modules_service
        self.patch_service = patch_service
        self.pull_request_service = pull_request_service

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

    def create_pull_request(self, title: Optional[str], body: Optional[str]) -> None:
        """
        Create pull requests in any repositories that contain changes.

        :param title: Title for the pull request.
        :param body: Body for the pull request.
        """
        created_pull_requests = self.pull_request_service.create_pull_request(title, body)
        print("Created the following pull requests:")
        for pr in created_pull_requests:
            print(f"- {pr.name}: {pr.link}")


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
        binder.bind_to_constructor(GithubService, GithubService.create)
        binder.bind_to_constructor(GitProxy, GitProxy.create)
        binder.bind_to_constructor(EvgCliService, partial(EvgCliService.create, ctx.obj))

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
    orchestrator = inject.instance(EmmOrchestrator)
    orchestrator.enable(module, sync_commit)


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
@click.option("-m", "--module", required=True, help="Name of module to enable.")
def disable(ctx: click.Context, module: str) -> None:
    """Disable the specified module in the current repo."""
    orchestrator = inject.instance(EmmOrchestrator)
    orchestrator.disable(module)


@cli.command(context_settings=dict(max_content_width=100))
@click.option("--enabled", is_flag=True, default=False, help="Only list enabled modules.")
@click.option("--show-details", is_flag=True, default=False, help="Show details about modules.")
@click.pass_context
def list_modules(ctx: click.Context, enabled: bool, show_details: bool) -> None:
    """List the modules available for the current repo."""
    orchestrator = inject.instance(EmmOrchestrator)
    orchestrator.display_modules(enabled, show_details)


@cli.command(context_settings=dict(max_content_width=100))
@click.option("--title", help="Title for the pull request.")
@click.option("--body", help="Body for the pull request")
@click.pass_context
def pull_request(ctx: click.Context, title: Optional[str], body: Optional[str]) -> None:
    """
    Create a Github pull request for changes in the base repository and any enabled modules.

    NOTE: Before using this command, you have to authenticate to github by 'gh auth login'.

    A pull request will be created for the base repository and any enabled modules that contain
    changes. Additionally, a comment will be added to each pull request with links to the other
    pull requests.

    By default, the commit info will be used to fill out the title and body of the pull request,
    however, the `--title` and `--body` options can be used to customize these.
    """
    validation_service = inject.instance(ValidationService)
    validation_service.validate_github()

    if title is None and body is not None:
        raise click.UsageError(
            "Cannot create a PR with an empty title, "
            "please provide a title with the `--title` option."
        )

    orchestrator = inject.instance(EmmOrchestrator)
    orchestrator.create_pull_request(title, body)


cli.add_command(evg_cli)
cli.add_command(git_cli)


if __name__ == "__main__":
    cli(obj=EmmOptions(), auto_envvar_prefix="EMM")
