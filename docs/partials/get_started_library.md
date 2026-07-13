# Get started with the Python Library

The **Aignostics Python Library** lets you call the Aignostics Platform programmatically from your own scripts, notebooks, and applications. It is well suited to building custom analysis pipelines and processing large datasets in Python.

```{include} ../partials/_get_started_signup.md
```

## Install the library

Add the Aignostics Python SDK to your project.

**With [uv](https://docs.astral.sh/uv/):**

```shell
uv add aignostics
```

**With [pip](https://pip.pypa.io/en/stable/):**

```shell
pip install aignostics
```

## Usage

The following snippet shows how to use the client to submit an application run:

```python
from aignostics import platform

# initialize the client
client = platform.Client()
# submit an application run
application_run = client.runs.submit(
    application_id="test-app",
    items=[
        platform.InputItem(
            external_id="slide-1",
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url="<a signed url to download the data>",
                    metadata={
                        "checksum_base64_crc32c": "AAAAAA==",
                        "resolution_mpp": 0.25,
                        "width_px": 1000,
                        "height_px": 1000,
                    },
                )
            ],
        ),
    ],
)
# wait for the results and download incrementally as they become available
application_run.download_to_folder("path/to/download/folder")
```

See the [library reference](https://aignostics.readthedocs.io/en/latest/lib_reference.html) for all classes and methods.

## System health checks

The library does **not** perform automated health checks before operations. If you need health verification, implement it in your application logic:

```python
from aignostics import platform
from aignostics.system import Service as SystemService

# Check system health before submitting runs
health = SystemService().health()
if not health:
    raise RuntimeError(f"System is unhealthy: {health.reason}")

# Proceed with run submission
client = platform.Client()
run = client.runs.submit(...)
```

This gives you full control over health-check behavior — custom retry logic, logging, and graceful handling of unhealthy states.

## Example notebooks

> [!IMPORTANT]
> Before you start, set up your authentication credentials if you have not done so. Visit
> [your personal dashboard on the Aignostics Platform website](https://platform.aignostics.com/getting-started/quick-start)
> and follow the steps in the `Use in Python Notebooks` section.

The SDK includes ready-to-use [Marimo](https://marimo.io/) notebooks that demonstrate platform interaction patterns — ideal for learning the API, prototyping workflows, and integrating with data science pipelines. They use the "Test Application" (free for all users):

```shell
# clone the python-sdk repository
git clone https://github.com/aignostics/python-sdk.git
# within the cloned repository, install the SDK and all dependencies
uv sync --all-extras
# open the example notebook in your browser
uv run marimo edit examples/notebook.py
```

> 💡 You can also run a notebook inside the Aignostics Launchpad: select the run you want to inspect in the left sidebar and click **Marimo**.

## Defining the input for an application run

The following details apply to advanced use cases. These examples use the "Test Application" — a free application available to all users for testing and development.

When creating a run, you specify the `application_id` and optionally the `application_version`. If you omit the version, the latest is used automatically. You then define the input items to process:

```python
(
    platform.InputItem(
        external_id="1",
        input_artifacts=[
            platform.InputArtifact(
                name="whole_slide_image",  # defined by the application version's input artifact schema
                download_url="<a signed url to download the data>",
                metadata={  # defined by the application version's input artifact schema
                    "checksum_base64_crc32c": "N+LWCg==",
                    "resolution_mpp": 0.46499982,
                    "width_px": 3728,
                    "height_px": 3640,
                },
            )
        ],
    ),
)
```

For each item you process, provide a unique `external_id` string — it is used to match results back to your inputs. The `input_artifacts` field is a list of `InputArtifact` objects defining the data and metadata for each item. The required artifacts depend on the application version; for the test application there is a single artifact, named `whole_slide_image`.

The `download_url` is a signed URL that allows the Aignostics Platform to download the image data during processing.

## Self-signed URLs for large files

To make whole slide images available to the Aignostics Platform, you provide a signed URL the platform can download from. Signed URLs for files in Google Cloud Storage buckets can be generated with `generate_signed_url` ([code](https://github.com/aignostics/python-sdk/blob/main/src/aignostics/platform/_utils.py)).

**You must provide the [required credentials](https://cloud.google.com/docs/authentication/application-default-credentials) for the Google Cloud Storage bucket.**

```{include} ../partials/_invite_your_team.md
```
