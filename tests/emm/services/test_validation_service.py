"""Unit tests for validation_service.py."""

from unittest.mock import MagicMock, patch

import pytest
from click import UsageError

import emm.services.validation_service as under_test
from emm.services.file_service import FileService

NAMESPACE = "emm.services.validation_service"


def ns(local_path: str) -> str:
    return f"{NAMESPACE}.{local_path}"


@pytest.fixture()
def file_service():
    file_service = MagicMock(spec_set=FileService)
    return file_service


@pytest.fixture()
def validation_service(file_service):
    validation_service = under_test.ValidationService(file_service)
    return validation_service


class TestValidateGitCommand:
    def test_validate_should_raise_exception_if_command_is_missing(
        self, validation_service, file_service
    ):
        file_service.which.return_value = None

        with pytest.raises(UsageError):
            validation_service.validate_git_command()

        file_service.which.assert_called_with("git")

    def test_validate_should_not_raise_exception_if_command_is_found(
        self, validation_service, file_service
    ):
        file_service.which.return_value = "/usr/bin/git"

        validation_service.validate_git_command()

        file_service.which.assert_called_with("git")


class TestValidateGhCommand:
    def test_validate_should_raise_exception_if_command_is_missing(
        self, validation_service, file_service
    ):
        file_service.which.return_value = None

        with pytest.raises(UsageError):
            validation_service.validate_gh_command()

        file_service.which.assert_called_with("gh")

    def test_validate_should_not_raise_exception_if_command_is_found(
        self, validation_service, file_service
    ):
        file_service.which.return_value = "/usr/bin/gh"

        validation_service.validate_gh_command()

        file_service.which.assert_called_with("gh")


class TestValidateEvergreenCommand:
    def test_validate_should_raise_exception_if_command_is_missing(
        self, validation_service, file_service
    ):
        file_service.which.return_value = None

        with pytest.raises(UsageError):
            validation_service.validate_evergreen_command()

        file_service.which.assert_called_with("evergreen")

    def test_validate_should_not_raise_exception_if_command_is_found(
        self, validation_service, file_service
    ):
        file_service.which.return_value = "/usr/bin/evergreen"

        validation_service.validate_evergreen_command()

        file_service.which.assert_called_with("evergreen")


class TestValidateGithubAuthentication:
    @patch(ns("_check_github_auth_status"))
    def test_validate_should_raise_exception_if_gh_is_not_authed(
        self, check_gh_auth_mock, validation_service
    ):
        check_gh_auth_mock.return_value = False

        with pytest.raises(UsageError):
            validation_service.validate_github_authentication()
            print()

    @patch(ns("_check_github_auth_status"))
    def test_validate_should_not_raise_exception_if_gh_is_authed(
        self, check_gh_auth_mock, validation_service
    ):
        check_gh_auth_mock.return_value = True

        validation_service.validate_github_authentication()


class TestValidateGithub:
    @patch(ns("_check_github_auth_status"))
    def test_validate_should_raise_exception_if_gh_is_not_authed(
        self, check_gh_auth_mock, validation_service, file_service
    ):
        file_service.which.return_value = "/usr/bin/gh"
        check_gh_auth_mock.return_value = False

        with pytest.raises(UsageError):
            validation_service.validate_github()

    @patch(ns("_check_github_auth_status"))
    def test_validate_should_not_raise_exception_if_gh_command_is_not_found(
        self, check_gh_auth_mock, validation_service, file_service
    ):
        file_service.which.return_value = None
        check_gh_auth_mock.return_value = True

        with pytest.raises(UsageError):
            validation_service.validate_github()

        file_service.which.assert_called_with("gh")

    @patch(ns("_check_github_auth_status"))
    def test_validate_should_not_raise_exception_if_gh_is_authed_and_gh_exists(
        self, check_gh_auth_mock, validation_service, file_service
    ):
        file_service.which.return_value = "/usr/bin/gh"
        check_gh_auth_mock.return_value = True

        validation_service.validate_github()
