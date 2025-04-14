# CLI Reference

Command Line Interface of

**Usage**:

```console
$ aignostics [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

🧠 Aignostics Python SDK v0.0.10 - built with love in Berlin 🐻

**Commands**:

* `application`: Application commands
* `system`: System commands

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
