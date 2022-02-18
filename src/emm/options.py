"""Configuration options for evg-module-manager."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

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


class EmmConfiguration(BaseModel):
    """
    Model for saving the EMM configuration.

    * evg_project: Evergreen project being executed against.
    * modules_directory: Directory to store repositories of modules.
    """

    evg_project: Optional[str]
    modules_directory: Optional[str]

    @classmethod
    def from_yaml_file(cls, filename: Path) -> EmmConfiguration:
        """
        Read the emm configuration from a yaml files.

        :param filename: File to read configuration from.
        :return: Model read from given file.
        """
        with open(filename) as f:
            return cls(**yaml.safe_load(f))

    def save_yaml_file(self, filename: Path) -> None:
        """
        Write the emm configuration to a yaml files.

        :param filename: File to write configuration to.
        """
        with open(filename, "w") as f:
            f.write(yaml.safe_dump(self.dict(exclude_none=True, exclude_unset=True)))
