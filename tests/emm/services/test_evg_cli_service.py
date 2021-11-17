"""Unit tests for evg_cli_service.py."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import emm.services.evg_cli_service as under_test

NAMESPACE = "emm.services.evg_cli_service"


def ns(local_path: str) -> str:
    return f"{NAMESPACE}.{local_path}"


@pytest.fixture()
def emm_options():
    emm_options = MagicMock(evg_project="my-evergreen_dir-project")
    return emm_options


@pytest.fixture()
def evg_cli():
    evg_cli = MagicMock()
    return evg_cli


@pytest.fixture()
def evg_cli_service(emm_options, evg_cli):
    evg_cli_service = under_test.EvgCliService(emm_options)
    evg_cli_service.evg_cli = evg_cli
    return evg_cli_service


class TestCreatePatch:
    def test_create_patch_should_fail_on_bad_output(self, evg_cli_service, evg_cli):
        evg_cli.__getitem__.return_value.return_value = "invalid output"

        with pytest.raises(ValueError):
            evg_cli_service.create_patch([])

    def test_create_patch_should_return_patch_id_and_build_url(self, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
             ID : {patch_id}
        Created : 2021-10-06 00:28:57.034 +0000 UTC
    Description : test
          Build : {build_url}
         Status : created
        """

        patch_details = evg_cli_service.create_patch([])

        assert patch_details.patch_id == patch_id
        assert patch_details.patch_url == build_url

    def test_create_patch_should_use_evg_cli_to_create_patch_for_project(
        self, evg_cli_service, evg_cli, emm_options
    ):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
             ID : {patch_id}
        Created : 2021-10-06 00:28:57.034 +0000 UTC
    Description : test
          Build : {build_url}
         Status : created
        """

        evg_cli_service.create_patch([])

        evg_cli.__getitem__.assert_called_with(
            ["patch", "--project", emm_options.evg_project, "--skip_confirm"]
        )

    def test_create_patch_should_include_extra_args(self, evg_cli_service, evg_cli, emm_options):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
                 ID : {patch_id}
            Created : 2021-10-06 00:28:57.034 +0000 UTC
        Description : test
              Build : {build_url}
             Status : created
            """
        extra_args = ["-u", "-d", "hello world"]

        evg_cli_service.create_patch(extra_args)

        evg_cli.__getitem__.assert_called_with(
            [
                "patch",
                "--project",
                emm_options.evg_project,
                "--skip_confirm",
                "-u",
                "-d",
                "hello world",
            ]
        )


class TestAddModuleToPatch:
    @patch(ns("local.cwd"))
    def test_add_modules_should_call_out_to_evg_cli(self, cwd_patch, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"
        module = "my module"
        directory = Path("path/to/module")

        evg_cli_service.add_module_to_patch(patch_id, module, directory, [])

        evg_cli.__getitem__.assert_called_with(
            ["patch-set-module", "--module", module, "--patch", patch_id, "--skip_confirm"]
        )
        cwd_patch.assert_called_with(directory)

    @patch(ns("local.cwd"))
    def test_add_modules_should_include_extra_args(self, cwd_patch, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"
        module = "my module"
        directory = Path("path/to/module")
        extra_args = ["-u", "-d", "hello world", "--large", "--preserve-commits"]

        evg_cli_service.add_module_to_patch(patch_id, module, directory, extra_args)

        evg_cli.__getitem__.assert_called_with(
            [
                "patch-set-module",
                "--module",
                module,
                "--patch",
                patch_id,
                "--skip_confirm",
                "--uncommitted",
                "--large",
                "--preserve-commits",
            ]
        )
        cwd_patch.assert_called_with(directory)


class TestFinalizePatch:
    def test_finalize_patch_should_call_out_to_evg_cli(self, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"

        evg_cli_service.finalize_patch(patch_id)

        evg_cli.__getitem__.assert_called_with(["finalize-patch", "--id", patch_id])


class TestCreateCqPatch:
    def test_create_cq_patch_should_fail_on_bad_output(self, evg_cli_service, evg_cli):
        evg_cli.__getitem__.return_value.return_value = "invalid output"

        with pytest.raises(ValueError):
            evg_cli_service.create_cq_patch([])

    def test_create_cq_patch_should_return_patch_id_and_build_url(self, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
             ID : {patch_id}
        Created : 2021-10-06 00:28:57.034 +0000 UTC
    Description : test
          Build : {build_url}
         Status : created
        """

        patch_details = evg_cli_service.create_cq_patch([])

        assert patch_details.patch_id == patch_id
        assert patch_details.patch_url == build_url

    def test_create_cq_patch_should_use_evg_cli_to_create_patch_for_project(
        self, evg_cli_service, evg_cli, emm_options
    ):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
             ID : {patch_id}
        Created : 2021-10-06 00:28:57.034 +0000 UTC
    Description : test
          Build : {build_url}
         Status : created
        """

        evg_cli_service.create_cq_patch([])

        evg_cli.__getitem__.assert_called_with(
            ["commit-queue", "merge", "--project", emm_options.evg_project, "--pause"]
        )

    def test_create_cq_patch_should_use_use_extra_args_if_present(
        self, evg_cli_service, evg_cli, emm_options
    ):
        patch_id = "my_patch_id"
        build_url = "http://my.build/url.html"
        evg_cli.__getitem__.return_value.return_value = f"""
             ID : {patch_id}
        Created : 2021-10-06 00:28:57.034 +0000 UTC
    Description : test
          Build : {build_url}
         Status : created
        """

        evg_cli_service.create_cq_patch(["--large"])

        evg_cli.__getitem__.assert_called_with(
            ["commit-queue", "merge", "--project", emm_options.evg_project, "--pause", "--large"]
        )


class TestAddModuleToCqPatch:
    @patch(ns("local.cwd"))
    def test_add_modules_should_call_out_to_evg_cli(self, cwd_patch, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"
        module = "my module"
        directory = Path("path/to/module")

        evg_cli_service.add_module_to_cq_patch(patch_id, module, directory, [])

        evg_cli.__getitem__.assert_called_with(
            ["commit-queue", "set-module", "--module", module, "--id", patch_id, "--skip_confirm"]
        )
        cwd_patch.assert_called_with(directory)

    @patch(ns("local.cwd"))
    def test_add_modules_should_use_extra_args_if_present(
        self, cwd_patch, evg_cli_service, evg_cli
    ):
        patch_id = "my_patch_id"
        module = "my module"
        directory = Path("path/to/module")

        evg_cli_service.add_module_to_cq_patch(patch_id, module, directory, ["--large"])

        evg_cli.__getitem__.assert_called_with(
            [
                "commit-queue",
                "set-module",
                "--module",
                module,
                "--id",
                patch_id,
                "--skip_confirm",
                "--large",
            ]
        )
        cwd_patch.assert_called_with(directory)


class TestFinalizeCqPatch:
    def test_finalize_patch_should_call_out_to_evg_cli(self, evg_cli_service, evg_cli):
        patch_id = "my_patch_id"

        evg_cli_service.finalize_cq_patch(patch_id)

        evg_cli.__getitem__.assert_called_with(["commit-queue", "merge", "--resume", patch_id])
