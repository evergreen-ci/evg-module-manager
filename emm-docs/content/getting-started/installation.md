---
weight: 1
---
## Prerequisites

You'll need an installation of [Python](https://www.python.org/) on your computer. It needs to
be version [3.7.1](https://www.python.org/downloads/release/python-371/) or higher.

To fully utilize this tool, the following commands also need to be installed and available on your
PATH:

* [evergreen](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool): The evergreen command line tool.
* [git](https://git-scm.com): Version 2.17 or higher
* [gh](https://github.com/cli/cli#installation): The github command line tool.
* [pipx](https://pypa.github.io/pipx/): Install python tools in isolated environments.

## Evergreen authentication

Be sure to setup your `.evergreen.yml` configuration for authentication to
evergreen. Details on ensure the evergreen cli is setup correctly can be found
[here](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool).

## Github authentication

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

## Installing evg-module-manager

Use `pipx` to install the tool:

```bash
pipx install evg-module-manager
```

## Updating evg-module-manager

You can also use `pipx` to update to the latest version:

```bash
pipx upgrade evg-module-manager
```
