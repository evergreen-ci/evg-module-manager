"""Service for working with git."""
import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from plumbum import local


class GitAction(str, Enum):
    """Actions to perform on a git repository."""

    CHECKOUT = "checkout"
    REBASE = "rebase"
    MERGE = "merge"


class GitService:
    """A service for interacting with git."""

    def __init__(self) -> None:
        """Initialize the service."""
        self.git = local.cmd.git

    def perform_git_action(
        self,
        git_action: GitAction,
        revision: str,
        branch_name: Optional[str] = None,
        directory: Optional[Path] = None,
    ) -> None:
        """
        Perform the given git action on a repository.

        :param git_action: Git action to perform.
        :param revision: Git revision to perform action against.
        :param branch_name: Branch name to create if running checkout.
        :param directory: Path to root of repo to operate on.
        """
        if git_action == GitAction.CHECKOUT:
            self.checkout(revision, directory, branch_name)
        elif git_action == GitAction.REBASE:
            self.rebase(revision, directory)
        elif git_action == GitAction.MERGE:
            self.merge(revision, directory)
        else:
            raise ValueError(f"Unknown git action: {git_action.value}")

    def clone(self, name: str, remote_repo: str, directory: Path, branch: Optional[str]) -> None:
        """
        Clone the specified repository to the given location.

        :param name: Local name to use for cloned repo.
        :param remote_repo: Remote repo location.
        :param directory: Directory to clone repo into.
        :param branch: Branch to checkout.
        """
        args = ["clone"]
        if branch is not None:
            args += ["--branch", branch]
        args += [remote_repo, name]

        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def fetch(self, directory: Optional[Path] = None) -> None:
        """
        Fetch commit from origin.

        :param directory: Path to root of repo to operate on.
        """
        args = ["fetch", "origin"]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def checkout(
        self, revision: str, directory: Optional[Path] = None, branch_name: Optional[str] = None
    ) -> None:
        """
        Checkout the given revision.

        :param revision: Revision to checkout.
        :param directory: Directory to execute command at.
        :param branch_name: Name of branch for git checkout.
        """
        args = ["checkout"]
        if branch_name is not None:
            args += ["-b", branch_name]
        args.append(revision)
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def rebase(self, revision: str, directory: Optional[Path] = None) -> None:
        """
        Rebase on the given revision.

        :param revision: Revision to rebase on.
        :param directory: Directory to execute command at.
        """
        args = ["rebase", revision]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def merge(self, revision: str, directory: Optional[Path] = None) -> None:
        """
        Merge the given revision.

        :param revision: Revision to merge.
        :param directory: Directory to execute command at.
        """
        args = ["merge", revision]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def current_commit(self, directory: Optional[Path] = None) -> str:
        """
        Get the commit hash of the current HEAD of a repository.

        :param directory: Path to repository to query.
        :return: Git hash of HEAD of repository.
        """
        args = ["rev-parse", "HEAD"]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def merge_base(self, commit_a: str, commit_b: str, directory: Optional[Path] = None) -> str:
        """
        Find the common ancestor of the given commits.

        :param commit_a: First commit to compare.
        :param commit_b: Second commit to compare.
        :param directory: Path to repository to query.
        :return: Git hash of common ancestor of the 2 commits.
        """
        args = ["merge-base", commit_a, commit_b]
        with local.cwd(self._determine_directory(directory)):
            return self.git[args]().strip()

    def commit_all(self, commit_message: str, directory: Optional[Path] = None) -> None:
        """
        Get the commit hash of the current HEAD of a repository.

        :param commit_message: Commit message for all the changes.
        :param directory: Directory to execute command at.
        """
        args = ["commit", "--all", "--message", commit_message]
        with local.cwd(self._determine_directory(directory)):
            self.git[args]()

    def rev_list(
        self, date: datetime.datetime, revision: Optional[str], directory: Optional[Path] = None
    ) -> str:
        """
        Get the list of revisions in range start to end.

        :param date: End date to get rev_list.
        :param revision: Revision to get rev_list.
        :param directory: Directory to execute command at.git
        :return: List of revisions.
        """
        args = ["rev-list", revision, "--max-count=1", f"--before={date}"]
        with local.cwd(self._determine_directory(directory)):
            res = self.git[args]().strip()
            print(res)
            return res

    def datetime_to_string(self, datetimes: datetime.datetime) -> str:
        """Convert datetime object to string."""
        if datetimes.hour == 0 and datetimes.minute == 0 and datetimes.second == 0:
            return datetimes.strftime("%Y.%m.%d")
        return datetimes.strftime("%Y.%m.%d.%H.%M.%S")

    def string_to_datetime(self, dates: str) -> datetime.datetime:
        """Convert date string to datetime object."""
        fields = dates.split(".")
        if len(fields) == 6:
            return datetime.datetime(
                int(fields[0]),
                int(fields[1]),
                int(fields[2]),
                int(fields[3]),
                int(fields[4]),
                int(fields[5]),
            )
        if len(fields) == 4:
            return datetime.datetime(int(fields[0]), int(fields[1]), int(fields[2]), int(fields[3]))
        if len(fields) == 3:
            return datetime.datetime(int(fields[0]), int(fields[1]), int(fields[2]))
        raise ValueError("Invalid Date format.")

    def bisect_in_dates(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> datetime.datetime:
        """Get the middle date between two datetime objects."""
        delta = (end - start) / 2
        print(delta)
        if delta.total_seconds() < 3600:
            raise ValueError("No more dates left.")

        mid = start + delta
        if mid.minute != 0 or mid.second != 0:
            mid = mid.replace(minute=0, second=0)
        if delta.total_seconds() > 86400 and start.hour == 0 and end.hour == 0:
            if mid.hour != 0:
                mid = mid.replace(hour=0)
        return mid

    def write_states(self, states_dict: Dict[str, str]) -> None:
        """Write the bisect state file."""
        state_path = Path(local.cwd) / "bisect"
        file = open(state_path, "w")
        file.write("start=%s\n" % (states_dict["start"]))
        file.write("end=%s\n" % (states_dict["end"]))
        file.close()

    def read_state(self) -> Dict[str, str]:
        """Read the previous bisect state."""
        state_path = Path(local.cwd) / "bisect"
        file = open(state_path, "r")
        state = dict()
        for line in file:
            dates, dates_value = line.strip().split("=")
            state[dates] = dates_value
        file.close()
        return state

    def bisect_start(
        self,
        state_dict: Dict[str, str],
        date: datetime.datetime,
        revision: Optional[str] = "HEAD",
        directory: Optional[Path] = None,
    ) -> None:
        """Start the bisect operation."""
        self.write_states(state_dict)
        self.rev_list(date, revision, directory)

    def bisect_mark(
        self, action: str, revision: Optional[str], directory: Optional[Path] = None
    ) -> None:
        """Mark the bisect results."""
        state = self.read_state()
        start_date = self.string_to_datetime(state["start"])
        end_date = self.string_to_datetime(state["end"])
        mid = self.bisect_in_dates(start_date, end_date)
        if action == "good":
            state["start"] = self.datetime_to_string(mid)
        else:
            state["end"] = self.datetime_to_string(mid)
        states_dict = {"start": state["start"], "end": state["end"]}
        print(f"bisect between {state['start']} and {state['end']}")
        self.bisect_start(states_dict, mid, revision, directory)

    def perform_bisect_action(
        self,
        bisect_action: str,
        start: str,
        end: str,
        revision: Optional[str] = "HEAD",
        directory: Optional[Path] = None,
    ) -> None:
        """Execute the bisect method."""
        if bisect_action == "start":
            states_dict = {"start": start, "end": end}
            start_date = self.string_to_datetime(start)
            end_date = self.string_to_datetime(end)
            mid = self.bisect_in_dates(start_date, end_date)
            print(f"bisect between {start} and {end}")
            self.bisect_start(states_dict, mid, revision, directory)
        elif bisect_action in ("good", "bad"):
            self.bisect_mark(bisect_action, revision, directory)
        else:
            raise ValueError(f"Unknown bisect action: {bisect_action}")

    @staticmethod
    def _determine_directory(directory: Optional[Path] = None) -> Path:
        """
        Determine which directory to run git command in.

        :param directory: Directory containing it repository.
        :return: Path to run git commands in.
        """
        if directory is None:
            return Path(local.cwd)
        elif not directory.is_absolute():
            return Path(local.cwd / directory)
        return directory
