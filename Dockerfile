# We share the base in the builder and targets
FROM python:3.12-slim-bookworm AS base

# The base of our builder
FROM base AS builder

# Copy in UV
COPY --from=ghcr.io/astral-sh/uv:0.7.15 /uv /bin/uv

# We use the system interpreter managed by uv
ENV UV_PYTHON_DOWNLOADS=0

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Create and set workdir 
WORKDIR /app


# The slim builder does not take in the extras
FROM builder AS builder-slim

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable --python 3.12

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY pyproject.toml /app
COPY .python-version /app
COPY uv.lock /app
COPY src /app/src
COPY LICENSE /app
COPY *.md /app

COPY .env.example /app/.env.example
COPY tests /app/tests
COPY examples /app/examples

# Install project specifics
# Nothing yet

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --python 3.12


# The all builder takes in all extras
FROM builder AS builder-all

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --all-extras --no-dev --no-editable --python 3.12

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY pyproject.toml /app
COPY .python-version /app
COPY uv.lock /app
COPY src /app/src
COPY LICENSE /app
COPY *.md /app

COPY .env.example /app/.env.example
COPY tests /app/tests
COPY examples /app/examples

# Install project specifics
COPY codegen/out/aignx /app/codegen/out/aignx

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras --no-dev --no-editable --python 3.12


# Base of our build targets
FROM base AS target

ENV AIGNOSTICS_RUNNING_IN_CONTAINER=1

# We don't want to run the app as root
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

# We place executables in the environment at the front of the path
# Remember: we don't have UV, as we only copied the app from the builder
ENV PATH="/app/.venv/bin:$PATH"

# API will run on port 8000 by default
EXPOSE 8000/tcp

# Marimo server will run on port 8001 by default
EXPOSE 8001/tcp

# No healthcheck by default
HEALTHCHECK NONE

# Default entrypoint is our CLI
ENTRYPOINT ["aignostics"]

# See https://matplotlib.org/stable/install/environment_variables_faq.html
ENV MPLCONFIGDIR=/tmp/matplotlib

# Target slim
FROM target AS slim

# Copy slim app, make it immutable
COPY --from=builder-slim --chown=root:root --chmod=755  /app /app

# Run as nonroot
USER app
WORKDIR /app


# And with all extras
FROM target AS all

# Copy fat app, i.e. with all extras, make it immutable
COPY --from=builder-all --chown=root:root --chmod=755  /app /app

# Run as nonroot
USER app
WORKDIR /app
