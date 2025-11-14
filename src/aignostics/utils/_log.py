"""Logging configuration and utilities."""

import contextlib
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

import platformdirs
from loguru import logger
from pydantic import Field

if TYPE_CHECKING:
    from loguru import Record

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ._constants import __env_file__, __is_library_mode__, __project_name__
from ._settings import load_settings


def _validate_file_name(file_name: str | None) -> str | None:
    """Validate the file_name is valid and the file writeable.

    - Checks file_name does not yet exist or is a file
    - If not yet existing, checks it can be created
    - If existing file, checks file is writeable

    Args:
        file_name: The file name of the log file

    Returns:
        str | None: The validated file name

    Raises:
        ValueError: If file name is not valid or the file not writeable
    """
    if file_name is None:
        return file_name

    file_path = Path(file_name)
    if file_path.exists():
        if file_path.is_dir():
            message = f"File name {file_path.absolute()} exists but is a directory"
            raise ValueError(message)
        if not os.access(file_path, os.W_OK):
            if file_path.exists():
                message = f"File {file_path.absolute()} is not writable"
                raise ValueError(message)
            return file_name  # This was a race condition, file was deleted in the meantime
    else:
        try:
            file_path.touch(exist_ok=True)
        except OSError as e:
            message = f"File {file_path.absolute()} cannot be created: {e}"
            raise ValueError(message) from e

        with contextlib.suppress(OSError):  # Parallel execution e.g. in tests can create race
            file_path.unlink()

    return file_name


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # noqa: PLR6301
        # Ignore Sentry-related log messages
        if "sentry.io" in record.getMessage():
            return

        # Prevent re-entrancy deadlock: Don't intercept logs from botocore/boto3
        # These libraries log from within handlers, which can cause circular calls:
        # Logger -> Handler -> Botocore -> Logger -> DEADLOCK
        # Let them use standard logging instead of loguru to avoid the lock issue
        if record.name.startswith(("botocore", "boto3")):
            return

        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = "DEBUG"

        # Patch the record to use the original logger name, function, and line from standard logging
        def patcher(record_dict: "Record") -> None:
            record_dict["module"] = record.module
            if record.processName and record.process:
                record_dict["process"].id = record.process
                record_dict["process"].name = record.processName
            if record.threadName and record.thread:
                record_dict["thread"].id = record.thread
                record_dict["thread"].name = record.threadName
            if hasattr(record, "taskName") and record.taskName:
                record_dict["extra"]["logging.taskName"] = record.taskName
            record_dict["name"] = record.name
            record_dict["function"] = record.funcName
            record_dict["line"] = record.lineno
            record_dict["file"].path = record.pathname
            record_dict["file"].name = record.filename

        # Don't use depth parameter - let it use the patched function/line info instead
        logger.patch(patcher).opt(exception=record.exc_info).log(level, record.getMessage())


class LogSettings(BaseSettings):
    """Settings for configuring logging behavior."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_LOG_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )

    level: Annotated[
        Literal["CRITICAL", "ERROR", "WARNING", "SUCCESS", "INFO", "DEBUG", "TRACE"],
        Field(description="Log level, see https://loguru.readthedocs.io/en/stable/api/logger.html", default="INFO"),
    ]
    stderr_enabled: Annotated[
        bool,
        Field(description="Enable logging to stderr", default=True),
    ]
    file_enabled: Annotated[
        bool,
        Field(description="Enable logging to file", default=False),
    ]
    file_name: Annotated[
        str,
        Field(
            description="Name of the log file",
            default=platformdirs.user_data_dir(__project_name__) + f"/{__project_name__}.log",
        ),
    ]
    redirect_logging: Annotated[
        bool,
        Field(description="Redirect standard logging", default=False),
    ]

    @field_validator("file_name")
    @classmethod
    def validate_file_name_when_enabled(cls, file_name: str, info: ValidationInfo) -> str:
        """
        Validate file_name only when file_enabled is True.

        Args:
            file_name: The file name to validate.
            info: Validation info containing other field values.

        Returns:
            str: The validated file name.
        """
        # Check if file_enabled is True in the provided data
        if info.data.get("file_enabled", False):
            _validate_file_name(file_name)
        return file_name


def logging_initialize(filter_func: Callable[["Record"], bool] | None = None) -> None:
    """Initialize logging configuration.

    Args:
        filter_func: Optional filter function to apply to all loggers.
                    Should accept a Record and return True to log the message, False to filter it out.
    """
    if __is_library_mode__:
        return

    settings = load_settings(LogSettings)

    logger.remove()  # Remove all default loggers

    k_service = os.getenv("K_SERVICE", "")  # GCP specific
    logger.configure(extra={"__project__name__": __project_name__, "K_SERVICE": k_service})  # Add as extras

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<yellow>{process: <6}</yellow> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | "
        "{extra}"
    )

    if settings.stderr_enabled:
        # Use catch=True to suppress errors when stderr is closed during test teardown
        logger.add(sys.stderr, level=settings.level, format=log_format, filter=filter_func, catch=True)

    if settings.file_enabled:
        logger.add(settings.file_name, level=settings.level, format=log_format, filter=filter_func, catch=True)

    if settings.redirect_logging:
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.trace("Logging initialized with level: {}", settings.level)
