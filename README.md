
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


## Introduction

The aignostics Python SDK opens multiple pathways to interact with the
aignostics platform:

1. **Run AI applications** such as
   [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product)
   directly from your terminal using the **Command Line Interface (CLI)**
   included in the SDK.
2. Call applications directly from **Python Notebooks** following the provided
   examples.
3. Deeply integrate the platform in your **enterprise systems and workflows**
   using the Python client provided via the SDK.

### We take quality and security seriously

We know you take **quality** and **security** as seriously as we do. That's why
the aignostics Python SDK is built following best practices and with full
transparency. This includes (1) making the complete
[source code of the SDK
available on GitHub](https://github.com/aignostics/python-sdk/), maintaining a
(2)
[A-grade code quality](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
with [high test coverage](https://app.codecov.io/gh/aignostics/python-sdk) in
all releases, (3) achieving
[A-grade security](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
with
[active scanning of dependencies](https://github.com/aignostics/python-sdk/issues/4),
and (4) providing
[extensive documentation](hhttps://aignostics.readthedocs.io/en/latest/). Read
more about how we achieve
[quality](https://aignostics.readthedocs.io/en/latest/quality.html) and
[security](https://aignostics.readthedocs.io/en/latest/security.html).

### Run your first AI workflow in 30 minutes

Go to
[your personal dashboard on the aignostics platform](https://platform.aignostics.com)
and scroll to the "Python SDK" section. Copy the personalized install script
shown in that section, and execute it in your terminal - we support MacOS and
Linux. This will update or install the [uv package manager](...) and install the
aignostics Python SDK.

You can now ready to run your first AI workflow directly from your terminal. See
as follows for a simple example where we download a sample dataset for the Atlas
H&E-TME application, submit an application run, and download the results.

```shell
uvx aignostics application dataset download —-app atlas_he_tme —-destination ./my-data/in —-dataset example_1
uvx aignostics application run submit —-app atlas_he_tme —-source ./my-data/in
uvx aignostics application run result download –app atlas_he_tme —-run 4711 —-destination ./my-data/out
```

You will find the output in the `./my-data/out` folder on your local disk, Use
tools such as [https://qupath.github.io/](https://qupath.github.io/) to inspect
the analysis results:

1. Open QuPath
2. TODO (Helmut): Explanation of next steps to come

## CLI Usage

The CLI is installed as part of the SDK. You can run it from your terminal using
the `uvx` command. See as follows for the primary commands:

```shell
uvx aignostics platform health          # checks if CLI and Platform are health
uvx aignostics platform info            # shows information about the platform
uvx aignostics application list         # lists AI applications available for the user
# TODO (Helmut): Explain a bit more.
```

The CLI provides extensive help:

```shell
uvx aignostics --help                   # all CLI commands
uvx aignostics application --help       # help for specific topic
uvx aignostics application list --help  # help for specific topic
uvx aignostics serve --help
```

Check out our
[CLI reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html#cli)
to learn about all commands and options available.

### Run with Docker

We recommend to run the CLI natively on your notebook, as explained above. If
required you can run the CLI as a Docker container:

```shell
# TODO (Helmut): Explain about the environment
docker run helmuthva/aignostics-python-sdk --help
docker run helmuthva/aignostics-python-sdk platform health
```

Running via docker compose is supported as well. The .env is passed through from
the host to the Docker container automatically.

```shell
docker compose run aignostics --help
docker compose run aignostics platform health
```

## Library Concepts

Adding Aignostics Python SDK to your codebase as a dependency is easy. See below
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

TODO(Andreas): Update the content below, which comes from oe-python-template:

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

Read the
[client reference documentation](https://aignostics.readthedocs.io/en/latest/lib_reference.html)
to learn about all classes and methods.

## Use in Notebooks

TODO(Andreas): Update the content below, which comes from oe-python-template:

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

If you use other languages then Python in your codebase you can natively
integrate with the webservice API of the aignostics platform

TODO (Andreas): Copy Dzima's doc into docs/partials/README_api.md, assets into
docs/source/_static

[Read the API reference documentation](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html)
to learn about all operations and parameters.


## Further Reading

* Inspect our [security policy](https://aignostics.readthedocs.io/en/latest/security.html) with detailed documentation of checks, tools and principles.
* Check out the [CLI Reference](https://aignostics.readthedocs.io/en/latest/cli_reference.html) with detailed documentation of all CLI commands and options.
* Check out the [Library Reference](https://aignostics.readthedocs.io/en/latest/lib_reference.html) with detailed documentation of public classes and functions.
* Check out the [API Reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) with detailed documentation of all API operations and parameters.
* Our [release notes](https://aignostics.readthedocs.io/en/latest/release-notes.html) provide a complete log of recent improvements and changes.
* In case you want to help us improve 🔬 Aignostics Python SDK: The [contribution guidelines](https://aignostics.readthedocs.io/en/latest/contributing.html) explain how to setup your development environment and create pull requests.
* We gratefully acknowledge the [open source projects](https://aignostics.readthedocs.io/en/latest/attributions.html) that this project builds upon. Thank you to all these wonderful contributors!

## Star History

<a href="https://star-history.com/#aignostics/python-sdk">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=aignostics/python-sdk&type=Date" />
 </picture>
</a>
