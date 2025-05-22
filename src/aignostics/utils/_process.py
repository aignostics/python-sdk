"""Process related utilities."""

from pathlib import Path

from pydantic import BaseModel


class ParentProcessInfo(BaseModel):
    """Information about a parent process."""

    name: str | None = None
    pid: int | None = None


class ProcessInfo(BaseModel):
    """Information about the current process."""

    project_root: str
    pid: int
    parent: ParentProcessInfo


def get_process_info() -> ProcessInfo:
    """
    Get information about the current process and its parent.

    Returns:
        ProcessInfo: Object containing process information.
    """
    import psutil  # noqa: PLC0415

    current_process = psutil.Process()
    parent = current_process.parent()

    return ProcessInfo(
        project_root=str(Path(__file__).parent.parent.parent.parent),
        pid=current_process.pid,
        parent=ParentProcessInfo(
            name=parent.name() if parent else None,
            pid=parent.pid if parent else None,
        ),
    )
