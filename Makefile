# Makefile for running common development tasks

# Define all PHONY targets
.PHONY: all act audit bump clean dist dist_native docs docker_build install lint pre_commit_run_all profile setup setup test test_coverage_reset test_long_running test_scheduled test_sequential update_from_template gui_watch

# Main target i.e. default sessions defined in noxfile.py
all:
	uv run --all-extras nox

# Nox targets

## Call nox sessions passing parameters
nox-cmd = @if [ "$@" = "test" ]; then \
	if [ -n "$(filter 3.%,$(MAKECMDGOALS))" ]; then \
		uv run --all-extras nox -s test -p $(filter 3.%,$(MAKECMDGOALS)); \
	elif [ -n "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
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

## Run tests marked as long_running
test_long_running:
	uv run --all-extras nox -s test -p 3.13 -- -m long_running --cov-append

## Run tests marked as scheduled
test_scheduled:
	uv run --all-extras nox -s test -p 3.13 -- -m scheduled

## Run tests marked as sequential
test_sequential:
	uv run --all-extras nox -s test -p 3.13 -- -m sequential

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
	uv sync --no-dev --all-extras
	uv run pyinstaller --distpath dist_native --clean --noconfirm aignostics.spec
	uv sync --all-extras

# Project specific targets
## codegen
codegen:
	docker run --rm -u "$(id -u):$(id -g)" -v "${PWD}:/local" openapitools/openapi-generator-cli:v7.10.0 generate \
		-i "/local/codegen/in/api.json" \
		-g python \
		-o /local/codegen/out \
		-c /local/codegen/config.json \
	# Alternative
	# openapi-generator generate -i codegen/in/api.json -g python -c codegen/config.json -o codegen/out

	# Hotfix for https://github.com/OpenAPITools/openapi-generator/issues/18932
	# create __init__.py files
	find codegen/out/aignx/codegen/models/ -name "[a-z]*.py" -type f | sed 's|.*/\(.*\)\.py|\1|' | xargs -I{} echo "from .{} import *" > codegen/out/aignx/codegen/models/__init__.py
	# ls codegen/out/aignx/codegen/models/ | awk -F . '/[a-z].py/ {print "from ."$1" import *"}' > codegen/out/aignx/codegen/models/__init__.py


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
	@echo "  codegen               - Generate API code"
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
	@echo "  test [3.11|3.12|3.13] - Run tests (for specific Python version)"
	@echo "  test_sequential       - Run tests marked as sequential with Python 3.13"
	@echo "  test_scheduled        - Run tests marked as scheduled with Python 3.13"
	@echo "  test_long_running     - Run tests marked as long running with Python 3.13"
	@echo "  test_coverage_reset   - Reset test coverage data"
	@echo "  update_from_template  - Update from template using copier"
	@echo ""
	@echo "Built with love in Berlin 🐻"
