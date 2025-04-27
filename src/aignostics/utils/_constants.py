"""Constants generated from the environment at runtime used throughout the project."""

import os
import sys
from importlib import metadata
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

__project_name__ = __name__.split(".")[0]
__project_path__ = str(Path(__file__).parent.parent.parent)
__version__ = metadata.version(__project_name__)
__is_development_mode__ = "uvx" not in sys.argv[0].lower()
__is_running_in_container__ = os.getenv(f"{__project_name__.upper()}_RUNNING_IN_CONTAINER")

# Determine if we're running in a read-only runtime environment
READ_ONLY_ENV_INDICATORS = [
    f"{__project_name__.upper()}_RUNNING_IN_CONTAINER",
    "VERCEL_ENV",
    "RAILWAY_ENVIRONMENT",
]
__is_running_in_read_only_environment__ = any(os.getenv(env_var) is not None for env_var in READ_ONLY_ENV_INDICATORS)

# Determine environment we are deployed on
ENV_VAR_MAPPINGS = {
    "ENV": lambda env: env,
    "VERCEL_ENV": lambda env: env,  # See https://vercel.com/docs/environment-variables/system-environment-variables
    "RAILWAY_ENVIRONMENT": lambda env: env,  # See https://docs.railway.com/reference/variables#railway-provided-variables
}
__env__ = "local"  # Default
for env_var, mapper in ENV_VAR_MAPPINGS.items():
    env_value = os.getenv(env_var)
    if env_value:
        __env__ = mapper(env_value)  # type: ignore[no-untyped-call]
        break

# Define environment file paths
__env_file__ = [
    Path.home() / f".{__project_name__}" / ".env",
    Path.home() / f".{__project_name__}" / f".env.{__env__}",
    Path(".env"),
    Path(f".env.{__env__}"),
]
env_file_path = os.getenv(f"{__project_name__.upper()}_ENV_FILE")
if env_file_path:
    __env_file__.insert(2, Path(env_file_path))

# Determine __base_url__
PLATFORM_URL_MAPPINGS = {
    "VERCEL_URL": lambda url: f"https://{url}",  # See https://vercel.com/docs/environment-variables/system-environment-variables
    "RAILWAY_PUBLIC_DOMAIN": lambda url: f"https://{url}",  # See https://docs.railway.com/reference/variables#railway-provided-variables
}
__base__url__ = os.getenv(f"{__project_name__.upper()}_BASE_URL")
if not __base__url__:
    for env_var, mappers in PLATFORM_URL_MAPPINGS.items():
        env_value = os.getenv(env_var)
        if env_value:
            __base__url__ = mappers(env_value)  # type: ignore[no-untyped-call]
            break


def get_project_url_by_label(prefix: str) -> str:
    """Get labeled Project-URL.

    See https://packaging.python.org/en/latest/specifications/core-metadata/#core-metadata-project-url

    Args:
        prefix(str): The prefix to match at the beginning of URL entries.

    Returns:
        The extracted URL string if found, or an empty string if not found.
    """
    for url_entry in metadata.metadata(__project_name__).get_all("Project-URL", []):
        if url_entry.startswith(prefix):
            return str(url_entry.split(", ", 1)[1])
    return ""


_authors = metadata.metadata(__project_name__).get_all("Author-email", [])
_author = _authors[0] if _authors else None
__author_name__ = _author.split("<")[0].strip() if _author else None
__author_email__ = _author.split("<")[1].strip(" >") if _author else None
__repository_url__ = get_project_url_by_label("Source")
__documentation__url__ = get_project_url_by_label("Documentation")
