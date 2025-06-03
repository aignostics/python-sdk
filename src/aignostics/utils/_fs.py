"""Filesystem utilities."""

import platform
from pathlib import Path, PureWindowsPath

# Constants
_WIN_DRIVE_MIN_LENGTH = 2  # Minimum length for a Windows drive path (e.g. C:)


def sanitize_path_component(component: str) -> str:
    """
    Sanitize a single path component (e.g., filename, directory name).

    Rules:
    1. Replaces all colons with underscores (no drive letter exceptions).

    This function is useful for sanitizing individual path components like filepath.stem
    where you don't want drive letter special handling.

    Args:
        component (str): The path component to sanitize.

    Returns:
        str: The sanitized path component.
    """
    return component.replace(":", "_")


def sanitize_path(path: str | Path) -> str | Path:
    """
    Sanitize a filesystem path.

    Rules:
    1. If a Path is provided a Path will returned, otherwise a string will be returned.
    2. Colons will be replaced with underscores except if it's a Windows drive letter.
    3. On Windows: If the sanitized path is reserved a ValueError will be raised.

    Args:
        path (str | Path): The path to sanitize.
        replace_colon_with_underscore (bool): if True (default) will apply rule #2

    Returns:
        str | Path: The sanitized path.

    Raises:
        ValueError: If the sanitized path is reserved on Windows.
    """
    is_path_object = isinstance(path, Path)
    path_str = str(path)

    # Replace colons with underscores, except for Windows drive letters (e.g., C:/).
    # See https://stackoverflow.com/questions/25774337/colon-in-file-names-in-python
    # on NTFS creating hidden "streams" otherwise
    # MacOS replaces a colon with a / in Finder, which is confusing, see
    # https://superuser.com/questions/1797432/does-mac-os-accept-colon-in-filename
    if len(path_str) >= _WIN_DRIVE_MIN_LENGTH and path_str[1] == ":" and path_str[0].isalpha():
        # Windows drive letter case - preserve drive letter, sanitize the rest
        drive_part = path_str[0:2]
        remaining_part = sanitize_path_component(path_str[2:])
        path_str = drive_part + remaining_part
    else:
        # Regular case - sanitize the entire path as a component
        path_str = sanitize_path_component(path_str)

    if platform.system() == "Windows" and PureWindowsPath(path_str).is_reserved():
        message = f"The path '{path_str}' is reserved on Windows and cannot be used. Please choose a different path."
        raise ValueError(message)

    # Return the same type as input
    if is_path_object:
        return Path(path_str)
    return path_str
