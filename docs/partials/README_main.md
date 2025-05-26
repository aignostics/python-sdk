## Introduction

The **Aignostics Python SDK** includes multiple pathways to interact with the
**Aignostics Platform**:

1. Use the **Aignostics Launchpad** to analyze whole slide images with advanced computational pathology applications like 
   [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) directly from your desktop.
   View your results by launching popular tools such as [QuPath](https://qupath.github.io/) and Python Notebooks with one click.
   The app runs on Mac OS X, Windows, and Linux.
2. Use the **Aignostics Command-line interface (CLI)** to run applications directly from your terminal or shell scripts.
   THe CLI lets you query public datasets from the [NCI Image Data Commons (IDC)](https://portal.imaging.datacommons.cancer.gov/),
   process both public and private whole slide images, and easily download results. The CLI is available for Mac OS X, Windows, and Linux.
3. Use the included **example notebooks** as starting points to run applications
   directly from your preferred notebook environment. We support Marimo and Jupyter based notebooks environments including Google Collab.
4. Use the **Aignostics Client Library** to seamlessly integrate the Aignostics Platform with your enterprise image management systems and scientific workflows.
   The client provides a simple way to access the Aignostics Platform API from your Python codebase. We support Python 3.11 and above.

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

## Quick Start

> [!Note]
> See as follows for a quick start guide to get you up and running with the Aignostics Python SDK as quickly as possible. 
> If you first want to learn bout the basic concepts and components of the Aignostics Platform skip to that section below. 
> The further reading section points you to reference documentation listing all available CLI commans, methods and classes provided by the SDK, how we achieve operational excellence and security, and more. 
> If you are not familiar with terminology please check the glossary at the end of this document.

### Launchpad: Run your first computational pathology analysis in 10 minutes from your desktop

The **Aignostics Launchpad** is a graphical desktop application that allows you to run
applications on whole slide images (WSIs) from your computer, and inspect results with QuPath and Python Notebooks with one click. It is designed to be user-friendly and intuitive, for use by Research Pathologists and Data Scientists. 

The Launchpad is available for Mac OS X, Windows, and Linux, and can be installed easily:

1. Visit the [Quick Start](https://platform.aignostics.com/getting-started/quick-start) 
   page in the Aignostics Console.
2. Copy the installation script and paste it into your terminal - compatible with MacOS, Windows, and Linux.
3. Launch the application by running `uvx aignostics launchpad`.
4. Follow the intuitive graphical interface to analyze public datasets or your own whole slide images 
   with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) and other computational pathology applications.

### CLI: Manage datasets and application runs from your terminal

The Python SDK includes the **Aignostics CLI**, a Command-Line Interface that allows you to
interact with the Aignostics Platform directly from your terminal or shell script.

See as follows for a simple example where we download a sample dataset for the [Atlas
H&E-TME application](https://www.aignostics.com/products/he-tme-profiling-product), submit an application run, and download the results.

```shell
# Download a sample dataset from the NCI Image Data Commons (IDC) portal to your current working directory
# As the dataset id refers to the TCGA LUAD collection, this creates a directory tcga_luad with the DICOM files
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 data/
# Prepare the metadata for the application run by creating a metadata.csv, extracting 
# the required metadata from the DICOM files. We furthermore add the required
# information about the tissue type and disease. TODO (Helmut): Update
uvx aignostics application run prepare he-tme data/tcga_luad/run.csv data/
# Edit the metadata.csv to insert the required information about the staining method, tissue type and disease
# Adapt to your favourite editor
nano tcga_luad/metadata.csv 
# Upload the metadata.csv and referenced whole slide images to the Aignostics Platform
uvx aignostics application run upload he-tme data/tcga_luad/run.csv
# Submit the application run and print tha run id
uvx aignostics application run submit he-tme data/tcga_luad/run.csv
# Check the status of the application run you triggered
uvx aignostics application run list
# Incrementally download results when they become available
# Fill in the id from the output in the previous step
uvx aignostics application run result download APPLICATION_RUN_ID 
```

For convenience the the `application run execute` command combines preparation, upload, submission and download.
The below is equivalent to the above, while adding additionally required metadata using a mapping

```shell
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 data/
uvx aignostics application run execute he-tme data/tcga_luad/run.csv data/ ".*\.dcm:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"
```

The CLI provides extensive help:

```shell
uvx aignostics --help                           # list all spaces such as application, dataset, bucket and system, 
uvx aignostics application --help               # list subcommands in the application space
uvx aignostics application run --help           # list subcommands in the application run sub-space
uvx aignostics application run list --help      # show help for specific command
uvx aignostics application run execute --help   # show help for another command
```

Check out our
[CLI reference documentation](https://aignostics.readthedocs.io/en/latest/reference.html#cli)
to learn about all commands and options available.

### Example Notebooks: Interact with the Aignostics Platform from your Python Notebook environment

> [!IMPORTANT]
> Before you get started, you need to set up your authentication credentials if
> you did not yet do so! Please visit
> [your personal dashboard on the Aignostics Platform website](https://platform.aignostics.com/getting-started/quick-start)
> and follow the steps outlined in the `Use in Python Notebooks` section.

The Python SDK includes Jupyter and Marimo notebooks to help you get started interacting 
with the Aignostics Platform in your notebook environment.

The notebooks showcase the interaction with the Aignostics Platform using our "Test Application". To run one them, 
please follow the steps outlined in the snippet below to clone this repository and start either the
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

> [!Note]
> You can as well run a notebook within the Aignostics Launchpad. To do so, select the
> Run you want to inspect in the left sidebar, and click the button "Open in Python Notebook".

### Client Library: Call the Aignostics Platform API from your Python scripts

> [!IMPORTANT]\
> Before you get started, you need to set up your authentication credentials if
> you did not yet do so! Please visit
> [your personal dashboard on the Aignostics Platform website](https://platform.aignostics.com/getting-started/quick-start)
> and follow the steps outlined in the `Enterprise Integration` section.

Next to using the Launchpad, CLI and example notebooks, the Python SDK includes the
*Aignostics Client Library* for integration with your Python Codebase.

The following sections outline how to install the Python SDK for this purpose and 
interact with the Client.

### Installation

The Aignostics Python SDK is published on the [Python Package Index (PyPI)](https://pypi.org/project/aignostics/), 
is compatible with Python 3.11 and above, and can be installed via via `uv` or `pip`:

**Install with [uv](https://docs.astral.sh/uv/):** If you don't have uv
installed follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/).

```shell
# Add Aignostics Python SDK as dependency to your project
uv add aignostics
```

**Install with [pip](https://pip.pypa.io/en/stable/)**

```shell
# Add Python SDK as dependency to your project
pip install aignostics
```

#### Usage

The following snippet shows how to use the Client to trigger an application
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

##### Defining the input for an application run

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

To make the whole slide images you want to process available to the Aignostics Platform, you
need to provide a signed URL that allows the platform to download the data.
Self-signed URLs for files in google storage buckets can be generated using the
`generate_signed_url`
([code](https://github.com/aignostics/python-sdk/blob/407e74f7ae89289b70efd86cbda59ec7414050d5/src/aignostics/client/utils.py#L85)).

**We expect that you provide the
[required credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
for the Google Storage Bucket**
