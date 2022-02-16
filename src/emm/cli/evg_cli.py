"""CLI interfaces for evergreen actions."""

from typing import List

import click
import inject

from emm.services.patch_service import PatchService
from emm.services.validation_service import ValidationService


class EvgOrchestrator:
    """Orchestrator for evergreen related commands."""

    @inject.autoparams()
    def __init__(self, patch_service: PatchService) -> None:
        """
        Initialize the service.

        :param patch_service: Service used to interact with patches.
        """
        self.patch_service = patch_service

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


@click.group(name="evg")
def evg_cli() -> None:
    """Perform evergreen actions against the base repo and enabled modules."""
    pass


@evg_cli.command(
    context_settings=dict(max_content_width=100, ignore_unknown_options=True, allow_extra_args=True)
)
@click.pass_context
def patch(ctx: click.Context) -> None:
    """
    Create an Evergreen patch with changes from the base repo and any enabled modules.

    Any options passed to this command was be forwarded to the `evergreen patch` command. However,
    the following options are already included and should not be added:

    \b
    * --skip_confirm, --yes, -y
    * --project, -p
    """
    validation_service = inject.instance(ValidationService)
    validation_service.validate_evergreen_command()
    orchestrator = inject.instance(EvgOrchestrator)
    orchestrator.submit_patch(ctx.args)


@evg_cli.command(
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

    \b
    * --skip_confirm, --yes, -y
    * --project, -p
    """
    validation_service = inject.instance(ValidationService)
    validation_service.validate_evergreen_command()
    orchestrator = inject.instance(EvgOrchestrator)
    orchestrator.submit_cq_patch(ctx.args)
