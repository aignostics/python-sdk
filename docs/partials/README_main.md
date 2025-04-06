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
