"""Service for creating pull requests."""
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

import inject

from emm.options import EmmOptions
from emm.services.evg_service import EvgService
from emm.services.git_service import LOGGER, GitService
from emm.services.github_service import GithubService
from emm.services.modules_service import ModulesService

BASE_REPO = "base"
PR_PREFIX = (
    "This code review is spread across multiple repositories. Here are the other "
    "Pull Requests associated with the code review:"
)


class PullRequest(NamedTuple):
    """
    Information about a created pull request.

    * name: The name to label with PR with.
    * url: URL to pull request in github.
    """

    name: str
    link: str

    def pr_comment(self) -> str:
        """Create a PR comment pointing to this PR."""
        return f"* [{self.name}]({self.link})"


class Repository(NamedTuple):
    """
    Information about a repository.

    * name: Name of the repository.
    * directory: Path to the location of the repository.
    * target_branch: Branch that a PR should be created against.
    """

    name: str
    directory: Optional[Path]
    target_branch: str


class PullRequestService:
    """A service for creating pull requests."""

    @inject.autoparams()
    def __init__(
        self,
        git_service: GitService,
        github_service: GithubService,
        modules_service: ModulesService,
        evg_service: EvgService,
        emm_options: EmmOptions,
    ) -> None:
        """
        Initialize the service.

        :param git_service: Service to interact with git.
        :param github_service: Service to interact with github.
        :param modules_service: Service to work with modules.
        :param evg_service: Service to interace with evergreen.
        :param emm_options: Command options.
        """
        self.git_service = git_service
        self.github_service = github_service
        self.modules_service = modules_service
        self.evg_service = evg_service
        self.emm_options = emm_options

    def collect_repositories(self) -> List[Repository]:
        """
        Create a list of potential repositories for PRs.

        :param project_id: Evergreen Project ID of base repository.
        :return: List of repositories associated the base repository.
        """
        enabled_modules = self.modules_service.get_all_modules(enabled=True)
        repository_list = [
            Repository(
                name=module.name,
                directory=Path(module.prefix) / module.name,
                target_branch=module.branch,
            )
            for module in enabled_modules.values()
        ]
        evg_project_id = self.emm_options.evg_project
        repository_list.append(
            Repository(
                name=BASE_REPO,
                directory=None,
                target_branch=self.evg_service.get_project_branch(evg_project_id),
            )
        )
        return repository_list

    def create_pull_request(self, title: Optional[str], body: Optional[str]) -> List[PullRequest]:
        """
        Create pull request for any repos with changes.

        :param args: Arguments to pass to the github CLi.
        :return: List of pull requests being created associate with its link.
        """
        repositories = self.collect_repositories()
        changed_repos = [repo for repo in repositories if self.repo_has_changes(repo)]

        self.push_changes_to_origin(changed_repos)
        pr_arguments = self.create_pr_arguments(title, body)
        pr_links = self.create_prs(changed_repos, pr_arguments)
        self.annotate_prs(changed_repos, pr_links)

        return list(pr_links.values())

    def push_changes_to_origin(self, changed_repos: List[Repository]) -> None:
        """
        Push changes in the given repositories to their origin.

        :param changed_repos: List of repos to push.
        """
        for repo in changed_repos:
            self.git_service.push_branch_to_remote(repo.directory)

    def create_prs(
        self, changed_repos: List[Repository], pr_args: List[str]
    ) -> Dict[str, PullRequest]:
        """
        Create PRs for the given repositories.

        :param changed_repos: List of repositories with changes to PR.
        :param pr_args: Arguments to use to create the PRs.
        :return: Dictionary of the repo name and the PR info.
        """
        return {
            repo.name: PullRequest(
                name=repo.name,
                link=self.github_service.pull_request(pr_args, directory=repo.directory),
            )
            for repo in changed_repos
        }

    def annotate_prs(
        self, changed_repos: List[Repository], pr_links: Dict[str, PullRequest]
    ) -> None:
        """
        Annotate the given PRs with links to the other PRs.

        :param changed_repos: List of repos with PR requests.
        :param pr_links: Dictionary of repo name and PR info.
        """
        if len(changed_repos) > 1:
            # We only want to add comments linking PR if there is more than 1 PR.
            for repo in changed_repos:
                pr_link = pr_links[repo.name]
                self.github_service.pr_comment(
                    pr_link.link,
                    self.create_comment(list(pr_links.values()), repo.name),
                    repo.directory,
                )

    @staticmethod
    def create_comment(pr_list: List[PullRequest], name: str) -> str:
        """
        Create a comment for a PR that describes where to find associated PRs.

        :param pr_list: List of PRs being created.
        :param name: Name of repository comment is for.
        :return: Comment to add to PR for given repository.
        """
        pr_links = "\n".join([pr.pr_comment() for pr in pr_list if pr.name != name])
        return f"{PR_PREFIX}\n{pr_links}"

    @staticmethod
    def create_pr_arguments(title: Optional[str], body: Optional[str]) -> List[str]:
        """
        Determine the arguments to pass to the gh cli command.

        :param title: Title for pull request.
        :param body: Body for pull request.
        :return: List of arguments to pass to gh cli command.
        """
        if title is None:
            return ["--fill"]

        if body is None:
            body = "''"

        return ["--title", title, "--body", body]

    def repo_has_changes(self, repo: Repository) -> bool:
        """Check if the given repository has changes that would indicate a PR should be made."""
        if not self.git_service.check_changes(repo.target_branch, repo.directory):
            LOGGER.debug(
                "No changes found for module", module=repo.name, target_branch=repo.target_branch
            )
            return False

        return True
