"""Unit tests for git_branch_service.py."""

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

import emm.services.git_branch_service as under_test
from emm.clients.git_proxy import GitProxy
from emm.models.repository import Repository
from emm.services.modules_service import ModulesService, UpdateStrategy


@pytest.fixture()
def modules_service():
    modules_service = MagicMock(spec_set=ModulesService)
    return modules_service


@pytest.fixture()
def git_proxy():
    git_proxy = MagicMock(spec_set=GitProxy)
    return git_proxy


@pytest.fixture()
def git_branch_service(modules_service, git_proxy):
    git_branch_service = under_test.GitBranchService(modules_service, git_proxy)
    return git_branch_service


def build_mock_repository(index: int, directory: Optional[Path] = None):
    return Repository(
        name=f"repo_name_{index}",
        directory=directory,
        target_branch=f"target_branch_{index}",
    )


class TestCreateBranch:
    def test_branch_creation_should_happen_in_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        repos = git_branch_service.create_branch("my-branch", "HEAD")

        assert len(repos) == len(module_list)
        assert git_proxy.checkout.call_count == len(module_list) + 1
        modules_service.sync_all_modules.assert_called_once()
        for module in module_list:
            assert module.name in repos


class TestBranchList:
    def test_branch_list_should_happen_in_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        repos = git_branch_service.branch_list()

        assert len(repos) == len(module_list)
        assert git_proxy.branch.call_count == len(module_list)
        for repo in repos:
            assert repo.module_name in [module.name for module in module_list]
            assert repo.output == git_proxy.branch.return_value


class TestSwitchBranch:
    def test_branch_switch_should_happen_in_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        repos = git_branch_service.switch_branch("my-branch")

        assert len(repos) == len(module_list)
        assert git_proxy.checkout.call_count == len(module_list)
        for module in module_list:
            assert module.name in repos


class TestDeleteBranch:
    def test_branch_delete_should_happen_in_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        module_list = [build_mock_repository(i, Path(f"/path/to/module_{i}")) for i in range(3)]
        modules_service.collect_repositories.return_value = module_list

        repos = git_branch_service.delete_branch("my-branch")

        assert len(repos) == len(module_list)
        assert git_proxy.branch.call_count == len(module_list)
        for module in module_list:
            assert module.name in repos


class TestUpdateBranch:
    def test_update_branch_should_update_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        n_modules = 3
        modules = {f"module_{i}": f"revision_{i}" for i in range(n_modules)}
        repos = [build_mock_repository(i) for i in range(n_modules)]
        modules_service.sync_all_modules.return_value = modules
        modules_service.collect_repositories.return_value = repos

        result = git_branch_service.update_branch(branch="master", rebase=False)

        assert len(result) == len(modules)
        assert len(modules) == git_proxy.fetch.call_count
        git_proxy.merge.assert_called_with("master")
        modules_service.sync_all_modules.assert_called_with(
            enabled=True, update_strategy=UpdateStrategy.MERGE
        )

    def test_update_branch_with_rebase_should_rebase_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        n_modules = 3
        modules = {f"module_{i}": f"revision_{i}" for i in range(n_modules)}
        repos = [build_mock_repository(i) for i in range(n_modules)]
        modules_service.sync_all_modules.return_value = modules
        modules_service.collect_repositories.return_value = repos

        result = git_branch_service.update_branch(branch="master", rebase=True)

        assert len(result) == len(modules)
        assert len(modules) == git_proxy.fetch.call_count
        git_proxy.rebase.assert_called_with("master")
        modules_service.sync_all_modules.assert_called_with(
            enabled=True, update_strategy=UpdateStrategy.REBASE
        )


class TestPull:
    def test_pull_should_pull_and_sync_all_modules(
        self,
        git_branch_service: under_test.GitBranchService,
        modules_service: ModulesService,
        git_proxy: GitProxy,
    ):
        modules = {f"module_{i}": f"revision_{i}" for i in range(3)}
        modules_service.sync_all_modules.return_value = modules

        result = git_branch_service.pull(False)

        assert len(result) == len(modules)
        git_proxy.pull.assert_called()
        modules_service.sync_all_modules.assert_called()
