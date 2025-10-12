# Makefile for running common development tasks

# Read and validate Python version from .python-version file
PYTHON_VERSION := $(shell \
	if [ ! -f .python-version ]; then \
		echo "Error: .python-version file not found" >&2; \
		echo "INVALID"; \
	else \
		version=$$(cat .python-version); \
		if ! echo "$$version" | grep -qE '^[0-9]+\.[0-9]+(\.[0-9]+)?$$'; then \
			echo "Error: .python-version must contain a valid 2 or 3 segment version number (e.g., 3.11 or 3.11.5), got: $$version" >&2; \
			echo "INVALID"; \
		else \
			echo "$$version"; \
		fi; \
	fi)

# Check if Python version is valid and fail if not
ifeq ($(PYTHON_VERSION),INVALID)
$(error Python version validation failed. See error message above.)
endif

# Define all PHONY targets
.PHONY: act all audit bump clean codegen dist dist_native docs docker_build gui_watch install lint pre_commit_run_all profile setup test test_coverage_reset test_default test_e2e test_e2e_matrix test_integration test_integration_matrix test_long_running test_scheduled test_sequential test_unit test_unit_matrix test_very_long_running update_from_template


# Main target i.e. default sessions defined in noxfile.py
all:
	uv run --all-extras nox

# Nox targets

