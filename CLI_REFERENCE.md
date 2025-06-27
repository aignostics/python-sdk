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

🔬 Aignostics Python SDK v0.2.72 - built with love in Berlin 🐻

**Commands**:

* `launchpad`: Open Aignostics Launchpad, the graphical...
* `notebook`: Run Python notebook server based on Marimo.
* `application`: List and inspect applications on...
* `bucket`: Operations on cloud bucket on Aignostics...
* `dataset`: Download datasets from National Institute...
* `user`: User operations such as login, logout and...
* `qupath`: Interact with QuPath application.
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
$ aignostics notebook [OPTIONS] [NOTEBOOK]
```

**Arguments**:

* `[NOTEBOOK]`: Path to the notebook file to run. If not provided, a default notebook will be used.  [default: /Users/helmut/Code/python-sdk/src/aignostics/notebook/_notebook.py]

**Options**:

* `--host TEXT`: Host to bind the server to  [default: 127.0.0.1]
* `--port INTEGER`: Port to bind the server to  [default: 8001]
* `--override-if-exists / --no-override-if-exists`: Override the notebook in the user data directory if it already exists.  [default: no-override-if-exists]
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
* `dump-schemata`: Output the input schema of the application...
* `describe`: Describe application.
* `run`: List, submit and manage application runs

### `aignostics application list`

List available applications.

**Usage**:

```console
$ aignostics application list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Show application details  [default: no-verbose]
* `--help`: Show this message and exit.

### `aignostics application dump-schemata`

Output the input schema of the application in JSON format.

**Usage**:

```console
$ aignostics application dump-schemata [OPTIONS] ID
```

**Arguments**:

* `ID`: Id of the application or application_version to dump the output schema for. If application id is given the latest version of the application will be used.  [required]

**Options**:

* `--destination DIRECTORY`: Path pointing to directory where the input and output schemata will be dumped.  [default: /Users/helmut/Code/python-sdk]
* `--zip / --no-zip`: If set, the schema files will be zipped into a single file, with the schema files deleted.  [default: no-zip]
* `--help`: Show this message and exit.

### `aignostics application describe`

Describe application.

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

* `execute`: Prepare metadata, upload data to platform,...
* `prepare`: Prepare metadata CSV file required for...
* `upload`: Upload files referenced in the metadata...
* `submit`: Submit run by referencing the metadata CSV...
* `list`: List runs.
* `describe`: Describe run.
* `cancel`: Cancel run.
* `result`: Download or delete run results.

#### `aignostics application run execute`

Prepare metadata, upload data to platform, and submit an application run, then incrementally download results.

(1) Prepares metadata CSV file for the given application version
    by scanning the source directory for whole slide images
    and extracting metadata such as width, height, and mpp.
(2) Amends the metadata CSV file using the given mappings
    to set all required attributes.
(3) Uploads the files referenced in the metadata CSV file
    to the cloud bucket provisioned in the Aignostics platform.
(4) Submits the run for the given application version
    with the metadata from the CSV file.
(5) Downloads the results of the run to the destination directory,
    by default waiting for the run to complete
    and downloading results incrementally.

**Usage**:

