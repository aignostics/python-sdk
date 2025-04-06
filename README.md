
[//]: # (README.md generated from docs/partials/README_*.md)

# 🔬 Aignostics Python SDK

[![License](https://img.shields.io/github/license/aignostics/python-sdk?logo=opensourceinitiative&logoColor=3DA639&labelColor=414042&color=A41831)
](https://github.com/aignostics/python-sdk/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aignostics.svg?logo=python&color=204361&labelColor=1E2933)](https://github.com/aignostics/python-sdk/blob/main/noxfile.py)
[![CI](https://github.com/aignostics/python-sdk/actions/workflows/test-and-report.yml/badge.svg)](https://github.com/aignostics/python-sdk/actions/workflows/test-and-report.yml)
[![Read the Docs](https://img.shields.io/readthedocs/aignostics)](https://aignostics.readthedocs.io/en/latest/)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)

[![Dependabot](https://img.shields.io/badge/dependabot-active-brightgreen?style=flat-square&logo=dependabot)](https://github.com/aignostics/python-sdk/security/dependabot)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://github.com/aignostics/python-sdk/issues?q=is%3Aissue%20state%3Aopen%20Dependency%20Dashboard)
[![Coverage](https://codecov.io/gh/aignostics/python-sdk/graph/badge.svg?token=SX34YRP30E)](https://codecov.io/gh/aignostics/python-sdk)
[![Ruff](https://img.shields.io/badge/style-Ruff-blue?color=D6FF65)](https://github.com/aignostics/python-sdk/blob/main/noxfile.py)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/aignostics/python-sdk/blob/main/noxfile.py)
[![GitHub - Version](https://img.shields.io/github/v/release/aignostics/python-sdk?label=GitHub&style=flat&labelColor=1C2C2E&color=blue&logo=GitHub&logoColor=white)](https://github.com/aignostics/python-sdk/releases)
[![GitHub - Commits](https://img.shields.io/github/commit-activity/m/aignostics/python-sdk/main?label=commits&style=flat&labelColor=1C2C2E&color=blue&logo=GitHub&logoColor=white)](https://github.com/aignostics/python-sdk/commits/main/)
[![PyPI - Version](https://img.shields.io/pypi/v/aignostics.svg?label=PyPI&logo=pypi&logoColor=%23FFD243&labelColor=%230073B7&color=FDFDFD)](https://pypi.python.org/pypi/aignostics)
[![PyPI - Status](https://img.shields.io/pypi/status/aignostics?logo=pypi&logoColor=%23FFD243&labelColor=%230073B7&color=FDFDFD)](https://pypi.python.org/pypi/aignostics)
[![Docker - Version](https://img.shields.io/docker/v/helmuthva/aignostics-python-sdk?sort=semver&label=Docker&logo=docker&logoColor=white&labelColor=1354D4&color=10151B)](https://hub.docker.com/r/helmuthva/aignostics-python-sdk/tags)
[![Docker - Size](https://img.shields.io/docker/image-size/helmuthva/aignostics-python-sdk?sort=semver&arch=arm64&label=image&logo=docker&logoColor=white&labelColor=1354D4&color=10151B)](https://hub.docker.com/r/helmuthva/aignostics-python-sdk/)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE3IDE2VjdsLTYgNU0yIDlWOGwxLTFoMWw0IDMgOC04aDFsNCAyIDEgMXYxNGwtMSAxLTQgMmgtMWwtOC04LTQgM0gzbC0xLTF2LTFsMy0zIi8+PC9zdmc+)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/aignostics/python-sdk)
[![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/aignostics/python-sdk)

<!---
[![ghcr.io - Version](https://ghcr-badge.egpl.dev/aignostics/python-sdk/tags?color=%2344cc11&ignore=0.0%2C0%2Clatest&n=3&label=ghcr.io&trim=)](https://github.com/aignostics/python-sdk/pkgs/container/python-sdk)
[![ghcr.io - Sze](https://ghcr-badge.egpl.dev/aignostics/python-sdk/size?color=%2344cc11&tag=latest&label=size&trim=)](https://github.com/aignostics/python-sdk/pkgs/container/python-sdk)
-->

> [!TIP]
> 📚 [Online documentation](https://aignostics.readthedocs.io/en/latest/) - 📖 [PDF Manual](https://aignostics.readthedocs.io/_/downloads/en/latest/pdf/)

> [!NOTE]
> 🧠 This project was scaffolded using the template [oe-python-template](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template) with [copier](https://copier.readthedocs.io/).

---


Python SDK enabling access to aignostics platform.

## Introduction

TODO (Helmut): Functionality and features.

### Operational Excellence

TODO (Helmut): Simplify. Focus on earning trust of customers.

The aignostics Python SDK is built with operational excellence, using modern
Python tooling and practices. This includes:

1. Various examples demonstrating usage: a.
   [Simple Python script](https://github.com/aignostics/python-sdk/blob/main/examples/script.py)
   b. [Streamlit web application](https://aignostics.streamlit.app/) deployed on
   [Streamlit Community Cloud](https://streamlit.io/cloud) c.
   [Jupyter](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb)
   and
   [Marimo](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.py)
   notebook
2. [Complete reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html)
   on Read the Docs
3. [Transparent test coverage](https://app.codecov.io/gh/aignostics/python-sdk)
   including unit and E2E tests (reported on Codecov)
4. Matrix tested with
   [multiple python versions](https://github.com/aignostics/python-sdk/blob/main/noxfile.py)
   to ensure compatibility (powered by [Nox](https://nox.thea.codes/en/stable/))
5. Compliant with modern linting and formatting standards (powered by
   [Ruff](https://github.com/astral-sh/ruff))
6. Up-to-date dependencies (monitored by
   [Renovate](https://github.com/renovatebot/renovate) and
   [Dependabot](https://github.com/aignostics/python-sdk/security/dependabot))
7. [A-grade code quality](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
   in security, maintainability, and reliability with low technical debt and
   codesmell (verified by SonarQube)
8. Additional code security checks using
   [CodeQL](https://github.com/aignostics/python-sdk/security/code-scanning)
9. [Security Policy](SECURITY.md)
10. [License](LICENSE) compliant with the Open Source Initiative (OSI)
11. 1-liner for installation and execution of command line interface (CLI) via
    [uv(x)](https://github.com/astral-sh/uv) or
    [Docker](https://hub.docker.com/r/helmuthva/aignostics-python-sdk/tags)
12. Setup for developing inside a
    [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers)
    included (supports VSCode and GitHub Codespaces)

## Setup

TODO (Helmut): Explain, starting with copy of script on
https://platform.aignostics.com

## CLI Usage

Executing the command line interface (CLI) in an isolated Python environment is
just as easy:

```shell
uvx aignostics platform health          # checks if CLI and Platform are health
uvx aignostics platform info            # shows information about the platform
uvx aignostics application list         # lists AI applications available for the user
```

Notes:

The CLI provides extensive help:

```shell
uvx aignostics --help                   # all CLI commands
uvx aignostics application --help       # help for specific topic
uvx aignostics application list --help  # help for specific topic
uvx aignostics serve --help
```

### Run with Docker

You can as well run the CLI within Docker.

```shell
docker run helmuthva/aignostics-python-sdk --help
docker run helmuthva/aignostics-python-sdk platform health
```

Execute command:

```shell
docker run --env THE_VAR=MY_VALUE helmuthva/aignostics-python-sdk platform health
```

Or use docker compose

The .env is passed through from the host to the Docker container.

```shell
docker compose run aignostics --help
docker compose run aignostics platform health
```

## Library Concepts

Adding Aignostics Python SDK to your project as a dependency is easy. See below
for usage examples.

```shell
uv add aignostics                       # add SDK as dependency to your project
```

If you don't have uv installed follow
[these instructions](https://docs.astral.sh/uv/getting-started/installation/).
If you still prefer pip over the modern and fast package manager
[uv](https://github.com/astral-sh/uv), you can install the library like this:

```shell
pip install aignostics                  # add SDK as dependency to your project
```

The following examples run from source - clone this repository using
`git clone git@github.com:aignostics/python-sdk.git`.

### Minimal Python Script:

```python
"""Example script demonstrating the usage of the service provided by Aignostics Python SDK."""

from dotenv import load_dotenv
from rich.console import Console

from aignostics import Service

console = Console()

load_dotenv()

message = Service.get_hello_world()
console.print(f"[blue]{message}[/blue]")
```

[Show script code](https://github.com/aignostics/python-sdk/blob/main/examples/script.py) -
[Read the reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html)

## Use in Notebooks

### Jupyter

[Show the Jupyter code](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb)

... or run within VSCode

```shell
uv sync --all-extras                                # Install dependencies required for examples such as Juypyter kernel, see pyproject.toml
```

Install the
[Jupyter extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

Click on `examples/notebook.ipynb` in VSCode and run it.

### Marimo

[Show the marimo code](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.py)

Execute the notebook as a WASM based web app

```shell
uv sync --all-extras                                # Install ipykernel dependency part of the examples extra, see pyproject.toml
uv run marimo run examples/notebook.py --watch      # Serve on localhost:2718, opens browser
```

or edit interactively in your browser

```shell
uv sync --all-extras                                # Install ipykernel dependency part of the examples extra, see pyproject.toml
uv run marimo edit examples/notebook.py --watch     # Edit on localhost:2718, opens browser
```

... or edit interactively within VSCode

Install the
[Marimo extension for VSCode](https://marketplace.visualstudio.com/items?itemName=marimo-team.vscode-marimo)

Click on `examples/notebook.py` in VSCode and click on the caret next to the Run
icon above the code (looks like a pencil) > "Start in marimo editor" (edit).

## API Concepts

TODO (Andreas): Explain API concepts, such as authentication, resources etc..


## Further Reading

* Inspect our [security policy](https://aignostics.readthedocs.io/en/latest/security.html) with detailed documentation of checks, tools and principles.
* Check out the [CLI Reference](https://aignostics.readthedocs.io/en/latest/cli_reference.html) with detailed documentation of all CLI commands and options.
* Check out the [Library Reference](https://aignostics.readthedocs.io/en/latest/lib_reference.html) with detailed documentation of public classes and functions.
* Check out the [API Reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) with detailed documentation of all API operations and parameters.
* Our [release notes](https://aignostics.readthedocs.io/en/latest/release-notes.html) provide a complete log of recent improvements and changes.
* In case you want to help us improve 🔬 Aignostics Python SDK: The [contribution guidelines](https://aignostics.readthedocs.io/en/latest/contributing.html) explain how to setup your development environment and create pull requests.
* We gratefully acknowledge the [open source projects](ATTRIBUTIONS.md) that this project builds upon. Thank you to all these wonderful contributors!

## Star History

<a href="https://star-history.com/#aignostics/python-sdk">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date" />
 </picture>
</a>
