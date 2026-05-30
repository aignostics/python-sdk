# Get started with the CLI

The **Aignostics CLI** is a command-line tool for interacting with the Aignostics Platform directly from your terminal or shell scripts. It is well suited to processing larger cohorts, automating repetitive analyses, and integrating with computational pipelines.

Common workflows:

- Download public datasets from the NCI Image Data Commons
- Submit batch processing runs for many slides
- Monitor run status and download results incrementally
- Automate repetitive tasks with shell scripts

```{include} ../partials/_get_started_signup.md
```

## Install the CLI

The CLI runs through [uv](https://docs.astral.sh/uv/). The command below installs uv if it isn't already present, updates it if it's out of date (including Homebrew-managed installs), and makes it available in your current shell. Afterwards every command is available through `uvx aignostics`.

**On macOS or Linux:**

```bash
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
else
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    if [ "$(printf '%s\n' "0.6.17" "$UV_VERSION" | sort -V | head -n1)" != "0.6.17" ]; then
        echo "Updating uv to the latest version..."
        UV_PATH=$(which uv)
        if [[ "$UV_PATH" == *"brew"* ]]; then
            echo "Updating uv using Homebrew..."
            brew upgrade uv
        else
            echo "Updating uv using the installer..."
            uv self update
        fi
    else
        echo "uv is up to date"
    fi
fi
```

**On Windows (PowerShell):**

```powershell
winget install --id=Microsoft.VCRedist.2015+.x64 -e
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify the install:

```bash
uvx aignostics --help
```

You should see the list of available command groups (`application`, `dataset`, `bucket`, `system`, and more). If the command isn't found, open a new terminal and try again.

## Run Atlas H&E-TME from the command line

This example downloads a public lung cancer dataset, submits an [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) run, and downloads the results:

```shell
# Download a sample dataset from the NCI Image Data Commons (IDC) portal.
# This dataset id refers to the TCGA LUAD collection and creates a tcga_luad directory of DICOM files.
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 data/
# Prepare a run.csv, extracting the required metadata from the DICOM files.
uvx aignostics application run prepare he-tme data/tcga_luad/run.csv data/
# Edit the run.csv to add the required staining method, tissue type, and disease (use any editor).
nano data/tcga_luad/run.csv
# Upload the run.csv and referenced whole slide images to the Aignostics Platform.
uvx aignostics application run upload he-tme data/tcga_luad/run.csv
# Submit the application run and print the run id.
uvx aignostics application run submit he-tme data/tcga_luad/run.csv
# Check the status of your run.
uvx aignostics application run list
# Incrementally download results as they become available (use the id from the previous step).
uvx aignostics application run result download APPLICATION_RUN_ID
```

For convenience, `application run execute` combines preparation, upload, submission, and download. The command below is equivalent to the above, supplying the required metadata with a mapping:

```shell
uvx aignostics dataset idc download 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0 data/
uvx aignostics application run execute he-tme data/tcga_luad/run.csv data/ --mapping ".*\.dcm:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"
```

The CLI provides extensive help at every level:

```shell
uvx aignostics --help                           # list all command groups
uvx aignostics application --help               # subcommands in the application group
uvx aignostics application run --help           # subcommands in the application run group
uvx aignostics application run list --help      # help for a specific command
```

See the [CLI reference](https://aignostics.readthedocs.io/en/latest/cli_reference.html) for all commands and options.

## System health checks

The CLI checks system health before uploading slides or submitting runs. If the system is unhealthy, the operation is blocked:

```
Error: Platform is not healthy: <reason>. Aborting.
```

To override this (not recommended for production), add `--force`:

```shell
uvx aignostics application run upload he-tme data/tcga_luad/run.csv --force
uvx aignostics application run submit he-tme data/tcga_luad/run.csv --force
uvx aignostics application run execute he-tme data/tcga_luad/run.csv data/ --force
```

To check system health manually:

```shell
uvx aignostics system health
```
