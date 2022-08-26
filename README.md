# Evergreen Module Manager

Manage Evergreen modules in your local environment.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/evg-module-manager) [![PyPI](https://img.shields.io/pypi/v/evg-module-manager.svg)](https://pypi.org/project/evg-module-manager/) [![Documentation](https://img.shields.io/badge/Docs-Available-green)](https://evergreen-ci.github.io/evg-module-manager/)
## Table of contents

1. [Description](#description)
2. [Getting Help](#getting-help)
3. [Documentation](#documentation)
4. [Dependencies](#dependencies)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Contributor's Guide](#contributors-guide)
    - [Setting up a local development environment](#setting-up-a-local-development-environment)
    - [linting/formatting](#lintingformatting)
    - [Running tests](#running-tests)
    - [Automatically running checks on commit](#automatically-running-checks-on-commit)
    - [Versioning](#versioning)
    - [Code Review](#code-review)
    - [Deployment](#deployment)
8. [Resources](#resources)

## Description

The evg-module-manager is a tool to help improve the local workflows of working with modules in
your evergreen projects. It will help you keep any modules defined in your local project in sync.
It supports the following functionality:

* List what modules are defined in the local project.
* List what modules are currently active in your local repo.
* Clone a module repository.
* Enable/disable modules in your local repo.
* Create an evergreen patch build that includes changes from the local patch build and all enabled
  modules.
* Submit a changes to the commit-queue that includes changes from the local patch build and all
  enabled modules.

## Getting Help

### What's the right channel to ask my question?
If you have a question about evg-module-manager, please mention @dag-on-call in the
slack channel [#evergreen-users](https://mongodb.slack.com/messages/#evergreen-users/)
or email us at
dev-prod-dag@mongodb.com.

### How can I request a change/report a bug in evg-module-manager?
Create a [DAG ticket](https://jira.mongodb.org/projects/DAG).

### What should I include in my ticket or #evergreen-users question?
Since #evergreen-users questions are interrupts,
please include as much information as possible.
This can help avoid long information-gathering threads.

Please include the following in any created tickets:
* **Motivation for Request**
  * Provide us the motivation for this change.
* **Context**
  * Provide some background context for this issue.
* **Description**
  * Provide some description on how this issue happened.

## Documentation

Read the documentation [here](https://evergreen-ci.github.io/evg-module-manager/).

## Dependencies

* Python 3.7 or later
* git
* evergreen command line tool
* [Evergreen config file](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool)
* [github CLI](https://cli.github.com/)

See [Usage Prerequisites](https://github.com/evergreen-ci/evg-module-manager/blob/main/docs/usage.md#prerequities)
for more details.

## Installation

We strongly recommend using a tool like [pipx](https://pypa.github.io/pipx/) to install
this tool. This will isolate the dependencies and ensure they don't conflict with other tools.

```bash
$ pipx install evg-module-manager
```

### Debugging installation issues

A common issue that arises during installation is pipx failing to install emm and printing out the following error:
```bash
$ pipx install evg-module-manager
Fatal error from pip prevented installation. Full pip output in file:
    /home/ubuntu/.local/pipx/logs/cmd_2022-03-31_13.24.42_pip_errors.log
 
Some possibly relevant errors from pip install:
    ERROR: Could not find a version that satisfies the requirement evg-module-manager (from versions: none)
    ERROR: No matching distribution found for evg-module-manager
 
Error installing evg-module-manager.
```

This error indicates that pipx could not find a version of emm that was built to support the version of Python installed on your machine.
Make sure to check that your version of Python matches the requirements called out in the [Dependencies](#dependencies) section. You
can check the version of Python that is on your computer by running
```bash
$ python --version
```

If you are running into the issue above but are sure that the correct version of Python is installed on your computer,
you can explicitly specify a path to the correct Python version during installation.

```bash
$ which python3.9
/usr/bin/python3.9
$ pipx install evg-module-manager --python /usr/bin/python3.9
```

## Usage

See the [documentation](https://evergreen-ci.github.io/evg-module-manager/) for details about using this tool.

```bash
Usage: evg-module-manager [OPTIONS] COMMAND [ARGS]...

  Evergreen Module Manager is a tool help simplify the local workflows of evergreen modules.

Options:
  --modules-dir PATH      Directory to store module repositories [default='..']
  --evg-config-file PATH  Path to file with evergreen auth configuration
                          [default='/Users/dbradf/.evergreen.yml']
  --evg-project TEXT      Name of Evergreen project [default='mongodb-mongo-master']
  --help                  Show this message and exit.

Commands:
  disable       Disable the specified module in the current repo.
  enable        Enable the specified module in the current repo.
  evg           Perform evergreen actions against the base repo and enabled modules.
  git           Perform git actions against the base repo and enabled modules.
  list-modules  List the modules available for the current repo.
  pull-request  Create a Github pull request for changes in the base repository and any...
```

## Contributor's Guide

### Setting up a local development environment

This project uses [poetry](https://python-poetry.org/) for setting up a local environment.

```bash
git clone ...
cd evg-module-manager
poetry install
```

### linting/formatting

This project uses [black](https://black.readthedocs.io/en/stable/) and
[isort](https://pycqa.github.io/isort/) for formatting.

```bash
poetry run black src tests
poetry run isort src tests
```

### Running tests

This project uses [pytest](https://docs.pytest.org/en/6.2.x/) for testing.

```bash
poetry run pytest
```

### Automatically running checks on commit

This project has [pre-commit](https://pre-commit.com/) configured. Pre-commit will run
configured checks at git commit time. To enable pre-commit on your local repository run:

```bash
poetry run pre-commit install
```

### Versioning

This project uses [semver](https://semver.org/) for versioning.

Please include a description what is added for each new version in `CHANGELOG.md`.

### Code Review

Please open a Github Pull Request for code review.

### Deployment

Deployment to pypi is automatically triggered on merges to main.

## Resources

* [Evergreen REST documentation](https://github.com/evergreen-ci/evergreen/wiki/REST-V2-Usage)
