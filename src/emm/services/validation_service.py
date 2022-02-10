"""Service to validate command prerequisites."""

import inject
from click import UsageError
from plumbum import local

from emm.services.file_service import FileService

DOCUMENTATION_LINK = (
    "https://github.com/evergreen-ci/evg-module-manager/blob/main/docs/usage.md#prerequisites"
)


class ValidationService:
    """A service to validate command prerequites."""

    @inject.autoparams()
    def __init__(self, file_service: FileService) -> None:
        """Initialize the service."""
        self.file_service = file_service

    def validate_git_command(self) -> None:
        """Check that git command exists."""
        if self.file_service.which("git") is None:
            raise UsageError(
                "Cannot find 'git' command. Please ensure git is installed. "
                f"See {DOCUMENTATION_LINK} for more information."
            )

    def validate_gh_command(self) -> None:
        """Check that the gh command exists."""
        if self.file_service.which("gh") is None:
            raise UsageError(
                "Cannot find 'gh' command. Pease ensure the github client is installed. "
                f"See {DOCUMENTATION_LINK} for more information."
            )

    def validate_evergreen_command(self) -> None:
        """Check that the evergreen command exists."""
        if self.file_service.which("evergreen") is None:
            raise UsageError(
                "Cannot find 'evergreen' command. Pease ensure the evergreen cli is "
                f"installed. See {DOCUMENTATION_LINK} for more information."
            )

    def validate_github(self) -> None:
        """Validate github CLI is installed and configured."""
        self.validate_gh_command()
        self.validate_github_authentication()

    def validate_github_authentication(self) -> None:
        """Check if github CLI already authenticated."""
        result = _check_github_auth_status()
        if not result:
            raise UsageError(
                f"Not authenticated to github. See {DOCUMENTATION_LINK} for more information."
            )


def _check_github_auth_status() -> bool:
    """Check the authentication status of the gh CLI."""
    args = ["auth", "status"]
    return local.cmd.gh[args]
