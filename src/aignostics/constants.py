"""Constants used throughout Aignostics Python SDK's codebase ."""

import importlib.metadata
import pathlib

__project_name__ = __name__.split(".")[0]
__project_path__ = str(pathlib.Path(__file__).parent.parent.parent)
__version__ = importlib.metadata.version(__project_name__)

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
