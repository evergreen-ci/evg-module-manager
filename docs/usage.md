# Using evg-module-manager

## Overview

`evg-module-manager` is a tool to help work with [Evergreen](https://github.com/evergreen-ci/evergreen)
modules on your local workstation.

### Prerequisites

In order to use the tool, be sure to have `git` and the `evergreen` cli installed and available
on your path. Also, be sure to setup your `.evergreen.yml` configuration for authentication to
evergreen. Details on ensure the evergreen cli is setup correctly can be found
[here](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool).

### Global options

Most actions need to know 2 pieces of information: what evergreen project is being used and where
to store module repos. There can be provided via command line options or via environment variables.

By default, modules will be stored in the parent directory from where you are running the command
and the 'mongodb-mongo-master' project will be used.

To override the defaults via command line options, use the `--evg-project` and `--modules-dir` flags:

```bash
evg-module-manager --evg-project mongodb-mongo-v5.0 --modules-dir ~/my_modules ...
```

To override the defaults via environment variables, use `EMM_EVG_PROJECT` and `EMM_MODULES_DIR`.

```bash
EMM_EVG_PROJECT=mongodb-mongo-v5.0 EMM_MODULES_DIR=~/mymodules evg-module-manager ...
```

## Getting the available modules

To see what modules are available, use the list-modules command:

```bash
evg-modules-manager list-modules
```

You can use the `--show-details` option to get more details about each module.

You can also pass the `--enabled` option to only list modules which are currently active in your
local repository.

## Enabling/disabling modules

To enable a modules in your local repo, use the `enable` command. If the module code is not
available locally, it will be cloned into the directory specified by the `modules-dir` option.
Modules are enabled by adding a symlink to the cloned repository at the modules "prefix".

```bash
evg-module-manager enable --module wiredtiger
```

You can disable a module with the `disable` command. This will remore the symlink, but leave
the cloned repository.

```bash
evg-module-manager disable --module wiredtiger
```

## Creating a branch

Use `git-branch` command to create a new branch on base repo and any enabled modules.
To create a new branch, you can use the **checkout** option along with the revision
you want to work with. If you want to create a new branch with a certain name,
specify the branch name to create with the `-b` or `--branch` option.

Checkout to the revision you want to work with:
```bash
evg-module-manager git-branch --operation checkout --revision "revision_to_checkout"
```

To create a branch named `my-branch`, use the following:
```bash
evg-module-manager git-branch --operation checkout --branch my-branch --revision HEAD
```


## Updating existing git branches

Use `git-branch` command to update your existing branches on base repo and any enabled modules.
By default, a git checkout action will be performed to the user provided revision
in the base repository.

For revisions on modules, the revision to be checked out would be the
revision for the module in the evergreen manifest associated with the latest commit in the history that
was run in evergreen.

To update the branch with the latest comment on all enabled modules. You can use the **rebase** or
**merge** operations, if any merge conflicts occur, they will be reported and
the repository will be left in the unmerged state for manually resolution.

To merge my active branch on the most recent comment:
```bash
evg-module-manager git-branch --operation merge --revision HEAD
```

To rebase my active branch on the most recent commit:
```bash
evg-module-manager git-branch --operation rebase --revision HEAD
```

## Performing git commit all

Use the `git-commit` command to commit all your git tracked changes to your base repository and any
modules that are currently enabled. The tool has already specified `--all` and `--message` option to git, which means
it would automatically add and commit all the modifications that git has tracked.

To commit all the tracked changes in base repo and any enabled modules:
```bash
evg-module-manager git-commit --commit-message "my commit message"
```

## Submitting a patch build

Use the `patch` command to create a patch build with changes to your base repository and any
modules that are currently enabled. You can pass along any options that the `evergreen patch`
command supports, however, the `--skip_confirm` and `--project` options are already specified
by the tools are should not be included.

```bash
evg-module-manager patch -d "my patch description" -u
```

## Submitting to the commit-queue

Use the `commit-queue` command to submit changes to the commit-queue that include changes to
your base repository and any modules that are currently enabled. You can pass along any
options that the `evergreen commit-queue merge` command supports, however, the
`--skip_confirm` and `--project` options are already specified by the tools are should not
be included.

```bash
evg-module-manager commit-queue
```
