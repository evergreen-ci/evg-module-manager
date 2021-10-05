# Evergreen Module Manager

Manage Evergreen modules in your local environment.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/evg-module-manager) [![PyPI](https://img.shields.io/pypi/v/evg-module-manager.svg)](https://pypi.org/project/evg-module-manager/) 

## Table of contents

1. [Description](#description)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contributor's Guide](#contributors-guide)
    - [Setting up a local development environment](#setting-up-a-local-development-environment)
    - [linting/formatting](#lintingformatting)
    - [Running tests](#running-tests)
    - [Automatically running checks on commit](#automatically-running-checks-on-commit)
    - [Versioning](#versioning)
    - [Code Review](#code-review)
    - [Deployment](#deployment)
6. [Resources](#resources)

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

## Dependencies

* Python 3.8 or later
* git
* evergreen command line tool
* [Evergreen config file](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool)

## Installation

We strongly recommend using a tool like [pipx](https://pypa.github.io/pipx/) to install
this tool. This will isolate the dependencies and ensure they don't conflict with other tools.

```bash
$ pipx install evg-module-manager
```

## Usage

See the [usage](docs/usage.md) documentation for details about using this tool.

```bash
evg-module-manager --help
Usage: evg-module-manager [OPTIONS] COMMAND [ARGS]...

  Evergreen Module Manager is a tool help simplify the local workflows of evergreen modules.

Options:
  --modules-dir PATH      Directory to store module repositories [default='..']
  --evg-config-file PATH  Path to file with evergreen auth configuration
                          [default='/Users/user/.evergreen.yml']
  --evg-project TEXT      Name of Evergreen project [default='mongodb-mongo-master']
  --help                  Show this message and exit.

Commands:
  commit-queue  Submit changes from the base repository and any enabled modules to the...
  disable       Disable the specified module in the current repo.
  enable        Enable the specified module in the current repo.
  list-modules  List the modules available for the current repo.
  patch         Create an Evergreen patch with changes from the base repo and any enabled...
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

Deployment to pypi is automatically triggered on merges to master.

## Resources

* [Evergreen REST documentation](https://github.com/evergreen-ci/evergreen/wiki/REST-V2-Usage)
