"""Service of dataset module."""

import atexit
import re
import subprocess
import sys
import threading
import time
from multiprocessing import Queue
from pathlib import Path
from typing import Any

from aignostics.utils import BaseService, Health, get_logger

logger = get_logger(__name__)

PATH_LENGTH_MAX = 260
TARGET_LAYOUT_DEFAULT = "%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID/"

# Global registry of active processes for cleanup
_active_processes: list[subprocess.Popen[str]] = []


def _terminate_process(process: subprocess.Popen[str]) -> None:
    """Terminate a single subprocess with graceful shutdown attempt.

    Args:
        process: The subprocess to terminate.
    """
    try:
        logger.warning("Terminating orphaned subprocess with PID %d", process.pid)
        process.terminate()
        # Give it a moment to terminate gracefully
        for _ in range(5):
            if process.poll() is not None:
                break
            time.sleep(0.1)
        # If still running, force kill
        if process.poll() is None:
            logger.warning("Forcefully killing subprocess with PID %d", process.pid)
            process.kill()
    except Exception:
        message = f"Error terminating subprocess with PID {process.pid}"
        logger.exception(message)


def _cleanup_processes() -> None:
    """Terminate any active subprocesses on exit."""
    for process in _active_processes[:]:
        if process.poll() is None:  # Process is still running
            _terminate_process(process)
            _active_processes.remove(process)


# Register the cleanup function
atexit.register(_cleanup_processes)


