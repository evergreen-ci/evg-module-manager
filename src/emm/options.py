"""Configuration options for evg-module-manager."""
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODULES_PATH = ".."
DEFAULT_EVG_CONFIG = os.path.expanduser("~/.evergreen.yml")
DEFAULT_EVG_PROJECT = "mongodb-mongo-master"
DEFAULT_EVG_PROJECT_CONFIG = "etc/evergreen.yml"


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
