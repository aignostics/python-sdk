ARG REPO_PATH=/srv/repo

FROM europe-docker.pkg.dev/aignx-shared-tools-ebagiogxst/aignx-dockerhub-registry-prd-ar/python:3.12-slim-bookworm AS base
ARG REPO_PATH

# Install Poetry without defiling environment with its dependencies
RUN apt-get update && apt-get install -y curl libmagic1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

RUN mkdir -p ${REPO_PATH}
WORKDIR $REPO_PATH

RUN poetry config virtualenvs.create false

COPY poetry.lock        poetry.lock
COPY pyproject.toml     pyproject.toml

# todo(andreas): change to .env and also adjust code
COPY .env           .env.dev
COPY .env               .env
COPY src/               src
COPY codegen/           codegen

ENV PYTHONPATH="\
$REPO_PATH/src/:\
$REPO_PATH/codegen/:\
"

FROM base AS test
ARG REPO_PATH

COPY tests/ tests

WORKDIR $REPO_PATH
RUN poetry install --sync --no-root

CMD ["pytest"]
