## Introduction

The aignostics Python SDK opens multiple pathways to interact with the
aignostics platform:

1. **Run AI applications** such as
   [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product)
   directly from your terminal using the **Command Line Interface (CLI)**
   included in the SDK.
2. Call applications directly from **Python Noebooks** following the provided
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
