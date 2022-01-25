"""Service for working with the evergreen CLI."""
import re
from pathlib import Path
from typing import List, NamedTuple

import inject
from plumbum import local

from emm.options import EmmOptions

PATCH_ID_RE = re.compile(r"ID\s:\s(?P<patch_id>\S+)$", flags=re.MULTILINE)
BUILD_URL_RE = re.compile(r"Build\s:\s(?P<build_url>\S+)$", flags=re.MULTILINE)


class PatchInfo(NamedTuple):
    """
    Information about a created patch.

    * patch_id: Id of created patch.
    * patch_url: URL to patch in the evergreen UI.
    """

    patch_id: str
    patch_url: str


class EvgCliService:
    """A service for interacting with the Evergreen CLI."""

    @inject.autoparams()
    def __init__(self, emm_options: EmmOptions) -> None:
        """
        Initialize the service.

        :param emm_options: Options about the command.
        """
        self.emm_options = emm_options
        self.evg_cli = local.cmd.evergreen

    def create_patch(self, extra_args: List[str]) -> PatchInfo:
        """
        Create a patch in evergreen.

        :param extra_args: Extra arguments to add to the patch command.
        :return: Details about the created patch.
        """
        args = ["patch", "--project", self.emm_options.evg_project, "--skip_confirm"]
        args.extend(extra_args)
        cmd_output = self.evg_cli[args]()
        patch_match = PATCH_ID_RE.search(cmd_output)
        build_url_match = BUILD_URL_RE.search(cmd_output)
        if not patch_match or not build_url_match:
            print(cmd_output)
            raise ValueError("Could not recognize output from 'evergreen patch'")

        return PatchInfo(
            patch_id=patch_match.group("patch_id"), patch_url=build_url_match.group("build_url")
        )

    def add_module_to_patch(
        self, patch_id: str, module: str, directory: Path, extra_args: List[str]
    ) -> None:
        """
        Add the specified module to the given patch.

        :param patch_id: ID of patch to add modules to.
        :param module: Name of modules to add.
        :param directory: Directory with the module changes.
        :param extra_args: Extra arguments that were passed to the patch command.
        """
        args = ["patch-set-module", "--module", module, "--patch", patch_id, "--skip_confirm"]
        if "-u" in extra_args or "--uncommitted" in extra_args:
            args.append("--uncommitted")
        if "--large" in extra_args:
            args.append("--large")
        if "--preserve-commits" in extra_args:
            args.append("--preserve-commits")
        with local.cwd(directory):
            self.evg_cli[args]()

    def finalize_patch(self, patch_id: str) -> None:
        """
        Mark the given patch as finalized.

        :param patch_id: ID of patch to finalize.
        """
        args = ["finalize-patch", "--id", patch_id]
        self.evg_cli[args]()

    def create_cq_patch(self, extra_args: List[str]) -> PatchInfo:
        """Create a commit-queue patch."""
        args = ["commit-queue", "merge", "--project", self.emm_options.evg_project, "--pause"]
        args.extend(extra_args)
        cmd_output = self.evg_cli[args]()
        patch_match = PATCH_ID_RE.search(cmd_output)
        build_url_match = BUILD_URL_RE.search(cmd_output)
        if not patch_match or not build_url_match:
            print(cmd_output)
            raise ValueError("Could not recognize output from 'evergreen commit-queue'")

        return PatchInfo(
            patch_id=patch_match.group("patch_id"), patch_url=build_url_match.group("build_url")
        )

    def add_module_to_cq_patch(
        self, patch_id: str, module: str, directory: Path, extra_args: List[str]
    ) -> None:
        """
        Add the specified module to the given commit-queue patch.

        :param patch_id: ID of patch to add modules to.
        :param module: Name of modules to add.
        :param directory: Directory with the module changes.
        :param extra_args: Extra args to pass to command.
        """
        args = [
            "commit-queue",
            "set-module",
            "--module",
            module,
            "--id",
            patch_id,
            "--skip_confirm",
        ]
        args.extend(extra_args)
        with local.cwd(directory):
            self.evg_cli[args]()

    def finalize_cq_patch(self, patch_id: str) -> None:
        """
        Mark the given commit-queue patch as finalized.

        :param patch_id: ID of patch to finalize.
        """
        # evergreen commit-queue merge --resume 5d3b120f1e2d1770d9f2104e
        args = ["commit-queue", "merge", "--resume", patch_id]
        self.evg_cli[args]()
