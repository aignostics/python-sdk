from aignx.codegen.models import ItemCreationRequestfrom aignx.codegen.models import ItemCreationRequestfrom aignx.codegen.models import RunCreationRequest

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

## Using the Python SDK in your Codebase

The following sections showcase how you can integrate the Python SDK in your codebase.

### Installation

Adding Aignostics Python SDK to your codebase as a dependency is easy. 
You can directly import add the dependency via your favourite package manager, 
e.g., [pip](https://pip.pypa.io/en/stable/) or [uv](https://docs.astral.sh/uv/).

**Install with uv** -- If you don't have uv installed follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/).
```shell
uv add aignostics                       # add SDK as dependency to your project
```

**Install with pip**
```shell
pip install aignostics                  # add SDK as dependency to your project
```

### Usage

Read the [client reference documentation](https://aignostics.readthedocs.io/en/latest/lib_reference.html) to learn about all classes and methods.

The following snippets showcase the basic code to run an application with the Python SDK. 
A more detailed example - including comments - is available in the `examples` folder as Python notebooks: 
[examples/notebook.ipynb](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb) (IPython) 
[examples/notebook.py](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.py) (Marimo).

```python
import aignostics.client
from aignx.codegen.models import (
    ApplicationVersion,
    RunCreationRequest,
    ItemCreationRequest
)

# initialize the client
client = aignostics.client.Client()
# trigger an application run
application_run = client.runs.create(
    RunCreationRequest(
        application_version=ApplicationVersion("..."),
        items=[
           ItemCreationRequest(...)
        ],
    )
)
# wait for the results and download incrementally as they become available
application_run.download_to_folder("path/to/download/folder")
```

### Authentication Setup
The SDK uses the [OAuth2](https://oauth.net/2/) protocol for authentication. 
Please visit [your personal dashboard on the aignostics platform](https://platform.aignostics.com) and scroll to the "Python SDK" section
to find your personalized setup instructions.

### Application Run Payloads

The payload expected to trigger an application run is specified by the `RunCreationRequest` pydantic model:
```python
RunCreationRequest(
   application_version=...,
   items=[
      ItemCreationRequest(...),
      ItemCreationRequest(...)
   ]
)
```
Next to the application version of the application you want to run, 
it defines the items you want to be processed as `ItemCreationRequest` objects:
```python
ItemCreationRequest(
    reference="1",
    input_artifacts=[
        InputArtifactCreationRequest(
            name="user_slide", # defined by the application version input_artifact schema
            download_url="<a signed url to download the data>",
            metadata={ # defined by the application version input_artifact schema
                "checksum_crc32c": "N+LWCg==",
                "base_mpp": 0.46499982,
                "width": 3728,
                "height": 3640,
            },
        )
    ],
),
```
For each item you want to process, you need to provide a unique `reference` string. 
This is used to identify the item in the results later on. 
The `input_artifacts` field is a list of `InputArtifactCreationRequest` objects, which defines what data & metadata you need to provide for each item.
The required artifacts depend on the application version you want to run - in the case of test application, there is only one artifact required, which is the image to process on.
The artifact name is defined as `user_slide`. 

The `download_url` is a signed URL that allows the Aignostics Platform to download the image data later during processing.

#### Self-signed URLs for large files

To make the images you want to process available to the Aignostics Platform, you need to provide a signed URL that allows the platform to download the data.
Self-signed URLs for files in google storage buckets can be generated using the `generate_signed_url` ([code](https://github.com/aignostics/python-sdk/blob/407e74f7ae89289b70efd86cbda59ec7414050d5/src/aignostics/client/utils.py#L85)).

**We expect that you provide the [required credentials](https://cloud.google.com/docs/authentication/application-default-credentials) for the Google Storage Bucket**

## Run with Docker

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
