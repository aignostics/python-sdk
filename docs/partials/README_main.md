Python SDK providing access to Aignostics AI services.

This [Copier](https://copier.readthedocs.io/en/stable/) template enables you to quickly generate a Python package with fully functioning build and test automation.
Projects generated from this template can be [easily updated](https://copier.readthedocs.io/en/stable/updating/) to benefit from improvements and new features of the template.

Features:
1. Package management with [uv](https://github.com/astral-sh/uv)
2. Code formatting with [Ruff](https://github.com/astral-sh/ruff)
3. Linting with [Ruff](https://github.com/astral-sh/ruff)
4. Static type checking with [mypy](https://mypy.readthedocs.io/en/stable/)
5. Complete set of [pre-commit](https://pre-commit.com/) hooks including [detect-secrets](https://github.com/Yelp/detect-secrets) and [pygrep](https://github.com/pre-commit/pygrep-hooks)
6. Unit and E2E testing with [pytest](https://docs.pytest.org/en/stable/) including parallel test execution
7. Matrix testing in multiple environments with [nox](https://nox.thea.codes/en/stable/)
8. Test coverage reported with [Codecov](https://codecov.io/) and published as release artifact
9. CI/CD pipeline automated with [GitHub Actions](https://github.com/features/actions)
10. CI/CD pipeline can be run locally with [act](https://github.com/nektos/act)
11. Code quality and security checks with [SonarQube](https://www.sonarsource.com/products/sonarcloud) and [GitHub CodeQL](https://codeql.github.com/)
12. Dependency monitoring with [pip-audit](https://pypi.org/project/pip-audit/), [Renovate](https://github.com/renovatebot/renovate), and [GitHub Dependabot](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide)
13. Licenses of dependencies extracted with [pip-licenses](https://pypi.org/project/pip-licenses/) and published as release artifacts in CSV and JSON format for compliance checks
14. Software Bill of Materials (SBOM) generated with [cyclonedx-python](https://github.com/CycloneDX/cyclonedx-python) and published as release artifact
15. Version and release management with [bump-my-version](https://callowayproject.github.io/bump-my-version/)
16. Changelog and release notes generated with [git-cliff](https://git-cliff.org/)
17. Documentation generated with [Sphinx](https://www.sphinx-doc.org/en/master/) including reference documentation and PDF export
18. Documentation published to [Read The Docs](https://readthedocs.org/)
19. Interactive OpenAPI specification with [Swagger](https://swagger.io/)
20. Python package published to [PyPI](https://pypi.org/)
21. Docker images published to [Docker.io](https://hub.docker.com/) and [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) with [artifact attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds)
22. One-click development environments with [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) and [GitHub Codespaces](https://github.com/features/codespaces)
23. Settings for use with [VSCode](https://code.visualstudio.com/)
24. Settings and custom instructions for use with [GitHub Copilot](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)

The generated project includes code, documentation and configuration of a fully functioning demo-application and service, which can be used as a starting point for your own project.
1. Service architecture suitable for use as shared library
2. Validation with [pydantic](https://docs.pydantic.dev/)
3. Command-line interface (CLI) with [Typer](https://typer.tiangolo.com/)
4. Versioned Web API with [FastAPI](https://fastapi.tiangolo.com/)
5. [Interactive Jupyter notebook](https://jupyter.org/) and [reactive Marimo notebook](https://marimo.io/)
6. Simple Web UI with [Streamlit](https://streamlit.io/)
7. Configuration to run the CLI and API in a Docker container including setup for [Docker Compose](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-docker-compose/)
8. Documentation including badges, setup instructions, contribution guide and security policy

Explore [here](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example) for what's generated out of the box.

## Generate a new project

This template is designed to be used with the [copier](https://copier.readthedocs.io/en/stable/) project generator. It allows you to create a new project based on this template and customize it according to your needs.
To generate a new project, follow these steps:

**Step 1**: Install uv package manager and copier. Copy the following code into your terminal and execute it.
```shell
if [[ "$OSTYPE" == "darwin"* ]]; then                 # Install dependencies for macOS X
  if ! command -v brew &> /dev/null; then             ## Install Homebrew if not present
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then            # Install dependencies for Linux
  sudo apt-get update -y && sudo apt-get install curl -y # Install curl
fi
if ! command -v uvx &> /dev/null; then                # Install uv package manager if not present
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.local/bin/env
fi
uv tool install copier                                # Install copier as global tool
```

**Step 2**: [Create an empty repository on GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository), clone to your local machine, and change into it's directory.

**Step 3**: Generate the project. Copy
```shell
copier copy --trust gh:helmut-hoffer-von-ankershoffen/oe-python-template .
```

**Step 4**: Perform initial commit and push. Copy the following code into your terminal and execute it.
```shell
git add .
git commit -m "feat: Initial commit"
git push
```

Visit your GitHub repository and check the Actions tab. The CI workflow should already be running! The workflow will fail at the SonarQube step, as this external service is not yet configured for our new repository.

**Step 5**: Follow the [instructions](SERVICE_CONNECTIONS.md) to wire up
external services such as CloudCov, SonarQube Cloud, Read The Docs, Docker.io, and Streamlit Community Cloud.

**Step 6**: Release the first versions
```shell
./n bump
```
Notes:
1. You can remove this section post having successfully generated your project.
2. The following sections refer to the dummy application and service provided by this template.
   Use them as inspiration and adapt them to your own project.

## Overview

Adding Aignostics Python SDK to your project as a dependency is easy. See below for usage examples.

```shell
uv add aignostics             # add dependency to your project
```

If you don't have uv installed follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/). If you still prefer pip over the modern and fast package manager [uv](https://github.com/astral-sh/uv), you can install the library like this:


```shell
pip install aignostics        # add dependency to your project
```

Executing the command line interface (CLI) in an isolated Python environment is just as easy:

```shell
uvx aignostics hello-world       # prints "Hello, world! [..]"
uvx aignostics serve             # serves web API
uvx aignostics serve --port=4711 # serves web API on port 4711
```

Notes:
1. The API is versioned, mounted at `/api/v1` resp. `/api/v2`
2. While serving the web API go to [http://127.0.0.1:8000/api/v1/hello-world](http://127.0.0.1:8000/api/v1/hello-world) to see the respons of the `hello-world` operation.
3. Interactive documentation is provided at [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)


The CLI provides extensive help:

```shell
uvx aignostics --help                # all CLI commands
uvx aignostics hello-world --help    # help for specific command
uvx aignostics echo --help
uvx aignostics openapi --help
uvx aignostics serve --help
```


## Operational Excellence

This project is designed with operational excellence in mind, using modern Python tooling and practices. It includes:

1. Various examples demonstrating usage:
  a. [Simple Python script](https://github.com/aignostics/python-sdk/blob/main/examples/script.py)
  b. [Streamlit web application](https://aignostics.streamlit.app/) deployed on [Streamlit Community Cloud](https://streamlit.io/cloud)
  c. [Jupyter](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb) and [Marimo](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.py) notebook
2. [Complete reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html) on Read the Docs
3. [Transparent test coverage](https://app.codecov.io/gh/aignostics/python-sdk) including unit and E2E tests (reported on Codecov)
4. Matrix tested with [multiple python versions](https://github.com/aignostics/python-sdk/blob/main/noxfile.py) to ensure compatibility (powered by [Nox](https://nox.thea.codes/en/stable/))
5. Compliant with modern linting and formatting standards (powered by [Ruff](https://github.com/astral-sh/ruff))
6. Up-to-date dependencies (monitored by [Renovate](https://github.com/renovatebot/renovate) and [Dependabot](https://github.com/aignostics/python-sdk/security/dependabot))
7. [A-grade code quality](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk) in security, maintainability, and reliability with low technical debt and codesmell (verified by SonarQube)
8. Additional code security checks using [CodeQL](https://github.com/aignostics/python-sdk/security/code-scanning)
9. [Security Policy](SECURITY.md)
10. [License](LICENSE) compliant with the Open Source Initiative (OSI)
11. 1-liner for installation and execution of command line interface (CLI) via [uv(x)](https://github.com/astral-sh/uv) or [Docker](https://hub.docker.com/r/helmuthva/aignostics-python-sdk/tags)
12. Setup for developing inside a [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) included (supports VSCode and GitHub Codespaces)


## Usage Examples

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

[Show script code](https://github.com/aignostics/python-sdk/blob/main/examples/script.py) - [Read the reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html)

### Streamlit App

Serve the functionality provided by Aignostics Python SDK in the web by easily integrating the service into a Streamlit application.

[Try it out!](https://aignostics.streamlit.app) - [Show the code](https://github.com/aignostics/python-sdk/blob/main/examples/streamlit.py)

... or serve the app locally
```shell
uv sync --all-extras                                # Install streamlit dependency part of the examples extra, see pyproject.toml
uv run streamlit run examples/streamlit.py          # Serve on localhost:8501, opens browser
```

## Notebooks

### Jupyter

[Show the Jupyter code](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb)

... or run within VSCode

```shell
uv sync --all-extras                                # Install dependencies required for examples such as Juypyter kernel, see pyproject.toml
```
Install the [Jupyter extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

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

Install the [Marimo extension for VSCode](https://marketplace.visualstudio.com/items?itemName=marimo-team.vscode-marimo)

Click on `examples/notebook.py` in VSCode and click on the caret next to the Run icon above the code (looks like a pencil) > "Start in marimo editor" (edit).

## Command Line Interface (CLI)

### Run with [uvx](https://docs.astral.sh/uv/guides/tools/)

Show available commands:

```shell
uvx aignostics --help
```

Execute commands:

```shell
uvx aignostics hello-world
uvx aignostics echo --help
uvx aignostics echo "Lorem"
uvx aignostics echo "Lorem" --json
uvx aignostics openapi
uvx aignostics openapi --output-format=json
uvx aignostics serve
```

### Environment

The service loads environment variables including support for .env files.

```shell
cp .env.example .env              # copy example file
echo "THE_VAR=MY_VALUE" > .env    # overwrite with your values
```

Now run the usage examples again.

### Run with Docker

You can as well run the CLI within Docker.

```shell
docker run helmuthva/aignostics-python-sdk --help
docker run helmuthva/aignostics-python-sdk hello-world
docker run helmuthva/aignostics-python-sdk echo --help
docker run helmuthva/aignostics-python-sdk echo "Lorem"
docker run helmuthva/aignostics-python-sdk echo "Lorem" --json
docker run helmuthva/aignostics-python-sdk openapi
docker run helmuthva/aignostics-python-sdk openapi --output-format=json
docker run helmuthva/aignostics-python-sdk serve
```

Execute command:

```shell
docker run --env THE_VAR=MY_VALUE helmuthva/aignostics-python-sdk echo "Lorem Ipsum"
```

Or use docker compose

The .env is passed through from the host to the Docker container.

```shell
docker compose run aignostics --help
docker compose run aignostics hello-world
docker compose run aignostics echo --help
docker compose run aignostics echo "Lorem"
docker compose run aignostics echo "Lorem" --json
docker compose run aignostics openapi
docker compose run aignostics openapi --output-format=json
docker compose up
curl http://127.0.0.1:8000/api/v1/hello-world
curl http://127.0.0.1:8000/api/v1/docs
curl http://127.0.0.1:8000/api/v2/hello-world
curl http://127.0.0.1:8000/api/v2/docs
```

## Extra: Lorem Ipsum

Dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam.
