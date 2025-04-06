# CLI Reference

Command Line Interface of the aignostics platform

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

* `platform`: Platform diagnostics and utilities
* `application`: aignostics applications

## `aignostics platform`

Platform diagnostics and utilities

**Usage**:

```console
$ aignostics platform [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `install`: Complete and validate installation of the...
* `health`: Indicate if aignostics platform is healthy.
* `info`: Print info about service configuration.
* `openapi`: Dump the OpenAPI specification of to stdout.
* `bucket`: Transfer bucket provide by platform

### `aignostics platform install`

Complete and validate installation of the CLI.

**Usage**:

```console
$ aignostics platform install [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics platform health`

Indicate if aignostics platform is healthy.

**Usage**:

```console
$ aignostics platform health [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `aignostics platform info`

Print info about service configuration.

**Usage**:

```console
$ aignostics platform info [OPTIONS]
```

**Options**:

* `--output-format [yaml|json]`: Output format  [default: yaml]
* `--env / --no-env`: Include environment variables in output  [default: no-env]
* `--filter-secrets / --no-filter-secrets`: Filter out secret values from environment variables  [default: filter-secrets]
* `--help`: Show this message and exit.

### `aignostics platform openapi`

Dump the OpenAPI specification of to stdout.

**Usage**:

```console
$ aignostics platform openapi [OPTIONS]
```

**Options**:

* `--api-version [v1]`: API Version  [default: v1]
* `--output-format [yaml|json]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

### `aignostics platform bucket`

Transfer bucket provide by platform

**Usage**:

```console
$ aignostics platform bucket [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ls`: List contents of tranfer bucket.
* `purge`: Purge content of transfer bucket.

#### `aignostics platform bucket ls`

List contents of tranfer bucket.

**Usage**:

```console
$ aignostics platform bucket ls [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics platform bucket purge`

Purge content of transfer bucket.

**Usage**:

```console
$ aignostics platform bucket purge [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `aignostics application`

aignostics applications

**Usage**:

```console
$ aignostics application [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List available applications.
* `describe`: Describe application.
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
