# Using evg-module-manager

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Global options](#global-options)
4. [Usage](#usage)
    - [Listing known modules](#listing-known-modules)
    - [Enabling/disabling modules](#enablingdisabling-modules)
    - [Creating a branch](#creating-a-branch)
    - [Working with branches](#working-with-branches)
    - [Committing changes to git](#committing-changes-to-git)
    - [Creating github pull request](#creating-github-pull-request)
    - [Creating an Evergreen patch build](#creating-an-evergreen-patch-build)
    - [Submitting to the commit-queue](#submitting-to-the-commit-queue)

## Overview

`evg-module-manager` is a tool to help work with [Evergreen](https://github.com/evergreen-ci/evergreen)
modules on your local workstation.

## Prerequisites

### Install prerequisites

To fully utilize this tool, the following commands need to be installed and available on your
PATH:

* [`git`](https://git-scm.com): Version 2.17 or higher
* [`evergreen`](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool): The evergreen command line tool.
* [`gh`](https://github.com/cli/cli#installation): The github command line tool.

### Configure authentication to external services

#### Evergreen authentication

Be sure to setup your `.evergreen.yml` configuration for authentication to
evergreen. Details on ensure the evergreen cli is setup correctly can be found
[here](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool).

#### Github authentication

Configure authentication to github with by running:
```bash
gh auth login
```

You can confirm authentication is configured corrected by running:
```bash
gh auth status
```
You should see output similar to the following:
```
github.com
  ✓ Logged in to github.com as username (/Users/username/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use ssh protocol.
  ✓ Token: *******************
```

## Global options

**Note**: `evg-module-manager` expects to be run from the base directory of the repository for the
evergreen project you are working with.

Most actions need to know 2 pieces of information: what evergreen project is being used and where
to store module repos. There can be provided via command line options or via environment variables.

By default, modules will be stored in the parent directory (`..`) from where you are running the command
and the '`mongodb-mongo-master`' project will be used.

To override the defaults via command line options, use the `--evg-project` and `--modules-dir` flags:

```bash
$ evg-module-manager --evg-project mongodb-mongo-v5.0 --modules-dir ~/my_modules ...
```

To override the defaults via environment variables, use `EMM_EVG_PROJECT` and `EMM_MODULES_DIR`.

```bash
$ EMM_EVG_PROJECT=mongodb-mongo-v5.0 EMM_MODULES_DIR=~/mymodules evg-module-manager ...
```

## Usage
### Listing known modules

To see what modules are available for the current project, use the `list-modules` command:

```bash
$ evg-modules-manager --evg-project sys-perf list-modules
- enterprise
- wtdevelop
```

You can use the `--show-details` option to get more details about each module.

```bash
$ evg-module-manager --evg-project mongodb-mongo-master list-modules --show-details
- enterprise
        prefix: src/mongo/db/modules
        repo: git@github.com:10gen/mongo-enterprise-modules.git
        branch: master
- wtdevelop
        prefix: src/third_party
        repo: git@github.com:wiredtiger/wiredtiger.git
        branch: develop
```
You can also pass the `--enabled` option to only list modules which are currently active in your
local repository.

```bash
$ evg-module-manager --evg-project mongodb-mongo-master list-modules --enabled
- wtdevelop
```

### Enabling/disabling modules

To enable a modules in your local repo, use the `enable` command. If the module code is not
available locally, it will be cloned into the directory specified by the `modules-dir` option.
Modules are enabled by adding a symlink to the cloned repository at the modules "prefix".

```bash
$ evg-module-manager enable --module wiredtiger
```

You can disable a module with the `disable` command. This will remove the symlink, but leave
the cloned repository.

```bash
$ evg-module-manager disable --module wiredtiger
```

### Creating a branch

Use `create-branch` command to create a new branch on the base repo and any enabled modules. Use the
`--branch` option to specify the name of the branch to create.

To create a branch named `my-branch`, use the following:
```bash
$ evg-module-manager create-branch --branch my-branch
```

By default, the branch will be created based on the currently checked out commit. You can use the
`--revision` option to base the commit off a different revision.

To create a branch with the revision you want to start work with:
```bash
$ evg-module-manager create-branch --branch my-branch --revision "revision_to_checkout"
```

### Working with branches

After performing some work on a branch, you will frequently want to update your branch with changes
from other branches via a `merge` or `rebase` operation. You can use the `update-branch` subcommand
to perform these operations across the base repo and all enabled modules.

The `--operation` option will allow you to specify whether to perform a `merge` operation or a 
`rebase` operation. By default, a `merge` operation will be performed.

To merge the most recent comment on `master` into my active branch:
```bash
$ evg-module-manager update-branch --operation merge --revision master
```

To rebase the most recent comment on `master` into my active branch:
```bash
$ evg-module-manager update-branch --operation rebase --revision master
```

If any merge conflicts occur during the operation, they will be reported and the repository will 
be left in the unmerged state for manual resolution.

### Committing changes to git

Use the `git-commit` command to commit all your git tracked changes to your base repository and any
modules that are currently enabled. The tool has already specified `--all` and `--message` option to git, which means
it would automatically add and commit all the modifications that git has tracked.

To commit all the tracked changes in base repo and any enabled modules:
```bash
$ evg-module-manager git-commit --commit-message "my commit message"
```

### Creating github pull request

**Note**: In order to create pull requests in github, you need to sure the `gh` command line tool
is available and authentication to github is configured. See [Github authentication](#github-authentication)
for details.

The `pull-request` subcommand will create pull requests across the base repo and all enabled 
modules.  

After local changes have committed in all repos, you can create the pull request from the base 
repo, and all enabled modules with changes would create a separate pull request. Each pull 
request would have comments that contain links for all other modules' pull requests.

To create pull requests in base repo and all enabled modules:

```bash
$ evg-module-manager pull-request
```

By default, the pull request title and body will be determined based on the commits. To override
these, the `--title` and `--body` options can be specified. If you provide the `--body` option,
you must also provide a `--title`.

```bash
$ evg-module-manager pull-request --title "my pull request title" --body "my pull request body"
```

### Creating an Evergreen patch build

**Note**: In order to create a patch build in Evergreen, you need to ensure the `evergreen` 
command line tool is available and configured. See [Evergreen authentication](#evergreen-authentication)
for details.

The `patch` subcommand will create an evergreen patch build with changes to your base repository 
and any modules that are currently enabled. You can pass along any options that the 
`evergreen patch` command supports, however, the `--skip_confirm` and `--project` options are 
already specified by the tools are should not be included.

```bash
$ evg-module-manager patch -d "my patch description" -u
```

### Submitting to the commit-queue

**Note**: In order to submit changes to the commit queue in Evergreen, you need to ensure the 
`evergreen` command line tool is available and configured. See 
[Evergreen authentication](#evergreen-authentication) for details.

The `commit-queue` subcommand will submit changes to the evergreen commit-queue that include 
changes to your base repository and any modules that are currently enabled. You can pass along any
options that the `evergreen commit-queue merge` command supports, however, the `--skip_confirm` 
and `--project` options are already specified by the tools are should not be included.

```bash
$ evg-module-manager commit-queue
```