## Call nox sessions passing parameters
nox-cmd = @if [ "$@" = "test" ]; then \
	if [ -n "$(filter 3.%,$(MAKECMDGOALS))" ]; then \
		uv run --all-extras nox -s test -p $(filter 3.%,$(MAKECMDGOALS)); \
	elif [ -n "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo $(filter-out $@,$(MAKECMDGOALS)); \
		uv run --all-extras nox -s $@ -- $(filter-out $@,$(MAKECMDGOALS)); \
	else \
		uv run --all-extras nox -s $@; \
	fi; \
elif [ -n "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
	uv run --all-extras nox -s $@ -- $(filter-out $@,$(MAKECMDGOALS)); \
else \
	uv run --all-extras nox -s $@; \
fi

## Individual Nox sessions
act audit bump dist docs lint setup test update_from_template:
	$(nox-cmd)

# Standalone targets

## Install development dependencies and pre-commit hooks
install:
	sh install.sh
	uv run pre-commit install

## Run default tests, i.e. unit, then integration, then e2e tests, no (very_)long_running tests, single Python version
test_default:
	XDIST_WORKER_FACTOR=0.5 uv run --all-extras nox -s test_default

## Run unit tests (non-sociable tests)
test_unit:
	XDIST_WORKER_FACTOR=0.0 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m "unit and not long_running and not very_long_running" --cov-append

test_unit_matrix:
	XDIST_WORKER_FACTOR=0.5 uv run --all-extras nox -s test -- -m "unit and not long_running and not very_long_running" --cov-append

## Run integration tests (test real layer/module interactions with mocked external services)
test_integration:
	XDIST_WORKER_FACTOR=0.2 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m "integration and not long_running and not very_long_running" --cov-append

test_integration_matrix:
	XDIST_WORKER_FACTOR=0.5 uv run --all-extras nox -s test -- -m "integration and not long_running and not very_long_running" --cov-append

## Run e2e tests (test complete workflows with real external services)
test_e2e:
	XDIST_WORKER_FACTOR=1 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m "e2e and not long_running and not very_long_running" --cov-append

test_e2e_matrix:
	XDIST_WORKER_FACTOR=1 uv run --all-extras nox -s test -- -m "e2e and not long_running and not very_long_running" --cov-append

## Run tests marked as long_running
test_long_running:
	XDIST_WORKER_FACTOR=2 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m long_running --cov-append

## Run tests marked as very_long_running
test_very_long_running:
	XDIST_WORKER_FACTOR=2 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m very_long_running --cov-append

## Run tests marked as scheduled or scheduled_only
test_scheduled:
	XDIST_WORKER_FACTOR=1 uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m "(scheduled or scheduled_only)"

## Run tests marked as sequential
test_sequential:
	uv run --all-extras nox -s test -p $(PYTHON_VERSION) -- -m sequential

## Reset test coverage data
test_coverage_reset:
	rm -rf .coverage
	rm -rf reports/coverage*

## Clean build artifacts and caches
clean:
	rm -rf .mypy_cache
	rm -rf .nox
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .venv
	rm -rf dist && mkdir -p dist && touch dist/.keep
	rm -rf dist_vercel/wheels && mkdir -p dist_vercel/wheels && touch dist_vercel/wheels/.keep
	rm -rf dist_native && mkdir -p dist_native && touch dist_native/.keep
	rm -rf .coverage
	rm -rf reports && mkdir -p reports && touch reports/.keep
	uv run make -C docs clean

## Build Docker image
docker_build:
	docker build -t aignostics --target all .
	docker build -t aignostics --target slim .

pre_commit_run_all:
	uv run pre-commit run --all-files

gui_watch:
	uv run runner/gui_watch.py

profile:
	uv run --all-extras python -m scalene runner/scalene.py

# Signing: https://gist.github.com/bpteague/750906b9a02094e7389427d308ba1002
dist_native:
	# Build
	uv run --python $(PYTHON_VERSION) --no-dev --extra pyinstaller --extra qupath --extra marimo pyinstaller --distpath dist_native --clean --noconfirm aignostics.spec
	# Create 7z archive preserving symlinks
	@if command -v 7z >/dev/null 2>&1; then \
		cd dist_native; \
		if [ "$$(uname)" = "Darwin" ] && [ -d "aignostics.app" ]; then \
			echo "Creating 7z archive for macOS app bundle..."; \
			7z a -t7z -mx=9 -mqs=on aignostics.7z aignostics.app/; \
		else \
			echo "Creating 7z archive of dist_native/aignostics contents..."; \
			7z a -t7z -mx=9 -mqs=on aignostics.7z aignostics/; \
		fi; \
	else \
		echo "Warning: 7z not available, skipping archive creation"; \
	fi

# Project specific targets
## codegen
codegen:
	# Download openapi.json from https://platform.aignostics.com/api/v1/openapi.json, 
	# format via jq, and save as codegen/in/openapi_$version.json, with the 
	# version extracted from the info.version field in the JSON
	mkdir -p codegen/in/archive
	# curl -s https://platform.aignostics.com/api/v1/openapi.json | jq . > codegen/in/openapi.json
	#curl -s https://platform-dev.aignostics.ai/api/v1/openapi.json | jq . > codegen/in/openapi.json
	curl -s https://platform-staging.aignostics.com/api/v1/openapi.json | jq . > codegen/in/openapi.json
	version=$$(jq -r .info.version codegen/in/openapi.json); \
	echo "Detected version $$version"; \
	cp -f codegen/in/openapi.json codegen/in/archive/openapi_$${version}.json
	# Generate code using OpenAPI Generator Docker image
	docker run --rm -u "$(id -u):$(id -g)" -v "${PWD}:/local" openapitools/openapi-generator-cli:v7.10.0 generate \
		-i "/local/codegen/in/openapi.json" \
		-g python \
		-o /local/codegen/out \
		-c /local/codegen/config.json \
	# Alternative
	# openapi-generator generate -i codegen/in/openapi.json -g python -c codegen/config.json -o codegen/out

	# Hotfix for https://github.com/OpenAPITools/openapi-generator/issues/18932
	# create __init__.py files
	find codegen/out/aignx/codegen/models/ -name "[a-z]*.py" -type f | sed 's|.*/\(.*\)\.py|\1|' | xargs -I{} echo "from .{} import *" > codegen/out/aignx/codegen/models/__init__.py
	# fix resource patch
	# in codegen/out/public_api.py replace all occurrences of resource_path='/v1 with resource_path='/api/v1
	sed -i '' "s|resource_path='/v1|resource_path='/api/v1|g" codegen/out/aignx/codegen/api/public_api.py
	
# Special rule to catch any arguments (like patch, minor, major, pdf, Python versions, or x.y.z)
# This prevents "No rule to make target" errors when passing arguments to make commands
.PHONY: %
%:
	@:

# Help
help:
	@echo "🔬 Available targets for Aignostics Python SDK (v$(shell test -f VERSION && cat VERSION || echo 'unknown version'))"
	@echo ""
	@echo "  act                   - Run GitHub actions locally via act"
	@echo "  all                   - Run all default nox sessions, i.e. lint, test, docs, audit"
	@echo "  audit                 - Run security and license compliance audit"
	@echo "  bump patch|minor|major|x.y.z - Bump version"
	@echo "  clean                 - Clean build artifacts and caches"
	@echo "  codegen               - Download openapi.json from Aignostics platform, generate API code"
	@echo "  dist                  - Build wheel and sdist into dist/"
	@echo "  dist_native		   - Build native app variant of Aignostics Launchpad into dist/native/"
	@echo "  docs [pdf]            - Build documentation (add pdf for PDF format)"
	@echo "  docker_build          - Build Docker image aignostics"
	@echo "  gui_watch             - Open GUI in browser and update on changes in source code"
	@echo "  install               - Install or update development dependencies inc. pre-commit hooks"
	@echo "  lint                  - Run linting and formatting checks"
	@echo "  pre_commit_run_all    - Run pre-commit hooks on all files"
	@echo "  profile               - Profile with Scalene"
	@echo "  setup                 - Setup development environment"
	@echo "  test_default          - Run unit, then integration, then e2e tests, no long-running ones (python version defined in .python-version)"
	@echo "  test_unit             - Run unit tests (python version defined in .python-version)"
	@echo "  test_unit_matrix      - Run unit tests (matrix testing Python versions)"
	@echo "  test_integration      - Run integration tests (python version defined in .python-version)"
	@echo "  test_integration_matrix - Run integration tests (matrix testing Python versions)"
	@echo "  test_e2e              - Run regular end-to-end tests (python version defined in .python-version)"
	@echo "  test_e2e_matrix       - Run regular end-to-end tests (matrix testing Python versions)"
	@echo "  test_long_running     - Run long-running end-to-end tests (python version defined in .python-version)"
	@echo "  test_very_long_running - Run very long-running end-to-end tests (python version defined in .python-version)"
	@echo "  test_sequential       - Run tests marked as sequential (python version defined in .python-version)"
	@echo "  test_scheduled        - Run tests marked as scheduled (python version defined in .python-version)"
	@echo "  test_coverage_reset   - Reset test coverage data"
	@echo "  update_from_template  - Update from template using copier"
	@echo ""
	@echo "Built with love in Berlin 🐻"
