
[//]: # (README.md generated from docs/partials/README_*.md)

# 🔬Aignostics Python SDK

[![License](https://img.shields.io/github/license/aignostics/python-sdk?logo=opensourceinitiative&logoColor=3DA639&labelColor=414042&color=A41831)](https://github.com/aignostics/python-sdk/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/aignostics.svg?logo=python&color=204361&labelColor=1E2933)](https://pypi.org/project/aignostics/)
[![CI/CD](https://github.com/aignostics/python-sdk/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/aignostics/python-sdk/actions/workflows/ci-cd.yml)
[![Docs](https://img.shields.io/readthedocs/aignostics)](https://aignostics.readthedocs.io/en/latest/)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Coverage](https://codecov.io/gh/aignostics/python-sdk/graph/badge.svg?token=SX34YRP30E)](https://codecov.io/gh/aignostics/python-sdk)
[![Uptime](https://uptime.betterstack.com/status-badges/v2/monitor/1wbqa.svg)](https://aignostics.betteruptime.com)

> [!NOTE]
> The Aignostics Python SDK is in alpha, with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) running on the [Aignostics Platform](https://platform.aignostics.com) being in [early access](https://www.linkedin.com/posts/aignostics_introducing-atlas-he-tme-aignostics-is-activity-7325865745827979265-Sya9?utm_source=share&utm_medium=member_desktop&rcm=ACoAABRmV7cBCGv8eM_ot_kRTrBsb12olQvoLS4). 
> Watch or star this repository to receive updates on new features and improvements of the Aignostics Python SDK.

---


## Introduction

The Aignostics Python SDK includes multiple pathways to interact with the
Aignostics Platform:

1. Use the **Aignostics Launchpad** to analyze whole slide images with AI applications like 
   [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product).
   This desktop application runs seamlessly on Mac OS X, Windows, and Linux.
   View your results by launching popular tools such as [QuPath](https://qupath.github.io/) and Python Notebooks with one click.
2. Use the **Aignostics CLI** to run AI applications directly from your terminal. 
   This command-line interface lets you query public datasets from the [NCI Image Data Commons (IDC)](https://portal.imaging.datacommons.cancer.gov/),
   process both public and private whole slide images, and easily download results.
3. Use the included **example notebooks** as starting points to run AI applications
   directly from your preferred notebook environment.
4. Use the **Aignostics Client** to seamlessly integrate the Aignostics Platform with your enterprise image management systems and scientific workflows.
   The client provides a simple way to access the Aignostics Platform API from your Python codebase.

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

## Aignostics Launchpad: Run your first AI analysis in minutes from your desktop

1. Visit the [Quick Start](https://platform.aignostics.com/getting-started/quick-start) 
   page in the Aignostics Platform Web Console.
2. Copy the installation script and paste it into your terminal - compatible with MacOS, Windows, and Linux.
3. Launch the application by running `uvx aignostics launchpad`.
4. Follow the intuitive graphical interface to analyze public datasets or your own whole slide images 
   with [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) and other AI applications.

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


## API Concepts

If you use other languages then Python in your codebase you can natively
integrate with the webservice API of the aignostics platform. 
The following sections outline the main concepts of the API and how to use it.

### Overview
The Aignostics Platform is a comprehensive cloud-based service that allows organizations to leverage advanced computational pathology applications without the need for specialized on-premises infrastructure. With its API (described in details below) it provides a standardized, secure interface for accessing Aignostics' portfolio of computational pathology applications. These applications perform advanced tissue and cell analysis on histopathology slides, delivering quantitative measurements, visual representations, and detailed statistical data.

### Key Features
Aignostics Platform offers key features designed to maximize value for its users:

* **High-throughput processing:** You can submit 500 whole slide images (WSI) in one request
* **Multi-format support:** Support for commonly used pathology image formats (TIF, DICOM, SVS)
* **Access to Aignostics applications:** Integration with Aignostics computational pathology application like Atlas H&E TME
* **Secure Data Handling:** Maintain control of your slide data through secure self-signed URLswithout needing to transfer files into foreign organization infrastructure
* **Incremental Results Delivery:** Access results for individual slides as they complete processing, without waiting for the entire batch to finish
* **Flexible Integration:** Integrate access to Aignostics applications with your existing systems through our API

### Registration and Access
To begin using the Aignostics Platform and its applications, your organization must first be registered by our team. Currently, account creation is not self-service. Please contact us to initiate the registration process.

1. Access to the Aignostics Platform requires a formal business agreement. Once an agreement is in place between your organization and Aignostics, we will proceed with your organization's registration. If your organization does not yet have an account, please contact your dedicated account manager or email us at support@aignostics.com to express your interest.
2. To register your organization, we require the name and email address of at least one employee, who will be assigned the Organization Admin role. This user will act as the primary administrator for your organization on the platform.
3. The Organization Admin can invite and manage additional users within the same organization though a dedicated Platform Dashboard. Please note:
   1. All user accounts must be associated with your organization's official domain.
   2. We do not support the registration of private or personal email addresses.
   3. For security, Two-Factor Authentication (2FA) is mandatory for all user accounts.

The entire process typically takes 2 business days depending on the complexity of the business agreement and specific requirements.

### User management
AIgnostics Platform is available to users registered in the platform. The client organization is created by the Aignostics business support team (super admin). The customer becomes the member of the organization.

Admin of the organization can add more users, admins or members. Both roles can trigger application runs, but additionally to that admins can manage users of the organization.

### Applications
An application is a fully automated end-to-end workflow composed of one or more specific tasks (Tissue Quality Control, Tissue Segmentation, Cell Detection and Classification…). Each application is designed for a particular analysis purpose (e.g. TME analysis, biomarker scoring). For each application we define input requirements, processing tasks and output formats.

Each application can have multiple versions. Applications and its versions are assigned to your organization by Aignostics based on business agreement. Please make sure you read dedicated application documentation to understand its specific constraints regarding acceptable formats, staining method, tissue types and diseases.

Once registered to the Platform, your organization will automatically gain access to the test application for free. This application can be used to configure the workflow and to make sure that the integration works correctly, without any extra cost.

### Application run
To trigger the application run, users can use the Python client, or the REST API. The platform expects the user payload, containing the metadata of the slides and the signed URLs to the WSIs. The detailed description of the payload is different for every application and described via the /v1/applications endpoint.

When the application run is created, it can be in one of the following states:

* **received** - the application run received from the client
* **scheduled** - the application run request is valid and is scheduled for execution
* **running** - the application run execution started
* **completed** - the application run execution is done and all outputs are available for download
* **completed** with error - the application run execution is done, but some items end up in the failed state
* **rejected** - the application run request is rejected before it is scheduled
* **cancelled by the system** - the application run failed during the execution with the number of errors higher than the threshold
* **cancelled by the user** - the application run is cancelled by the user before it is finished

Only the user who created the application run can check its status, retrieve results or cancel its execution.

### Results
When the processing of an image is successfully completed, the resulting outputs become available for the download. To assess specifics of application outputs please consult application specific documentation, which you can find available in Aignostics Platform Dashboard. You will receive access to application documentations only for those applications that are available to your organization.

Application run outputs are automatically deleted 30 days after the application run has completed. However, the owner of the application run (the user who initiated it) can use the API to manually delete outputs earlier, once the run has reached a final state - completed, cancelled by the system or cancelled by the user.

### Quotas
Every organization has a limit on how many WSIs it can process in a calendar month. The following quotas exist:

* **For an organization** - assigned by the Aignostics based on defined business agreement with the organization
* **For a user** - assigned by the organization Admin to the user

When the per month quota is reached, the application run request is denied.

Other limitations may apply to your organization:

* Allowed number of users an organization can register
* Allowed number of images user can submit in one application run
* Allowed number of parallel application runs for the whole organization

Additionally, we allow organization Admin to define following limitations for its users:

* Maximum number of images the user can process per calendar month.
* Maximum number of parallel application runs for a user

To view the quota and the quota usage, please access Platform Dashboard.

### Cost
Every WSI processed by the Platform generates a cost. Usage of test application doesn't generate any cost and is free for any registered user.

When the application run is cancelled, either by the system or by the user, only the processed images are added to the cost for your organization.

**[Read the API reference documentation](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html) to learn about all operations and parameters.**


## Further Reading

1. Inspect our
   [security policy](https://aignostics.readthedocs.io/en/latest/security.html)
   with detailed documentation of checks, tools and principles.
2. Check out the
   [CLI reference](https://aignostics.readthedocs.io/en/latest/cli_reference.html)
   with detailed documentation of all CLI commands and options.
3. Check out the
   [library reference](https://aignostics.readthedocs.io/en/latest/lib_reference.html)
   with detailed documentation of public classes and functions.
4. Check out the
   [API reference](https://aignostics.readthedocs.io/en/latest/api_reference_v1.html)
   with detailed documentation of all API operations and parameters.
5. Our
   [release notes](https://aignostics.readthedocs.io/en/latest/release-notes.html)
   provide a complete log of recent improvements and changes.
6. We gratefully acknowledge the
   [open source projects](https://aignostics.readthedocs.io/en/latest/attributions.html)
   that this project builds upon. Thank you to all these wonderful contributors!