```console
$ aignostics application run execute [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV_FILE SOURCE_DIRECTORY MAPPING...
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of application version to execute. If application id is given, the latest version of that application is used.  [required]
* `METADATA_CSV_FILE`: Filename of the .csv file containing the metadata and references.  [required]
* `SOURCE_DIRECTORY`: Source directory to scan for whole slide images  [required]
* `MAPPING...`: Mapping to use for amending metadata CSV file. Each mapping is of the form &#x27;&lt;regexp&gt;:&lt;key&gt;:&lt;value&gt;,&lt;key&gt;:&lt;value&gt;,...&#x27;.The regular expression is matched against the reference attribute of the entry. The key/value pairs are applied to the entry if the pattern matches. You can use the mapping option multiple times to set values for multiple files. Example: &quot;.*:staining_method:H&amp;E,tissue:LIVER,disease:LIVER_CANCER&quot;  [required]

**Options**:

* `--create-subdirectory-for-run / --no-create-subdirectory-for-run`: Create a subdirectory for the results of the run in the destination directory  [default: create-subdirectory-for-run]
* `--create-subdirectory-per-item / --no-create-subdirectory-per-item`: Create a subdirectory per item in the destination directory  [default: create-subdirectory-per-item]
* `--upload-prefix TEXT`: Prefix for the upload destination. If not given will be set to current milliseconds.  [default: 1751042637999.952]
* `--wait-for-completion / --no-wait-for-completion`: Wait for run completion and download results incrementally  [default: wait-for-completion]
* `--help`: Show this message and exit.

#### `aignostics application run prepare`

Prepare metadata CSV file required for submitting a run.

(1) Scans source_directory for whole slide images.
(2) Extracts metadata from whole slide images such as width, height, mpp.
(3) Creates CSV file with columns as required by the given application version.
(4) Optionally applies mappings to amend the metadata CSV file for columns
    that are not automatically filled by the metadata extraction process.

Example:
    aignostics application run prepare &quot;he-tme:v0.51.0&quot; metadata.csv /path/to/source_directory
    --mapping &quot;*.tiff:staining_method:H&amp;E,tissue:LUNG,disease:LUNG_CANCER&quot;

**Usage**:

```console
$ aignostics application run prepare [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV SOURCE_DIRECTORY
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application version to generate the metadata for. If application id is given, the latest version of that application is used.  [required]
* `METADATA_CSV`: Target filename for the generated metadata CSV file.  [required]
* `SOURCE_DIRECTORY`: Source directory to scan for whole slide images  [required]

**Options**:

* `--mapping TEXT`: Mapping to use for amending metadata CSV file. Each mapping is of the form &#x27;&lt;regexp&gt;:&lt;key&gt;:&lt;value&gt;,&lt;key&gt;:&lt;value&gt;,...&#x27;. The regular expression is matched against the reference attribute of the entry. The key/value pairs are applied to the entry if the pattern matches. You can use the mapping option multiple times to set values for multiple files.
* `--help`: Show this message and exit.

#### `aignostics application run upload`

Upload files referenced in the metadata CSV file to the Aignostics platform.

1. Reads the metadata CSV file.
2. Uploads the files referenced in the CSV file to the Aignostics platform.
3. Incrementally updates the CSV file with upload progress and the signed URLs for the uploaded files.

**Usage**:

```console
$ aignostics application run upload [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV_FILE
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application version to upload data for. If application id is given, the latest version of that application is used.  [required]
* `METADATA_CSV_FILE`: Filename of the .csv file containing the metadata and references.  [required]

**Options**:

* `--upload-prefix TEXT`: Prefix for the upload destination. If not given will be set to current milliseconds.  [default: 1751042638000.043]
* `--help`: Show this message and exit.

#### `aignostics application run submit`

Submit run by referencing the metadata CSV file.

1. Requires the metadata CSV file to be generated and referenced files uploaded first

Returns:
    The ID of the submitted application run.

**Usage**:

```console
$ aignostics application run submit [OPTIONS] APPLICATION_VERSION_ID METADATA_CSV_FILE
```

**Arguments**:

* `APPLICATION_VERSION_ID`: Id of the application version to submit run for. If application id is given, the latest version of that application is used.  [required]
* `METADATA_CSV_FILE`: Filename of the .csv file containing the metadata and references.  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run list`

List runs.

**Usage**:

```console
$ aignostics application run list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Show application details  [default: no-verbose]
* `--limit INTEGER`: Maximum number of runs to display
* `--help`: Show this message and exit.

#### `aignostics application run describe`

Describe run.

**Usage**:

```console
$ aignostics application run describe [OPTIONS] RUN_ID
```

**Arguments**:

* `RUN_ID`: Id of the run to describe  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run cancel`

Cancel run.

**Usage**:

```console
$ aignostics application run cancel [OPTIONS] RUN_ID
```

**Arguments**:

* `RUN_ID`: Id of the run to cancel  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run result`

Download or delete run results.

**Usage**:

```console
$ aignostics application run result [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `download`: Download results of a run.
* `delete`: Delete results of a run.

##### `aignostics application run result download`

Download results of a run.

**Usage**:

```console
$ aignostics application run result download [OPTIONS] RUN_ID [DESTINATION_DIRECTORY]
```

**Arguments**:

* `RUN_ID`: Id of the run to download results for  [required]
* `[DESTINATION_DIRECTORY]`: Destination directory to download results to  [default: /Users/helmut/Library/Application Support/aignostics/results]

**Options**:

* `--create-subdirectory-for-run / --no-create-subdirectory-for-run`: Create a subdirectory for the results of the run in the destination directory  [default: create-subdirectory-for-run]
* `--create-subdirectory-per-item / --no-create-subdirectory-per-item`: Create a subdirectory per item in the destination directory  [default: create-subdirectory-per-item]
* `--wait-for-completion / --no-wait-for-completion`: Wait for run completion and download results incrementally  [default: wait-for-completion]
* `--qupath-project / --no-qupath-project`: Create a QuPath project referencing input slides and results. 
The QuPath project will be created in a subfolder of the destination directory. 
This option requires the QuPath extension for Launchpad: start the Launchpad with `uvx --with &quot;aignostics&quot; aignostics ...` 
This options requires installation of the QuPath application: Run uvx --with &quot;aignostics&quot; aignostics qupath install  [default: no-qupath-project]
* `--help`: Show this message and exit.

##### `aignostics application run result delete`

Delete results of a run.

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
* `find`: Find objects in bucket on Aignostics...
* `download`: Download objects from bucket in Aignostics...
* `delete`: Delete objects in bucket on Aignostics...
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

### `aignostics bucket find`

Find objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket find [OPTIONS] [WHAT]...
```

**Arguments**:

* `[WHAT]...`: Patterns or keys to match object keys against - all if not specified.

**Options**:

* `--what-is-key / --no-what-is-key`: Specify if &#x27;what&#x27; is a single object key. If not specified, &#x27;what&#x27; is treated as a regex pattern.  [default: no-what-is-key]
* `--detail / --no-detail`: Show details  [default: no-detail]
* `--signed-urls`: Include signed download URLs
* `--help`: Show this message and exit.

### `aignostics bucket download`

Download objects from bucket in Aignostics platform to local directory.

**Usage**:

```console
$ aignostics bucket download [OPTIONS] [WHAT]...
```

**Arguments**:

* `[WHAT]...`: Patterns or keys to match object keys against - all if not specified.

**Options**:

* `--what-is-key / --no-what-is-key`: Specify if &#x27;what&#x27; is a single object key. If not specified, &#x27;what&#x27; is treated as a regex pattern.  [default: no-what-is-key]
* `--destination DIRECTORY`: Destination directory to download the matching objects to.  [default: /Users/helmut/Library/Application Support/aignostics/bucket_downloads]
* `--help`: Show this message and exit.

### `aignostics bucket delete`

Delete objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket delete [OPTIONS] WHAT...
```

**Arguments**:

* `WHAT...`: Patterns or keys to match object keys against.  [required]

**Options**:

* `--what-is-key / --no-what-is-key`: Specify if &#x27;what&#x27; is a single object key. If not specified, &#x27;what&#x27; is treated as a regex pattern.  [default: no-what-is-key]
* `--dry-run / --no-dry-run`: If set, only determines number of items that would be deleted, without actually deleting.  [default: dry-run]
* `--help`: Show this message and exit.

### `aignostics bucket purge`

Purge all objects in bucket on Aignostics Platform.

**Usage**:

```console
$ aignostics bucket purge [OPTIONS]
```

**Options**:

* `--dry-run / --no-dry-run`: If set, only determines number of items that would be deleted, without actually deleting.  [default: dry-run]
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
* `[TARGET]`: target directory for download  [default: /Users/helmut/Library/Application Support/aignostics/datasets/idc]

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
$ aignostics dataset aignostics download [OPTIONS] SOURCE_URL [DESTINATION_DIRECTORY]
```

**Arguments**:

* `SOURCE_URL`: URL to download, e.g. gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff  [required]
* `[DESTINATION_DIRECTORY]`: Destination directory to download to  [default: /Users/helmut/Library/Application Support/aignostics/datasets/aignostics]

**Options**:

* `--help`: Show this message and exit.

## `aignostics user`

User operations such as login, logout and whoami.

**Usage**:

```console
$ aignostics user [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `logout`: Logout if authenticated.
* `login`: (Re)login.
* `whoami`: Print user info.

### `aignostics user logout`

Logout if authenticated.

- Deletes the cached authentication token if existing.

**Usage**:

```console
$ aignostics user logout [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics user login`

(Re)login.

**Usage**:

```console
$ aignostics user login [OPTIONS]
```

**Options**:

* `--relogin / --no-relogin`: Re-login  [default: no-relogin]
* `--help`: Show this message and exit.

### `aignostics user whoami`

Print user info.

**Usage**:

```console
$ aignostics user whoami [OPTIONS]
```

**Options**:

* `--relogin / --no-relogin`: Re-login  [default: no-relogin]
* `--help`: Show this message and exit.

## `aignostics qupath`

Interact with QuPath application.

**Usage**:

```console
$ aignostics qupath [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Install QuPath application.
* `launch`: Launch QuPath application.
* `processes`: List running QuPath processes.
* `terminate`: Terminate running QuPath processes.
* `uninstall`: Uninstall QuPath application.
* `add`: Add image(s) to QuPath project.
* `annotate`: Add image(s) to QuPath project.
* `inspect`: Inspect project.
* `run-script`: Run a QuPath Groovy script with optional...

### `aignostics qupath install`

Install QuPath application.

**Usage**:

```console
$ aignostics qupath install [OPTIONS]
```

**Options**:

* `--version TEXT`: Version of QuPath to install. Do not change this unless you know what you are doing.  [default: 0.6.0-rc5]
* `--path DIRECTORY`: Path to install QuPath to. If not specified, the default installation path will be used.Do not change this unless you know what you are doing.  [default: /Users/helmut/Library/Application Support/aignostics]
* `--reinstall / --no-reinstall`: Reinstall QuPath even if it is already installed. This will overwrite the existing installation.  [default: reinstall]
* `--platform-system TEXT`: Override the system to assume for the installation. This is useful for testing purposes.  [default: Darwin]
* `--platform-machine TEXT`: Override the machine architecture to assume for the installation. This is useful for testing purposes.  [default: arm64]
* `--help`: Show this message and exit.

### `aignostics qupath launch`

Launch QuPath application.

**Usage**:

```console
$ aignostics qupath launch [OPTIONS]
```

**Options**:

* `--project DIRECTORY`: Path to QuPath project directory.
* `--image TEXT`: Path to image. Must be part of QuPath project
* `--script FILE`: Path to QuPath script to run on launch. Must be part of QuPath project.
* `--help`: Show this message and exit.

### `aignostics qupath processes`

List running QuPath processes.

Notice: This will not list processes that are not started from the installation directory.

**Usage**:

```console
$ aignostics qupath processes [OPTIONS]
```

**Options**:

* `-j, --json`: Output the running QuPath processes as JSON.  [required]
* `--help`: Show this message and exit.

### `aignostics qupath terminate`

Terminate running QuPath processes.

Notice: This will not terminate processes that are not started from the installation directory.

**Usage**:

```console
$ aignostics qupath terminate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics qupath uninstall`

Uninstall QuPath application.

**Usage**:

```console
$ aignostics qupath uninstall [OPTIONS]
```

**Options**:

* `--version TEXT`: Version of QuPath to install. If not specified, all versions will be uninstalled.
* `--path DIRECTORY`: Path to install QuPath to. If not specified, the default installation path will be used.Do not change this unless you know what you are doing.  [default: /Users/helmut/Library/Application Support/aignostics]
* `--platform-system TEXT`: Override the system to assume for the installation. This is useful for testing purposes.  [default: Darwin]
* `--platform-machine TEXT`: Override the machine architecture to assume for the installation. This is useful for testing purposes.  [default: arm64]
* `--help`: Show this message and exit.

### `aignostics qupath add`

Add image(s) to QuPath project. Creates project if it does not exist.

**Usage**:

```console
$ aignostics qupath add [OPTIONS] PROJECT PATH...
```

**Arguments**:

* `PROJECT`: Path to QuPath project directory. Will be created if it does not exist.  [required]
* `PATH...`: One or multiple paths. A path can point to an individual image or folder.In case of a folder, all images within will be added for supported image types.  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics qupath annotate`

Add image(s) to QuPath project. Creates project if it does not exist.

**Usage**:

```console
$ aignostics qupath annotate [OPTIONS] PROJECT IMAGE ANNOTATIONS
```

**Arguments**:

* `PROJECT`: Path to QuPath project directory. Will be created if it does not exist.  [required]
* `IMAGE`: Path to image to annotate. If the image is not part of the project, it will be added.  [required]
* `ANNOTATIONS`: Path to polygons file to import. The file must be a compatible GeoJSON file.  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics qupath inspect`

Inspect project.

**Usage**:

```console
$ aignostics qupath inspect [OPTIONS] PROJECT
```

**Arguments**:

* `PROJECT`: Path to QuPath project directory.  [required]

**Options**:

* `--help`: Show this message and exit.

### `aignostics qupath run-script`

Run a QuPath Groovy script with optional arguments.

**Usage**:

```console
$ aignostics qupath run-script [OPTIONS] SCRIPT
```

**Arguments**:

* `SCRIPT`: Path to the Groovy script file to execute.  [required]

**Options**:

* `-p, --project DIRECTORY`: Path to the QuPath project directory.
* `-i, --image TEXT`: Name of the image in the project or path to image file.
* `-a, --args TEXT`: Arguments to pass to the script. Can be specified multiple times.
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
* `config`: Configure application settings.

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
    mask_secrets (bool): Mask values for variables identified as secrets.
    output_format (OutputFormat): Output format (JSON or YAML).

**Usage**:

```console
$ aignostics system info [OPTIONS]
```

**Options**:

* `--include-environ / --no-include-environ`: Include environment variables  [default: no-include-environ]
* `--mask-secrets / --no-mask-secrets`: Mask secrets  [default: mask-secrets]
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

### `aignostics system config`

Configure application settings.

**Usage**:

```console
$ aignostics system config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `get`: Set a configuration key to a value.
* `set`: Set a configuration key to a value.
* `unset`: Set a configuration key to a value.
* `remote-diagnostics-enable`: Enable remote diagnostics via Sentry and...
* `remote-diagnostics-disable`: Disable remote diagnostics.
* `http-proxy-enable`: Enable HTTP proxy.
* `http-proxy-disable`: Disable HTTP proxy.

#### `aignostics system config get`

Set a configuration key to a value.

**Usage**:

```console
$ aignostics system config get [OPTIONS] KEY
```

**Arguments**:

* `KEY`: Configuration key to get value for  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics system config set`

Set a configuration key to a value.

**Usage**:

```console
$ aignostics system config set [OPTIONS] KEY VALUE
```

**Arguments**:

* `KEY`: Configuration key to set  [required]
* `VALUE`: Value to set for the configuration key  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics system config unset`

Set a configuration key to a value.

**Usage**:

```console
$ aignostics system config unset [OPTIONS] KEY
```

**Arguments**:

* `KEY`: Configuration key to unset  [required]

**Options**:

* `--help`: Show this message and exit.

#### `aignostics system config remote-diagnostics-enable`

Enable remote diagnostics via Sentry and Logfire. Data stored in EU data centers.

**Usage**:

```console
$ aignostics system config remote-diagnostics-enable [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics system config remote-diagnostics-disable`

Disable remote diagnostics.

**Usage**:

```console
$ aignostics system config remote-diagnostics-disable [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics system config http-proxy-enable`

Enable HTTP proxy.

**Usage**:

```console
$ aignostics system config http-proxy-enable [OPTIONS]
```

**Options**:

* `--host TEXT`: Host  [default: proxy.charite.de]
* `--port INTEGER`: Port  [default: 8080]
* `--scheme TEXT`: Scheme  [default: http]
* `--ssl-cert-file TEXT`: SSL certificate file
* `--no-ssl-verify / --no-no-ssl-verify`: Disable SSL verification  [default: no-no-ssl-verify]
* `--help`: Show this message and exit.

#### `aignostics system config http-proxy-disable`

Disable HTTP proxy.

**Usage**:

```console
$ aignostics system config http-proxy-disable [OPTIONS]
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
* `dicom`: Workaround for Typer bug, see...

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

Workaround for Typer bug, see https://github.com/fastapi/typer/pull/1240.

Raises:
    typer.Exit: If no subcommand is invoked, prints the help message and exits.

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
