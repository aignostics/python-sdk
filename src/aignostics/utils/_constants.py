"""Constants used throughout."""

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
__env__ = os.getenv("ENV", os.getenv("VERCEL_ENV", "local"))
__env_file__ = [
    Path.home() / f".{__project_name__}" / ".env",
    Path.home() / f".{__project_name__}" / f".env.{__env__}",
    Path(".env"),
    Path(f".env.{__env__}"),
]
env_file_path = os.getenv(f"{__project_name__.upper()}_ENV_FILE")
if env_file_path:
    __env_file__.insert(2, Path(env_file_path))

vercel_base_url = os.getenv("VERCEL_URL", None)
if vercel_base_url:
    vercel_base_url = "https://" + vercel_base_url
__base__url__ = os.getenv(__project_name__.upper() + "_BASE_URL", None)
if not __base__url__ and vercel_base_url:
    __base__url__ = vercel_base_url


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
