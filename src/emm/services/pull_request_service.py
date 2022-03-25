"""Service for creating pull requests."""
from typing import Dict, List, NamedTuple, Optional

import inject

from emm.clients.evg_service import EvgService
from emm.clients.git_proxy import DEFAULT_REMOTE, LOGGER, GitProxy
from emm.clients.github_service import GithubService
from emm.models.repository import Repository
from emm.options import EmmOptions
from emm.services.modules_service import ModulesService

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


class PullRequestOption(NamedTuple):
    """
    Options for creating a pull request.

    * title: Title of the pull request.
    * branch: Remote branch of the pull request.
    * remote_url: URL to pull request in github.
    * body: Body of the pull request.
    """

    title: str
    body: str
    branch: str
    remote_url: str

    def option_list(self) -> List[str]:
        """Convert pull request arguements to arguement lists."""
        if self.remote_url == DEFAULT_REMOTE:
            return ["--title", self.title, "--body", self.body]

        return [
            "--title",
            self.title,
            "--body",
            self.body,
            "--head",
            self.branch,
            "--repo",
            self.remote_url,
        ]


class PullRequestService:
    """A service for creating pull requests."""

    @inject.autoparams()
    def __init__(
        self,
        git_service: GitProxy,
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

    def create_pull_request(
        self, title: Optional[str], body: Optional[str], remote: str
    ) -> List[PullRequest]:
        """
        Create pull request for any repos with changes.

        :param args: Arguments to pass to the github CLi.
        :return: List of pull requests being created associate with its link.
        """
        repositories = self.modules_service.collect_repositories()
        changed_repos = [repo for repo in repositories if self.repo_has_changes(repo)]
        remote_urls = self.determine_remote(remote, changed_repos)
        self.push_changes_to_remote(remote_urls, changed_repos)
        pr_arguments = self.combine_pr_arugments(title, body, remote_urls, changed_repos)
        pr_links = self.create_prs(changed_repos, pr_arguments)
        self.annotate_prs(changed_repos, pr_links)

        return list(pr_links.values())

    def determine_remote(self, remote: str, changed_repos: List[Repository]) -> List[str]:
        """
        Determine which remote to push.

        :param remote: The user specified remote.
        :param changed_repos: List of pull request arguments.
        """
        return [self.git_service.determine_remote(remote, repo.directory) for repo in changed_repos]

    def push_changes_to_remote(self, remotes: List[str], changed_repos: List[Repository]) -> None:
        """
        Push changes in the given repositories to their origin.

        :param remotes: List of remote url to push changes.
        :param changed_repos: List of repos to push.
        """
        for idx, repo in enumerate(changed_repos):
            self.git_service.push_branch_to_remote(remotes[idx], repo.directory)

    def create_prs(
        self, changed_repos: List[Repository], pr_args: List[List[str]]
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
                link=self.github_service.pull_request(pr_args[idx], directory=repo.directory),
            )
            for idx, repo in enumerate(changed_repos)
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

    def combine_pr_arugments(
        self,
        title: Optional[str],
        body: Optional[str],
        remotes: List[str],
        changed_repos: List[Repository],
    ) -> List[List[str]]:
        """
        Determine the arguments to pass to the gh cli command.

        :param title: Title for pull request.
        :param body: Body for pull request.
        :param remotes: List of remote urls to push for pull request.
        :param changed_repos: List of repos with PR requests.
        :return: List of arguments to pass to gh cli command.
        """
        return [
            PullRequestOption(
                title=title if title else self.git_service.commit_message(repo.directory),
                body=body if body else "''",
                branch=self.git_service.current_branch(repo.directory),
                remote_url=remotes[idx],
            ).option_list()
            for idx, repo in enumerate(changed_repos)
        ]

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

    def repo_has_changes(self, repo: Repository) -> bool:
        """Check if the given repository has changes that would indicate a PR should be made."""
        if not self.git_service.check_changes(repo.target_branch, repo.directory):
            LOGGER.debug(
                "No changes found for module", module=repo.name, target_branch=repo.target_branch
            )
            return False

        return True
