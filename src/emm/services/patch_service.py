"""A service for working with patches."""
from pathlib import Path
from typing import List

import inject

from emm.clients.evg_cli_service import EvgCliService, PatchInfo
from emm.clients.evg_service import EvgService
from emm.options import EmmOptions
from emm.services.file_service import FileService


class PatchService:
    """A service for working with patches."""

    @inject.autoparams()
    def __init__(
        self,
        file_service: FileService,
        evg_cli_service: EvgCliService,
        evg_service: EvgService,
        emm_options: EmmOptions,
    ) -> None:
        """
        Initialize the service.

        :param file_service: Service for working with files.
        :param evg_cli_service: Service for working with the evergreen CLI.
        :param evg_service: Service for working with evergreen.
        :param emm_options: Optional about the command.
        """
        self.file_service = file_service
        self.evg_cli_service = evg_cli_service
        self.evg_service = evg_service
        self.emm_options = emm_options

    def create_patch(self, extra_args: List[str]) -> PatchInfo:
        """
        Create an evergreen patch and add any modules to it.

        :param extra_args: Extra arguments to pass to the patch command.
        """
        modules_data = self.evg_service.get_module_map(self.emm_options.evg_project)
        base_patch = self.evg_cli_service.create_patch(extra_args)
        for module, module_data in modules_data.items():
            module_location = Path(module_data.prefix) / module
            if self.file_service.path_exists(module_location):
                self.evg_cli_service.add_module_to_patch(
                    base_patch.patch_id, module, module_location, extra_args
                )

        return base_patch

    def create_cq_patch(self, extra_args: List[str]) -> PatchInfo:
        """
        Create an evergreen commit-queue patch.

        :param extra_args: Extra arguments to pass to the patch command.
        """
        modules_data = self.evg_service.get_module_map(self.emm_options.evg_project)
        base_patch = self.evg_cli_service.create_cq_patch(extra_args)
        for module, module_data in modules_data.items():
            module_location = Path(module_data.prefix) / module
            if self.file_service.path_exists(module_location):
                self.evg_cli_service.add_module_to_cq_patch(
                    base_patch.patch_id, module, module_location, extra_args
                )

        self.evg_cli_service.finalize_cq_patch(base_patch.patch_id)
        return base_patch
