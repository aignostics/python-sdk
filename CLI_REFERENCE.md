# CLI Reference

Command Line Interface of Aignostics Python SDK

**Usage**:

```console
$ aignostics [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

🔬 Aignostics Python SDK v0.0.10 - built with love in Berlin 🐻

**Commands**:

* `gui`: Start graphical user interface (GUI) in...
* `notebook`: Start notebook in web browser.
* `application`: Application commands
* `idc`: Commands to query and download...
* `system`: System commands

## `aignostics gui`

Start graphical user interface (GUI) in native window.

**Usage**:

```console
$ aignostics gui [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics notebook`

Start notebook in web browser.

**Usage**:

```console
$ aignostics notebook [OPTIONS]
```

**Options**:

* `--host TEXT`: Host to bind the server to  [default: 127.0.0.1]
* `--port INTEGER`: Port to bind the server to  [default: 8001]
* `--help`: Show this message and exit.

## `aignostics application`

Application commands

**Usage**:

```console
$ aignostics application [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List available applications.
* `describe`: Describe application.
* `bucket`: Transfer bucket provide by platform
* `dataset`: Datasets for use as input for applications
* `metadata`: Metadata required as input for applications
* `run`: Runs of applications

### `aignostics application list`

List available applications.

**Usage**:

```console
$ aignostics application list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics application describe`

Describe application.

**Usage**:

```console
$ aignostics application describe [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics application bucket`

Transfer bucket provide by platform

**Usage**:

```console
$ aignostics application bucket [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ls`: List contents of tranfer bucket.
* `purge`: Purge content of transfer bucket.

#### `aignostics application bucket ls`

List contents of tranfer bucket.

**Usage**:

```console
$ aignostics application bucket ls [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application bucket purge`

Purge content of transfer bucket.

**Usage**:

```console
$ aignostics application bucket purge [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics application dataset`

Datasets for use as input for applications

**Usage**:

```console
$ aignostics application dataset [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `download`: Download dataset.

#### `aignostics application dataset download`

Download dataset.

**Usage**:

```console
$ aignostics application dataset download [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics application metadata`

Metadata required as input for applications

**Usage**:

```console
$ aignostics application metadata [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `generate`: Generate metadata.

#### `aignostics application metadata generate`

Generate metadata.

**Usage**:

```console
$ aignostics application metadata generate [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics application run`

Runs of applications

**Usage**:

```console
$ aignostics application run [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `submit`: Create run.
* `list`: List runs.
* `describe`: Describe run.
* `cancel`: Cancel run.
* `result`: Results of applications runs

#### `aignostics application run submit`

Create run.

**Usage**:

```console
$ aignostics application run submit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run list`

List runs.

**Usage**:

```console
$ aignostics application run list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run describe`

Describe run.

**Usage**:

```console
$ aignostics application run describe [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run cancel`

Cancel run.

**Usage**:

```console
$ aignostics application run cancel [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics application run result`

Results of applications runs

**Usage**:

```console
$ aignostics application run result [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `describe`: Describe the result of an application run.
* `download`: Download the result of an application run.
* `delete`: Delete the result of an application run.

##### `aignostics application run result describe`

Describe the result of an application run.

**Usage**:

```console
$ aignostics application run result describe [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `aignostics application run result download`

Download the result of an application run.

**Usage**:

```console
$ aignostics application run result download [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

##### `aignostics application run result delete`

Delete the result of an application run.

**Usage**:

```console
$ aignostics application run result delete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics idc`

Commands to query and download collections, cases, studies and series of Image Data Commons (IDC) Portal of the National Institute of Cancer (NIC)

**Usage**:

```console
$ aignostics idc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `browse`: Open browser to explore IDC portal.
* `columns`: List available columns in IDC index.
* `query`: Query IDC index.
* `download`: Download from manifest file, identifier,...

### `aignostics idc browse`

Open browser to explore IDC portal.

**Usage**:

```console
$ aignostics idc browse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics idc columns`

List available columns in IDC index.

**Usage**:

```console
$ aignostics idc columns [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics idc query`

Query IDC index. For example queries see https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/labs/idc_rsna2023.ipynb.

**Usage**:

```console
$ aignostics idc query [OPTIONS] [QUERY]
```

**Arguments**:

* `[QUERY]`: SQL Query  [default: SELECT
  SeriesInstanceUID
FROM
  index
WHERE
  Modality = &#x27;MR&#x27;
]

**Options**:

* `--help`: Show this message and exit.

### `aignostics idc download`

Download from manifest file, identifier, or comma-separate set of identifiers.

Raises:
    typer.Exit: If the target directory does not exist.

**Usage**:

```console
$ aignostics idc download [OPTIONS] SOURCE [TARGET]
```

**Arguments**:

* `SOURCE`: Filename of manifest, identifier, or comma-separate set of identifiers  [required]
* `[TARGET]`: target directory for download  [default: /Users/akunft/dev/python-sdk]

**Options**:

* `--target-layout TEXT`: layout of the target directory. See default for available elements for use  [default: %collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID]
* `--dry-run / --no-dry-run`: dry run  [default: no-dry-run]
* `--help`: Show this message and exit.

## `aignostics system`

System commands

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
