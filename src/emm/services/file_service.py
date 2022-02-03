"""A service for working with files."""
from pathlib import Path
from shutil import which
from typing import Any, Dict, Optional

import yaml


class FileService:
    """A service for working with files."""

    @staticmethod
    def read_yaml_file(file_path: Path) -> Dict[str, Any]:
        """
        Read the given yaml file into a dictionary.

        :param file_path: Path to yaml file to read.
        :return: Dictionary of yaml contents.
        """
        with open(file_path) as file_contents:
            return yaml.safe_load(file_contents)

    @staticmethod
    def write_yaml_file(file_path: Path, contents: Dict[str, Any]) -> None:
        """Write the given contents to the specified file."""
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as file_contents:
            yaml.safe_dump(contents, file_contents)

    @staticmethod
    def path_exists(path: Path) -> bool:
        """Determine if the given path exists."""
        return path.exists()

    @staticmethod
    def create_symlink(target: Path, source: Path) -> None:
        """Create a symlink."""
        target.symlink_to(source)

    @staticmethod
    def rm_symlink(target: Path) -> None:
        """Delete the specified symlink."""
        target.unlink()

    @staticmethod
    def mkdirs(target: Path) -> None:
        """Create directories for path if they don't exist."""
        target.mkdir(parents=True)

    @staticmethod
    def which(cmd: str) -> Optional[str]:
        """Find the path to the given command, if it exists."""
        return which(cmd)
