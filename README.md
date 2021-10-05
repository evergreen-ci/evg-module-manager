# Evergreen Module Manager

Manage Evergreen modules in your local environment.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/evergreen-module-manager) [![PyPI](https://img.shields.io/pypi/v/evergreen-module-manager.svg)](https://pypi.org/project/evergreen-module-manager/) 

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

TBD

## Dependencies

* Python 3.8 or later
* git
* [Evergreen config file](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool)

## Installation

We strongly recommend using a tool like [pipx](https://pypa.github.io/pipx/) to install
this tool. This will isolate the dependencies and ensure they don't conflict with other tools.

```bash
$ pipx install evergreen-module-manager
```

## Usage

TBD

## Contributor's Guide

### Setting up a local development environment

This project uses [poetry](https://python-poetry.org/) for setting up a local environment.

```bash
git clone ...
cd ...
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
