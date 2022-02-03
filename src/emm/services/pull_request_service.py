"""Service for creating pull requests."""


from pathlib import Path
from typing import List, NamedTuple, Optional

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
                directory=Path(module.prefix),
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

        # Push changes to origin.
        for repo in changed_repos:
            self.git_service.push_branch_to_remote(repo.directory)

        # Create the PRs
        pr_arguments = self.create_pr_arguments(title, body)
        pr_links = {
            repo.name: PullRequest(
                name=repo.name,
                link=self.github_service.pull_request(pr_arguments, directory=repo.directory),
            )
            for repo in changed_repos
        }

        # Annotate the PRs with links
        if len(changed_repos) > 1:
            # We only want to add comments linking PR if there is more than 1 PR.
            for repo in changed_repos:
                pr_link = pr_links[repo.name]
                self.github_service.pr_comment(
                    pr_link.link,
                    self.create_comment(list(pr_links.values()), repo.name),
                    repo.directory,
                )

        return list(pr_links.values())

    def create_comment(self, pr_list: List[PullRequest], name: str) -> str:
        """
        Create a comment for a PR that describes where to find associated PRs.

        :param pr_list: List of PRs being created.
        :param name: Name of repository comment is for.
        :return: Comment to add to PR for given repository.
        """
        pr_links = "\n".join([pr.pr_comment() for pr in pr_list if pr.name != name])
        return f"{PR_PREFIX}\n{pr_links}"

    def create_pr_arguments(self, title: Optional[str], body: Optional[str]) -> List[str]:
        """
        Determine the arguments to pass to the gh cli command.

        :param title: Title for pull request.
        :param body: Body for pull request.
        :return: List of arguments to pass to gh cli command.
        """
        if title is None and body is None:
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
