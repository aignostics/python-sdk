# CLI Reference

The Aignostics Python SDK provides two CLI entry points:

- **`aignostics`** — Full SDK (installed with `pip install aignostics`). Includes all commands
  for application runs, WSI processing, dataset downloads, cloud storage, and the Launchpad.
- **`aignostics-sdk`** — Slim API client (installed with `pip install aignostics-sdk`). Includes
  only user authentication and SDK metadata schema commands.

When the full `aignostics` package is installed both entry points are available.

---

## `aignostics-sdk` CLI Reference

Command Line Interface of the slim `aignostics-sdk` distribution.

**Usage**:

```console
$ aignostics-sdk [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `user`: User operations such as login, logout and whoami.
* `sdk`: Platform operations such as dumping the SDK run and item metadata schemas.

### `aignostics-sdk user`

User operations such as login, logout and whoami.

**Usage**:

```console
$ aignostics-sdk user [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `login`: Authenticate with the Aignostics Platform using OAuth 2.0 device flow.
* `logout`: Remove cached authentication token.
* `whoami`: Show the currently authenticated user.

#### `aignostics-sdk user login`

Authenticate with the Aignostics Platform using OAuth 2.0 device flow.

**Usage**:

```console
$ aignostics-sdk user login [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics-sdk user logout`

Remove cached authentication token.

**Usage**:

```console
$ aignostics-sdk user logout [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `aignostics-sdk user whoami`

Show the currently authenticated user.

**Usage**:

```console
$ aignostics-sdk user whoami [OPTIONS]
```

**Options**:

* `--mask-secrets / --no-mask-secrets`: Mask secrets in output.  [default: mask-secrets]
* `--help`: Show this message and exit.

### `aignostics-sdk sdk`

Platform operations such as dumping the SDK run and item metadata schemas.

**Usage**:

```console
$ aignostics-sdk sdk [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `run-metadata-schema`: Export the JSON Schema for SDK run custom metadata.
* `item-metadata-schema`: Export the JSON Schema for SDK item custom metadata.

#### `aignostics-sdk sdk run-metadata-schema`

Export the JSON Schema for SDK run custom metadata.

**Usage**:

```console
$ aignostics-sdk sdk run-metadata-schema [OPTIONS]
```

**Options**:

* `--pretty / --no-pretty`: Pretty-print the JSON output.  [default: no-pretty]
* `--help`: Show this message and exit.

#### `aignostics-sdk sdk item-metadata-schema`

Export the JSON Schema for SDK item custom metadata.

**Usage**:

```console
$ aignostics-sdk sdk item-metadata-schema [OPTIONS]
```

**Options**:

* `--pretty / --no-pretty`: Pretty-print the JSON output.  [default: no-pretty]
* `--help`: Show this message and exit.

---

## `aignostics` CLI Reference

