---
weight: 8
---
Use the `git branch-update` subcommand to update your current branch with the changes made remotely.

The `git branch-update` subcommand will:
* fetch the latest changes from the origin of all the repositories.
* update base local branch with the latest changes, if requested.
* update your branch with the latest changes in the base repository.
* update all enabled modules up to the change associated with where the base repository was updated to.

The `-b`/`--branch` option allows you to specify the base branch, `--local` option can be used if you
are specifying a local base branch rather than remote, `--rebase` option allows to rebase on top of
changes rather than merge changes in.

Updating local base branch and merge changes in on your branch:

```bash
$ evg-module-manager git branch-update --branch master --local
Base: updated to latest 'master'
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```

Updating local base branch and rebase your branch on top of it:

```bash
$ evg-module-manager git branch-update --branch master --local --rebase
Base: updated to latest 'master'
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```

Updating with remote base branch:

```bash
$ evg-module-manager git branch-update --branch origin/master
Base: updated to latest 'origin/master'
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```
