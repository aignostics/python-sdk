## Introduction

The Aignostics Python SDK includes multiple pathways to interact with the
Aignostics Platform:

1. Use the **Aignostics Launchpad** to analyze your whole slide images 
   with our AI applications and inspect the results with common tools
   such as [QuPath](https://qupath.github.io/) and Python Notebooks.
   The Launchpad is a user-friendly desktop application running on
   MacOS X, Windows and Linux that allows you to easily upload your data 
   without needing to write any code.
2. Use the **Aignostics CLI** to run AI applications
   directly from your terminal. The Aignostics Command Line Interface (CLI) allows to query public datasets provided by [NCI Image Data Commons (IDC)](https://portal.imaging.datacommons.cancer.gov/), 
   run applications on public and private whole slide images, and download results.
3. Use the included **example** notebook as a starting point to run AI applications
   directly from your notebook environment. 
4. Use the **Aignostics Client** to deeply integrate the Aignostics Platform with your enterprise image management systems and scientific workflows.
   The client makes it easy to call the Aignostics Platform API from your Python codebase.

### We take quality and security seriously

We know you take **quality** and **security** as seriously as we do. That's why
the Aignostics Python SDK is built following best practices and with full
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
[operational excellence](https://aignostics.readthedocs.io/en/latest/operational_excellence.html) and
[security](https://aignostics.readthedocs.io/en/latest/security.html).

## Aignostics Launchpad: Run your first AI workflow in 10 minutes from your Desktop

1. Go to [Quick Start](https://platform.aignostics.com/getting-started/quick-start)
in the Web Console of the Aignostics Platform. 
2. Copy and paste the install script into your terminal - we support MacOS, Windows and Linux. 
This will install the [uv package manager](https://github.com/astral-sh/uv) and this
Python SDK.
3. Execute `uvx aignostics launchpad` to open the included desktop application.
4. Follow the instructions in the application to run your first AI workflow.

## Aignostics CLI: Manage datasets and application runs from your terminal

The Python SDK includes a Command Line Interface (CLI) that allows you to
interact with the Aignostics Platform directly from your terminal.

See as follows for a simple example where we download a sample dataset for the Atlas
H&E-TME application, submit an application run, and download the results.

```shell
# Download a sample dataset from the NCI Image Data Commons (IDC) portal to your current working directory
# As the dataset id refers to the TCGA LUAD collection, this creates a directory tcga_luad with the DICOM files
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 .
# Prepare the metadata for the application run by creating a metadata.csv, extracting 
# the required metadata from the DICOM files. We furthermore add the required
# information about the tissue type and disease. TODO (Helmut): Update
uvx aignostics application run prepare he-tme:v0.50.0 tcga_luad/metadata.csv tcga_luad
# Edit the metadata.csv to insert the required information about the tissue type and disease
nano tcga_luad/metadata.csv # Adapt to your favourite editor
# Upload the metadata.csv and referenced whole slide images to the Aignostics Platform
uvx aignostics application run upload he-tme:v0.50.0 tcga_luad/metadata.csv
# Submit the application run and print tha run id
uvx aignostics application run submit he-tme:v0.50.0 tcga_luad/metadata.csv
# Check the status of the application run you triggered
uvx aignostics application run list
uvx aignostics application run result dowload APPLICATION_RUN_ID # Fill in the application run id
```

The CLI provides extensive help:

```shell
uvx aignostics --help                   # all subcommands
uvx aignostics application --help       # list subcommands in the application space
uvx aignostics application list --help  # help for specific command
uvx aignostics application run --help.  # list subcommands in the application run space
```

Check out our
[CLI reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html#cli)
to learn about all commands and options available.

## Examples: Interact with the Aignostics Platform from your Python Notebook environment

> [!IMPORTANT]\
> Before you get started, you need to set up your authentication credentials if
> you did not yet do so! Please visit
> [your personal dashboard on the Aignostics Platform website](https://platform.aignostics.com/getting-started/quick-start)
> and follow the steps outlined in the `Use in Python Notebooks` section.

We provide Jupyter and Marimo notebooks to help you get started with the SDK.
The notebooks showcase the interaction with the Aignostics Platform using our
test application. To run one them, please follow the steps outlined in the
snippet below to clone this repository and start either the
[Jupyter](https://docs.jupyter.org/en/latest/index.html)
([examples/notebook.ipynb](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.ipynb))
or [Marimo](https://marimo.io/)
([examples/notebook.py](https://github.com/aignostics/python-sdk/blob/main/examples/notebook.py))
notebook:

```shell
# clone the `python-sdk` repository
git clone https://github.com/aignostics/python-sdk.git
# within the cloned repository, install the SDK and all dependencies
uv sync --all-extras
# show jupyter example notebook in the browser
uv run jupyter notebook examples/notebook.ipynb
# show marimo example notebook in the browser
uv run marimo edit examples/notebook.py
```

## Aignostics Client: Call the Aignostics Platform API from your Python scripts

> [!IMPORTANT]\
> Before you get started, you need to set up your authentication credentials if
> you did not yet do so! Please visit
> [your personal dashboard on the Aignostics Platform website](https://platform.aignostics.com/getting-started/quick-start)
> and follow the steps outlined in the `Enterprise Integration` section.

Next to using the CLI and notebooks, you can also use the Python SDK in your
codebase. The following sections outline how to install the SDK and interact
with it.

### Installation

Adding Aignostics Python SDK to your codebase as a dependency is easy. You can
directly add the dependency via your favourite package manager:

**Install with [uv](https://docs.astral.sh/uv/):** If you don't have uv
installed follow
[these instructions](https://docs.astral.sh/uv/getting-started/installation/).

```shell
# add SDK as dependency to your project
uv add aignostics
```

**Install with [pip](https://pip.pypa.io/en/stable/)**

```shell
# add SDK as dependency to your project
pip install aignostics
```

### Usage

The following snippet shows how to use the Python SDK to trigger an application
run:

```python
from aignostics import platform

# initialize the client
client = platform.Client()
# trigger an application run
application_run = client.runs.create(
   application_version="two-task-dummy:v0.35.0",
   items=[
      platform.InputItem(
         reference="slide-1",
         input_artifacts=[
            platform.InputArtifact(
               name="user_slide",
               download_url="<a signed url to download the data>",
               metadata={
                  "checksum_crc32c": "AAAAAA==",
                  "base_mpp": 0.25,
                  "width": 1000,
                  "height": 1000,
               },
            )
         ],
      ),
   ],
)
# wait for the results and download incrementally as they become available
application_run.download_to_folder("path/to/download/folder")
```

Please look at the notebooks in the `example` folder for a more detailed example
and read the
[client reference documentation](https://aignostics.readthedocs.io/en/latest/lib_reference.html)
to learn about all classes and methods.

#### Defining the input for an application run

Next to the `application_version` of the application you want to run, you have
to define the input items you want to process in the run. The input items are
defined as follows:

```python
platform.InputItem(
    reference="1",
    input_artifacts=[
        platform.InputArtifact(
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

For each item you want to process, you need to provide a unique `reference`
string. This is used to identify the item in the results later on. The
`input_artifacts` field is a list of `InputArtifact` objects, which defines what
data & metadata you need to provide for each item. The required artifacts depend
on the application version you want to run - in the case of test application,
there is only one artifact required, which is the image to process on. The
artifact name is defined as `user_slide`.

The `download_url` is a signed URL that allows the Aignostics Platform to
download the image data later during processing.

#### Self-signed URLs for large files

To make the images you want to process available to the Aignostics Platform, you
need to provide a signed URL that allows the platform to download the data.
Self-signed URLs for files in google storage buckets can be generated using the
`generate_signed_url`
([code](https://github.com/aignostics/python-sdk/blob/407e74f7ae89289b70efd86cbda59ec7414050d5/src/aignostics/client/utils.py#L85)).

**We expect that you provide the
[required credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
for the Google Storage Bucket**
