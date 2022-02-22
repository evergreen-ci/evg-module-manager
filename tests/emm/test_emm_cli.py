"""Unit tests for emm_cli.py."""

from unittest.mock import MagicMock, patch

import emm.emm_cli as under_test
from emm.options import EmmConfiguration


class TestGenerateConfiguration:
    @patch("emm.emm_cli.Path")
    def test_command_line_options_should_be_used_when_no_local_file(self, path_mock):
        path_mock.return_value.exists.return_value = False
        mock_ctx = MagicMock()

        under_test.generate_configuration(mock_ctx, "evergreen.yml", "modules_dir", "evg-project")

        assert mock_ctx.obj.evg_project == "evg-project"

    @patch("emm.emm_cli.Path")
    @patch("emm.emm_cli.EmmConfiguration.from_yaml_file")
    def test_local_file_options_should_be_used_when_local_file_exists(
        self, emm_config_mock, path_mock
    ):
        path_mock.return_value.exists.return_value = True
        mock_ctx = MagicMock()

        emm_config_mock.return_value = EmmConfiguration(
            evg_project="evg-project-from-yml",
            modules_directory=None,
        )

        under_test.generate_configuration(mock_ctx, "evergreen.yml", "modules_dir", "evg-project")

        assert mock_ctx.obj.evg_project == "evg-project-from-yml"
