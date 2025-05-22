# CLI Reference

Command Line Interface (CLI) of Aignostics Python SDK providing access to Aignostics Platform.

**Usage**:

```console
$ aignostics [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

🔬 Aignostics Python SDK v0.2.0 - built with love in Berlin 🐻

**Commands**:

* `launchpad`: Open Aignostics Launchpad, the graphical...
* `notebook`: Run Python notebook server based on Marimo.
* `application`: List and inspect applications on...
* `bucket`: Operations on cloud bucket on Aignostics...
* `dataset`: Download datasets from National Institute...
* `system`: Determine health, info and further...
* `wsi`: Operations on whole slide images.

## `aignostics launchpad`

Open Aignostics Launchpad, the graphical user interface of the Aignostics Platform.

**Usage**:

```console
$ aignostics launchpad [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics notebook`

Run Python notebook server based on Marimo.

**Usage**:

```console
$ aignostics notebook [OPTIONS]
```

**Options**:

* `--host TEXT`: Host to bind the server to  [default: 127.0.0.1]
* `--port INTEGER`: Port to bind the server to  [default: 8001]
* `--help`: Show this message and exit.

## `aignostics application`

List and inspect applications on Aignostics Platform.

**Usage**:

```console
$ aignostics application [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List available applications.
* `describe`: Describe application.
* `run`: List, submit and manage application runs

### `aignostics application list`

List available applications.

Args:
    verbose (bool): If True, show detailed information about each application

Returns:
    bool: Success status of the operation

**Usage**:

```console
$ aignostics application list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Show application details  [default: no-verbose]
* `--help`: Show this message and exit.

### `aignostics application describe`

Describe application.

Args:
    application_id (str): The ID of the application to describe

Returns:
    bool: Success status of the operation

**Usage**:

```console
$ aignostics application describe [OPTIONS] APPLICATION_ID
```

**Arguments**:

* `APPLICATION_ID`: Id of the application to describe  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics application run`

List, submit and manage application runs

**Usage**:

```console
$ aignostics application run [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `prepare`: Prepare metadata CSV file required for...
* `upload`: Upload files referenced in the metadata...
* `submit`: Submit run by referencing the metadata CSV...
* `list`: List application runs, sorted by...
* `describe`: Describe application run.
* `cancel`: Cancel application run.
* `result`: Inspect and download application run results

#### `aignostics application run prepare`

Prepare metadata CSV file required for submitting a run.

1. Scans source_directory for whole slide images (.tif, .tiff and .dcm)
2. Extracts metadata from whole slide images such as width, height, mpp
3. Creates CSV file with metadata as required for the given application version

Args:
    application_version_id (str): The ID of the application version to generate metadata for
    metadata_csv (str): The target filename for the generated metadata file.
    source_directory (str): The source directory to scan for whole slide images

**Usage**:

```console
$ aignostics application run prepare [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV SOURCE_DIRECTORY
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application to generate the metadata for  [required]
* `METADATA_CSV`: Target filename for the generated metadata file. .csv will be appended automatically.  [required]
* `SOURCE_DIRECTORY`: Source directory to scan for whole slide images  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run upload`

Upload files referenced in the metadata CSV file to the Aignostics platform.

1. Reads the metadata CSV file
2. Uploads the files referenced in the CSV file to the Aignostics platform
3. Incrementally updates the CSV file with upload progress and the signed URLs for the uploaded files

Args:
    application_version_id (str): The ID of the application version to generate the metadata for
    metadata_csv_file (str): The metadata file containing the references to whole slide images.
    upload_prefix (str): The prefix for the upload destination. If not given, will be set to current milliseconds.

Returns:
    bool: Success status of the operation

**Usage**:

```console
$ aignostics application run upload [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV_FILE
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application to generate the metadata for  [required]
* `METADATA_CSV_FILE`: Filename of the .csv file containing the metadata and references.  [required]

**Options**:

* `--upload-prefix TEXT`: Prefix for the upload destination. If not given will be set to current milliseconds.  [default: 1747952510754.803]
* `--help`: Show this message and exit.

#### `aignostics application run submit`

Submit run by referencing the metadata CSV file.

1. Requires the metadata CSV file to be generated and referenced files uploaded first

Args:
    application_version_id (str): The ID of the application version to submit a run for
    metadata_csv_file (str): The metadata file containing the references to whole slide images
        and their metadata to submit.

Returns:
    bool: Success status of the operation

**Usage**:

```console
$ aignostics application run submit [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV_FILE
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application version to submit run for  [required]
* `METADATA_CSV_FILE`: Filename of the .csv file containing the metadata and references.  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run list`

List application runs, sorted by triggered_at, descending.

Args:
    verbose (bool): If True, show detailed information about each run.
    limit (int | None): Maximum number of runs to display. If None, display all runs.

Returns:
    int: Number of runs found, or -1 if an error occurred

**Usage**:

```console
$ aignostics application run list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Show application details  [default: no-verbose]
* `--limit INTEGER`: Maximum number of runs to display
* `--help`: Show this message and exit.

#### `aignostics application run describe`

Describe application run.

Args:
    run_id (str): The ID of the run to describe

Returns:
    bool: Success status of the operation

**Usage**:

```console
$ aignostics application run describe [OPTIONS] RUN_ID
```

**Arguments**:

* `RUN_ID`: Id of the run to describe  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run cancel`

Cancel application run.

Args:
    run_id(str): The ID of the run to cancel

Returns:
    bool: True if the run was canceled successfully, False otherwise

**Usage**:

```console
$ aignostics application run cancel [OPTIONS] RUN_ID
```

**Arguments**:

* `RUN_ID`: Id of the run to cancel  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run result`

Inspect and download application run results

**Usage**:

```console
$ aignostics application run result [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `describe`: Describe the result of an application run.
* `download`: Download the results of an application run.
* `delete`: Delete the results of an application run.

##### `aignostics application run result describe`

Describe the result of an application run.

**Usage**:

```console
$ aignostics application run result describe [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `aignostics application run result download`

Download the results of an application run.

Args:
    run_id (str): The ID of the run to download results for
    destination_directory (str): The destination directory to download results to

Returns:
    bool: True if the download was successful, False otherwise

**Usage**:

```console
$ aignostics application run result download [OPTIONS] RUN_ID DESTINATION_DIRECTORY
```

**Arguments**:

* `RUN_ID`: Id of the run to download results for  [required]
* `DESTINATION_DIRECTORY`: Destination directory to download results to  [required]

**Options**:

* `--help`: Show this message and exit.

##### `aignostics application run result delete`

Delete the results of an application run.

**Usage**:

```console
$ aignostics application run result delete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics bucket`

Operations on cloud bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `upload`: Upload file or directory to bucket in...
* `ls`: List objects in bucket on Aignostics...
* `find`: Find objects in bucket on Aignostics...
* `delete`: Find objects in bucket on Aignostics...
* `purge`: Purge all objects in bucket on Aignostics...

### `aignostics bucket upload`

Upload file or directory to bucket in Aignostics platform.

**Usage**:

```console
$ aignostics bucket upload [OPTIONS] SOURCE
```

**Arguments**:

* `SOURCE`: Source file or directory to upload  [required]

**Options**:

* `--destination-prefix TEXT`: Destination layout. Supports {username}, {timestamp}. E.g. you might want to use &quot;{username}/myproject/&quot;  [default: {username}]
* `--help`: Show this message and exit.

### `aignostics bucket ls`

List objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket ls [OPTIONS]
```

**Options**:

* `--detail / --no-detail`: Show details  [default: no-detail]
* `--help`: Show this message and exit.

### `aignostics bucket find`

Find objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket find [OPTIONS]
```

**Options**:

* `--detail / --no-detail`: Show details  [default: no-detail]
* `--help`: Show this message and exit.

### `aignostics bucket delete`

Find objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket delete [OPTIONS] KEY
```

**Arguments**:

* `KEY`: key of object in object  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics bucket purge`

Purge all objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket purge [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics dataset`

Download datasets from National Institute of Cancer (NIC) and Aignostics.

**Usage**:

```console
$ aignostics dataset [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `idc`: Download public datasets from Image Data...
* `aignostics`: Download proprietary sample datasets from...

### `aignostics dataset idc`

Download public datasets from Image Data Commons (IDC) Portal of National Institute of Cancer (NIC).

**Usage**:

```console
$ aignostics dataset idc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `browse`: Open browser to explore IDC portal.
* `indices`: List available columns in given of the IDC...
* `columns`: List available columns in given of the IDC...
* `query`: Query IDC index.
* `download`: Download from manifest file, identifier,...

#### `aignostics dataset idc browse`

Open browser to explore IDC portal.

**Usage**:

```console
$ aignostics dataset idc browse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics dataset idc indices`

List available columns in given of the IDC Portal.

**Usage**:

```console
$ aignostics dataset idc indices [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics dataset idc columns`

List available columns in given of the IDC Portal.

**Usage**:

```console
$ aignostics dataset idc columns [OPTIONS]
```

**Options**:

* `--index TEXT`: List available columns in given of the IDC Portal. See List available columns in given of the IDC Portal for available indices  [default: sm_instance_index]
* `--help`: Show this message and exit.

#### `aignostics dataset idc query`

Query IDC index. For example queries see https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/labs/idc_rsna2023.ipynb.

**Usage**:

```console
$ aignostics dataset idc query [OPTIONS] [QUERY]
```

**Arguments**:

* `[QUERY]`: SQL Query to execute.See https://idc-index.readthedocs.io/en/latest/column_descriptions.html for indices and their attributes  [default: SELECT
    SOPInstanceUID, SeriesInstanceUID, ImageType[3], instance_size, TotalPixelMatrixColumns, TotalPixelMatrixRows
FROM
    sm_instance_index
WHERE
    TotalPixelMatrixColumns &gt; 25000
    AND TotalPixelMatrixRows &gt; 25000
    AND ImageType[3] = &#x27;VOLUME&#x27;
]

**Options**:

* `--indices TEXT`: Comma separated list of additional indices to sync before running the query. The main index is always present. By default sm_instance_index is synched in addition. See https://idc-index.readthedocs.io/en/latest/column_descriptions.html for available indices.  [default: sm_instance_index]
* `--help`: Show this message and exit.

#### `aignostics dataset idc download`

Download from manifest file, identifier, or comma-separate set of identifiers.

Raises:
    typer.Exit: If the target directory does not exist.

**Usage**:

```console
$ aignostics dataset idc download [OPTIONS] SOURCE [TARGET]
```

**Arguments**:

* `SOURCE`: Identifier or comma-separated set of identifiers. IDs matched against collection_id, PatientId, StudyInstanceUID, SeriesInstanceUID or SOPInstanceUID.  [required]
* `[TARGET]`: target directory for download  [default: /Users/helmut/Code/python-sdk]

**Options**:

* `--target-layout TEXT`: layout of the target directory. See default for available elements for use  [default: %collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID/]
* `--dry-run / --no-dry-run`: dry run  [default: no-dry-run]
* `--help`: Show this message and exit.

### `aignostics dataset aignostics`

Download proprietary sample datasets from Aignostics.

**Usage**:

```console
$ aignostics dataset aignostics [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `download`: Download from bucket to folder via a...

#### `aignostics dataset aignostics download`

Download from bucket to folder via a signed URL.

**Usage**:

```console
$ aignostics dataset aignostics download [OPTIONS] SOURCE_URL DESTINATION_DIRECTORY
```

**Arguments**:

* `SOURCE_URL`: URL to download, e.g. gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff  [required]
* `DESTINATION_DIRECTORY`: Destination directory to download to  [required]

**Options**:

* `--help`: Show this message and exit.

## `aignostics system`

Determine health, info and further utillities.

**Usage**:

```console
$ aignostics system [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `health`: Determine and print system health.
* `info`: Determine and print system info.
* `serve`: Start the web server, hosting the...
* `openapi`: Dump the OpenAPI specification.
* `install`: Complete installation.
* `whoami`: Print user info.

### `aignostics system health`

Determine and print system health.

Args:
    output_format (OutputFormat): Output format (JSON or YAML).

**Usage**:

```console
$ aignostics system health [OPTIONS]
```

**Options**:

* `--output-format [yaml|json]`: Output format  [default: json]
* `--help`: Show this message and exit.

### `aignostics system info`

Determine and print system info.

Args:
    include_environ (bool): Include environment variables.
    filter_secrets (bool): Filter secrets from the output.
    output_format (OutputFormat): Output format (JSON or YAML).

**Usage**:

```console
$ aignostics system info [OPTIONS]
```

**Options**:

* `--include-environ / --no-include-environ`: Include environment variables  [default: no-include-environ]
* `--filter-secrets / --no-filter-secrets`: Filter secrets  [default: filter-secrets]
* `--output-format [yaml|json]`: Output format  [default: json]
* `--help`: Show this message and exit.

### `aignostics system serve`

Start the web server, hosting the graphical web application and/or webservice API.

Args:
    host (str): Host to bind the server to.
    port (int): Port to bind the server to.
    watch (bool): Enable auto-reload on changes of source code.
    open_browser (bool): Open app in browser after starting the server.

**Usage**:

```console
$ aignostics system serve [OPTIONS]
```

**Options**:

* `--host TEXT`: Host to bind the server to  [default: 127.0.0.1]
* `--port INTEGER`: Port to bind the server to  [default: 8000]
* `--open-browser / --no-open-browser`: Open app in browser after starting the server  [default: no-open-browser]
* `--help`: Show this message and exit.

### `aignostics system openapi`

Dump the OpenAPI specification.

Args:
    api_version (str): API version to dump.
    output_format (OutputFormat): Output format (JSON or YAML).

Raises:
    typer.Exit: If an invalid API version is provided.

**Usage**:

```console
$ aignostics system openapi [OPTIONS]
```

**Options**:

* `--api-version TEXT`: API Version. Available: v1  [default: v1]
* `--output-format [yaml|json]`: Output format  [default: json]
* `--help`: Show this message and exit.

### `aignostics system install`

Complete installation.

**Usage**:

```console
$ aignostics system install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics system whoami`

Print user info.

**Usage**:

```console
$ aignostics system whoami [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics wsi`

Operations on whole slide images.

**Usage**:

```console
$ aignostics wsi [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `inspect`: Inspect a wsi file and display its metadata.
* `dicom`

### `aignostics wsi inspect`

Inspect a wsi file and display its metadata.

**Usage**:

```console
$ aignostics wsi inspect [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Path to the wsi file  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics wsi dicom`

**Usage**:

```console
$ aignostics wsi dicom [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `inspect`: Inspect DICOM files at any hierarchy level.
* `geojson_import`: Import GeoJSON annotations into DICOM ANN...

#### `aignostics wsi dicom inspect`

Inspect DICOM files at any hierarchy level.

**Usage**:

```console
$ aignostics wsi dicom inspect [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Path of file or directory to inspect  [required]

**Options**:

* `--verbose / --no-verbose`: Verbose output  [default: no-verbose]
* `--summary / --no-summary`: Show only summary information  [default: no-summary]
* `--help`: Show this message and exit.

#### `aignostics wsi dicom geojson_import`

Import GeoJSON annotations into DICOM ANN instance.

**Usage**:

```console
$ aignostics wsi dicom geojson_import [OPTIONS] DICOM_PATH GEOJSON_PATH
```

**Arguments**:

* `DICOM_PATH`: Path to the DICOM file  [required]
* `GEOJSON_PATH`: Path to the GeoJSON file  [required]

**Options**:

* `--help`: Show this message and exit.
