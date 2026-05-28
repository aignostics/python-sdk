"""Data models for the application module."""

from enum import StrEnum
from importlib.util import find_spec
from pathlib import Path

from pydantic import BaseModel, computed_field

from aignostics.platform import ItemResult, OutputArtifactElement, RunData

has_qupath_extra = find_spec("ijson")
if has_qupath_extra:
    from aignostics.qupath import AddProgress as QuPathAddProgress
    from aignostics.qupath import AnnotateProgress as QuPathAnnotateProgress


class DownloadProgressState(StrEnum):
    """Enum for download progress states."""

    INITIALIZING = "Initializing ..."
    DOWNLOADING_INPUT = "Downloading input slide ..."
    QUPATH_ADD_INPUT = "Adding input slides to QuPath project ..."
    CHECKING = "Checking run status ..."
    WAITING = "Waiting for item completing ..."
    DOWNLOADING = "Downloading artifact ..."
    QUPATH_ADD_RESULTS = "Adding result images to QuPath project ..."
    QUPATH_ANNOTATE_INPUT_WITH_RESULTS = "Annotating input slides in QuPath project with results ..."
    COMPLETED = "Completed."


class DownloadProgress(BaseModel):
    """Model for tracking download progress with computed progress metrics."""

    status: DownloadProgressState = DownloadProgressState.INITIALIZING
    run: RunData | None = None
    item: ItemResult | None = None
    item_count: int | None = None
    item_index: int | None = None
    item_external_id: str | None = None
    artifact: OutputArtifactElement | None = None
    artifact_count: int | None = None
    artifact_index: int | None = None
    artifact_path: Path | None = None
    artifact_download_url: str | None = None
    artifact_size: int | None = None
    artifact_downloaded_chunk_size: int = 0
    artifact_downloaded_size: int = 0
    input_slide_path: Path | None = None
    input_slide_url: str | None = None
    input_slide_size: int | None = None
    input_slide_downloaded_chunk_size: int = 0
    input_slide_downloaded_size: int = 0
    if has_qupath_extra:
        qupath_add_input_progress: QuPathAddProgress | None = None
        qupath_add_results_progress: QuPathAddProgress | None = None
        qupath_annotate_input_with_results_progress: QuPathAnnotateProgress | None = None

    @computed_field  # type: ignore
    @property
    def total_artifact_count(self) -> int | None:
        """Calculate total number of artifacts across all items.

        Returns:
            int | None: Total artifact count or None if counts not available.
        """
        if self.item_count and self.artifact_count:
            return self.item_count * self.artifact_count
        return None

    @computed_field  # type: ignore
    @property
    def total_artifact_index(self) -> int | None:
        """Calculate the current artifact index across all items.

        Returns:
            int | None: Total artifact index or None if indices not available.
        """
        if self.item_count and self.artifact_count and self.item_index is not None and self.artifact_index is not None:
            return self.item_index * self.artifact_count + self.artifact_index
        return None

    @computed_field  # type: ignore
    @property
    def item_progress_normalized(self) -> float:  # noqa: PLR0911
        """Compute normalized item progress in range 0..1.

        Returns:
            float: The normalized item progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING_INPUT:
            if (not self.item_count) or self.item_index is None:
                return 0.0
            return min(1, float(self.item_index + 1) / float(self.item_count))
        if self.status == DownloadProgressState.DOWNLOADING:
            if (not self.total_artifact_count) or self.total_artifact_index is None:
                return 0.0
            return min(1, float(self.total_artifact_index + 1) / float(self.total_artifact_count))
        if has_qupath_extra:
            if self.status == DownloadProgressState.QUPATH_ADD_INPUT and self.qupath_add_input_progress:
                return self.qupath_add_input_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ADD_RESULTS and self.qupath_add_results_progress:
                return self.qupath_add_results_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS:
                if (not self.item_count) or (not self.item_index):
                    return 0.0
                return min(1, float(self.item_index + 1) / float(self.item_count))
        return 0.0

    @computed_field  # type: ignore
    @property
    def artifact_progress_normalized(self) -> float:
        """Compute normalized artifact progress in range 0..1.

        Returns:
            float: The normalized artifact progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING_INPUT:
            if not self.input_slide_size:
                return 0.0
            return min(1, float(self.input_slide_downloaded_size) / float(self.input_slide_size))
        if self.status == DownloadProgressState.DOWNLOADING:
            if not self.artifact_size:
                return 0.0
            return min(1, float(self.artifact_downloaded_size) / float(self.artifact_size))
        if (
            has_qupath_extra
            and self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
            and self.qupath_annotate_input_with_results_progress
        ):
            return self.qupath_annotate_input_with_results_progress.progress_normalized
        return 0.0
