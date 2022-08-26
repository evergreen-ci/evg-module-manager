# Changelog

## 1.2.0 - 2022-08-22
- Add `--local` option to `git branch-update` subcommand.

## 1.1.8 - 2022-08-15
- Cache the results of `evergreen evaluate` when creating a new branch.

## 1.1.7 - 2022-07-08
- Add getting help section.

## 1.1.6 - 2022-04-13
- Document how to handle common pipx install error.

## 1.1.5 - 2022-04-12
- Evaluate evergreen project configuration before using it.

## 1.1.4 - 2022-03-31
- Update documents to notify user set remote before pull-request

## 1.1.3 - 2022-03-28
- Output message when no pull requests are being created.

## 1.1.2 - 2022-03-17
- Set upstream when pushing a branch.

## 1.1.1 - 2022-03-10
- Update documentation to call out Python 3.7.1 dependency.

## 1.1.0 - 2022-02-18
- Add save-local-config subcommand.
- Support reading configuration from local file.

## 1.0.0 - 2022-02-17
- Add several new git subcommands to support a more flexible workflow.
- Replace `create-branch` subcommand with `git-branch-create` subcommand.
- Replace `update-branch` subcommand with `git-branch-update` subcommand.
- Replace `commit-queue` subcommand with `evg-commit-queue` subcommand.
- Replace `patch` subcommand with `evg-patch` subcommand.

## 0.2.3 - 2022-02-16
- Add support for Python 3.7

## 0.2.2 - 2022-02-14
- Add documentation site.

## 0.2.1 - 2022-02-11
- Fix create patch not configurable in Linux

## 0.2.0 - 2022-02-04
- 'pull-request' subcommand will now default to '--fill' and validate arguments.
- 'pull-request' will only add comments if there are multiple PRs being created.

## 0.1.10 - 2022-02-02
- Support git version 2.17
- Update Usage documentation.

## 0.1.9 - 2022-01-25
- Add check for github CLI installation

## 0.1.8 - 2021-12-29
- Add support for github pull request

## 0.1.7 - 2021-12-05
- Add check for changelog updates

## 0.1.6 - 2021-11-29
- Adding branching support

## 0.1.5 - 2021-11-24
- Ability to create commits in enabled modules

## 0.1.4 - 2021-11-23
- Add check to ensure version update

## 0.1.3 - 2021-11-16
- Add support for evergreen test

## 0.1.2 - 2021-11-09
- Add Apache-2.0 license

## 0.1.1 - 2021-11-08
- Update project metadata

## 0.1.0 - 2021-11-08
- Initial Release
