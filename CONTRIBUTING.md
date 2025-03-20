# Contributing

Thank you for considering contributing to Aignostics Python SDK!

## Setup

Clone this GitHub repository via ```git clone git@github.com:aignostics/python-sdk.git``` and change into the directory of your local Aignostics Python SDK repository: ```cd python-sdk```

Install the dependencies:

### macOS

```shell
if ! command -v brew &> /dev/null; then # if Homebrew package manager not present ...
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # ... install it
else
  which brew # ... otherwise inform where brew command was found
fi
# Install required tools if not present
which jq &> /dev/null || brew install jq
which xmllint &> /dev/null || brew install xmllint
which act &> /dev/null || brew install act
which pinact &> /dev/null || brew install pinact
uv run pre-commit install             # install pre-commit hooks, see https://pre-commit.com/
```

### Linux

```shell
sudo sudo apt install -y curl jq libxml2-utils gnupg2  # tooling
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash # act
uv run pre-commit install # see https://pre-commit.com/
```

## Code

```
src/aignostics/
├── __init__.py          # Package initialization
└── cli.py               # Command Line Interface
tests/                   # Unit and E2E tests
├── cli_tests.py         # Verifies the CLI functionality
└── fixtures/            # Fixtures and mock data
examples/                # Example code demonstrating use of the project
├── streamlit.py         # Streamlit App, deployed in Streamlit Community Cloud
├── notebook.py          # Marimo notebook
├── notebook.ipynb       # Jupyter notebook
└── script.py            # Minimal script
```

## Run

### .env file

Don't forget to configure your `.env` file with the required environment variables.

Notes:
1. .env.example is provided as a template.
2. .env is excluded from version control, so feel free to add secret values.

### update dependencies and create virtual environment

```shell
uv sync                      # install dependencies
uv sync --all-extras         # install all extras, required for examples
uv venv                      # create a virtual environment
source .venv/bin/activate    # activate it
uv run pre-commit install    # Install pre-commit hook etc.
```

### run the CLI

```shell
uv run aignostics # shows help
```

## Build

All build steps are defined in `noxfile.py`.

```shell
uv run nox        # Runs all build steps except setup_dev
```

You can run individual build steps - called sessions in nox as follows:

```shell
uv run nox -s test      # run tests
uv run nox -s lint      # run formatting and linting
uv run nox -s audit     # run security and license audit, inc. sbom generation
uv run nox -s docs      # build documentation, output in docs/build/html
uv run nox -s docs_pdf  # locally build pdf manual to docs/build/latex/aignostics.pdf
```

As a shortcut, you can run build steps using `./n`, e.g.

```shell
./n test
./n lint
# ...
```

Generate a wheel using uv
```shell
uv build
```

Notes:
1. Reports dumped into ```reports/```
3. Documentation dumped into ```docs/build/html/```
2. Distribution dumped into ```dist/```

### Running GitHub CI workflow locally

```shell
uv run nox -s act
```

Notes:
1. Workflow defined in `.github/workflows/*.yml`
2. test-and-report.yml calls all build steps defined in noxfile.py

### Docker

```shell
docker build -t aignostics-python-sdk .
```

```shell
docker run --env THE_VAR=THE_VALUE aignostics --help
```

### Pinning github actions

```shell
pinact run  # See https://dev.to/suzukishunsuke/pin-github-actions-to-a-full-length-commit-sha-for-security-2n7p
```

### Copier

Update from template

```shell
uv run nox -s update_from_template
```

## Pull Request Guidelines

1. Before starting to write code read the [code style guide](CODE_STYLE.md) document for mandatory coding style
   guidelines.
2. **Pre-Commit Hooks:** We use pre-commit hooks to ensure code quality. Please install the pre-commit hooks by running `uv run pre-commit install`. This ensure all tests, linting etc. pass locally before you can commit.
3. **Squash Commits:** Before submitting a pull request, please squash your commits into a single commit.
4. **Branch Naming:** Use descriptive branch names like `feature/your-feature` or `fix/issue-number`.
5. **Testing:** Ensure new features have appropriate test coverage.
6. **Documentation:** Update documentation to reflect any changes or new features.
