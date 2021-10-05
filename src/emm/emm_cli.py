"""Command line entry point to application."""
import logging
import os.path
import sys
from dataclasses import dataclass
from pathlib import Path

import click
import inject
import structlog
from evergreen import EvergreenApi, RetryingEvergreenApi
from structlog.stdlib import LoggerFactory

LOGGER = structlog.get_logger(__name__)

DEFAULT_MODULES_PATH = ".."
DEFAULT_EVG_CONFIG = os.path.expanduser("~/.evergreen.yml")
DEFAULT_EVG_PROJECT = "mongodb-mongo-master"
DEFAULT_EVG_PROJECT_CONFIG = "etc/evergreen.yml"
EXTERNAL_LOGGERS = [
    "evergreen",
    "inject",
    "urllib3",
]


@dataclass
class EmmOptions:
    """
    Options for running the script.

    * modules_directory: Directory to clone modules into.
    * evg_config: Path to evergreen API configuration.
    * evg_project: Evergreen project of base repository.
    """

    modules_directory: Path = Path(DEFAULT_MODULES_PATH)
    evg_config: Path = Path(DEFAULT_EVG_CONFIG)
    evg_project: str = DEFAULT_EVG_PROJECT


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


@click.group()
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
    """ """
    ctx.ensure_object(EmmOptions)
    ctx.obj.modules_dir = modules_dir
    ctx.obj.evg_config = Path(evg_config_file)
    ctx.obj.evg_project = evg_project

    configure_logging(False)

    evg_config_file = os.path.expanduser(evg_config_file)
    evg_api = RetryingEvergreenApi.get_api(config_file=evg_config_file)

    def dependencies(binder: inject.Binder) -> None:
        binder.bind(EvergreenApi, evg_api)

    inject.configure(dependencies)


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
@click.option("-m", "--module", required=True, help="Name of module to enable.")
def enable(ctx: click.Context, module: str) -> None:
    """
    Enable the specified module in the current repo.
    """
    raise NotImplementedError()


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
@click.option("-m", "--module", required=True, help="Name of module to enable.")
def disable(ctx: click.Context, module: str) -> None:
    """
    Disable the specified module in the current repo.
    """
    raise NotImplementedError()


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
def patch(ctx: click.Context) -> None:
    """
    Create an Evergreen patch with changes from the base repo and any enabled modules.
    """
    raise NotImplementedError()


@cli.command(context_settings=dict(max_content_width=100))
@click.pass_context
def commit_queue(ctx: click.Context) -> None:
    """
    Submit changes from the base repository and any enabled modules to the Evergreen commit queue.
    """
    raise NotImplementedError()


if __name__ == "__main__":
    cli(obj=EmmOptions())