class Service(BaseService):
    """Service of the IDC module."""

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of hello service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={},
        )

    @staticmethod
    def _capture_progress_output(  # noqa: C901
        process: subprocess.Popen[str],
        queue: Queue,  # type: ignore[type-arg]
        base_progress: float = 0.04,
    ) -> None:
        """Capture output from the download process and update progress queue.

        Args:
            process (subprocess.Popen): Process with stdout to monitor
            queue (Queue): Queue to update with progress information
            base_progress (float): Starting progress value (0.5 means 50% complete)
        """
        if process.stderr is None:
            logger.warning("Cannot capture progress: subprocess stderr is None")
            return

        progress_pattern = re.compile(r"Downloading data:\s+(\d+)%")
        buffer = ""
        last_percentage = 0

        # Read one character at a time to handle carriage returns
        while process.poll() is None:
            char = process.stderr.read(1)
            if not char:  # End of stream
                break

            char_str = char
            # Handle carriage return (line overwrite)
            if char_str == "\r":
                # Process the current buffer for percentage
                match = progress_pattern.search(buffer)
                if match:
                    percentage = int(match.group(1))
                    if percentage != last_percentage:  # Only update if changed
                        last_percentage = percentage
                        # Scale the progress
                        adjusted_progress = base_progress + (percentage / 100.0) * (1.0 - base_progress)
                        queue.put_nowait(min(adjusted_progress, 0.99))  # Cap at 99% until complete
                        logger.debug("Updated progress: %.2f", adjusted_progress)

                # Reset buffer after processing carriage return
                buffer = ""
            elif char_str == "\n":
                # Process the current buffer for percentage on newline
                match = progress_pattern.search(buffer)
                if match:
                    percentage = int(match.group(1))
                    if percentage != last_percentage:
                        last_percentage = percentage
                        adjusted_progress = base_progress + (percentage / 100.0) * (1.0 - base_progress)
                        queue.put_nowait(min(adjusted_progress, 0.99))
                        logger.debug("Updated progress: %.2f", adjusted_progress)

                # For debug purposes, log the complete line
                logger.debug("Process output: %s", buffer)
                buffer = ""
            else:
                # Add character to buffer
                buffer += char_str

        # Process any remaining content in buffer
        if buffer:
            match = progress_pattern.search(buffer)
            if match:
                percentage = int(match.group(1))
                adjusted_progress = base_progress + (percentage / 100.0) * (1.0 - base_progress)
                queue.put_nowait(min(adjusted_progress, 0.99))

        # Process has finished, set progress to 100%
        queue.put_nowait(1.0)
        logger.debug("Process completed, setting progress to 100%")

    @staticmethod
    def download_with_queue(  # noqa: PLR0915
        queue: Queue,  # type: ignore[type-arg]
        source: str,
        target: str = str(Path.cwd()),
        target_layout: str = TARGET_LAYOUT_DEFAULT,
        dry_run: bool = False,
    ) -> None:
        """Download from manifest file, identifier, or comma-separate set of identifiers.

        Args:
            queue (Queue): The queue to use for progress updates.
            source (str): The source to download from.
            target (str): The target directory to download to.
            target_layout (str): The layout of the target directory.
            dry_run (bool): If True, perform a dry run.

        Raises:
            ValueError: If the target directory does not exist.
        """
        from ._idc_index import IDCClient  # noqa: PLC0415

        queue.put_nowait(0.01)

        client = IDCClient.client()
        queue.put_nowait(0.02)

        target_directory = Path(target)
        if not target_directory.is_dir():
            logger.warning("Target directory does not exist: %s", target_directory)
            message = f"Target directory does not exist: {target_directory}"
            raise ValueError(message)

        item_ids = [item.strip() for item in source.split(",") if item.strip()]

        if not item_ids:
            message = "No IDs provided."
            logger.warning(message)
            raise ValueError(message)

        index_df = client.index
        client.fetch_index("sm_instance_index")
        logger.info("Downloaded instance index")
        sm_instance_index_df = client.sm_instance_index
        queue.put_nowait(0.03)

        def check_and_download(column_name: str, item_ids: list[str], target_directory: Path, kwarg_name: str) -> bool:
            if column_name != "SOPInstanceUID":
                matches = index_df[column_name].isin(item_ids)
                matched_ids = index_df[column_name][matches].unique().tolist()
            else:
                matches = sm_instance_index_df[column_name].isin(item_ids)  # type: ignore
                matched_ids = sm_instance_index_df[column_name][matches].unique().tolist()  # type: ignore
            if not matched_ids:
                return False
            unmatched_ids = list(set(item_ids) - set(matched_ids))
            if unmatched_ids:
                logger.debug("Partial match for %s: matched %s, unmatched %s", column_name, matched_ids, unmatched_ids)
            logger.info("Identified matching %s: %s", column_name, matched_ids)
            queue.put_nowait(0.04)

            # Properly handle Windows paths - convert to raw string format
            safe_target_dir = str(target_directory).replace("\\", "\\\\")

            # Create command for the subprocess
            script_content = f"""
import sys
from aignostics.dataset._idc_index import IDCClient

client = IDCClient.client()
client.fetch_index("sm_instance_index")
client.download_from_selection(
    {kwarg_name}={matched_ids!r},
    downloadDir="{safe_target_dir}",
    dirTemplate="{target_layout}",
    quiet=False,
    show_progress_bar=True,
    use_s5cmd_sync=True,
    dry_run={dry_run!r}
)
"""

            # Run the download in a subprocess
            logger.debug(
                "Starting download subprocess with executable '%s' and script:\n%s", sys.executable, script_content
            )
            process = subprocess.Popen(  # noqa: S603
                [sys.executable, "-c", script_content],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Register process for cleanup
            _active_processes.append(process)

            # Start a thread to monitor the subprocess output
            monitor_thread = threading.Thread(
                target=Service._capture_progress_output, args=(process, queue, 0.5), daemon=True
            )
            monitor_thread.start()

            try:
                # Wait for the subprocess to complete
                return_code = process.wait()
                monitor_thread.join()

                if return_code != 0:
                    stdout_output = process.stdout.read() if process.stdout else "No stdout output"
                    stderr_output = process.stderr.read() if process.stderr else "No stderr output"
                    logger.error(
                        "Download subprocess failed with code '%d'\n\nstdout:\n\n%sstdin:\n\n%s\n\n",
                        return_code,
                        stdout_output,
                        stderr_output,
                    )
                    return False

                logger.info("Download completed successfully")
                queue.put_nowait(1.0)
                return True
            finally:
                # Clean up process reference
                if process in _active_processes:
                    _active_processes.remove(process)

        matches_found = 0
        matches_found += check_and_download("collection_id", item_ids, target_directory, "collection_id")
        matches_found += check_and_download("PatientID", item_ids, target_directory, "patientId")
        matches_found += check_and_download("StudyInstanceUID", item_ids, target_directory, "studyInstanceUID")
        matches_found += check_and_download("SeriesInstanceUID", item_ids, target_directory, "seriesInstanceUID")
        matches_found += check_and_download("SOPInstanceUID", item_ids, target_directory, "sopInstanceUID")
        if not matches_found:
            message = "None of the values passed matched any of the identifiers: "
            message += "collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID."
            logger.warning(message)
            raise ValueError(message)
