"""Utility functions for the application GUI."""

from aignostics.platform import ApplicationRunStatus, ItemStatus


def application_id_to_icon(application_id: str) -> str:
    """Convert application ID to icon.

    Args:
        application_id (str): The application ID.

    Returns:
        str: The icon name.
    """
    match application_id:
        case "he-tme":
            return "biotech"
        case "test-app":
            return "construction"
    return "bug_report"


def run_status_to_icon_and_color(run_status: str) -> tuple[str, str]:  # noqa: PLR0911
    """Convert run status to icon amd color.

    Args:
        run_status (str): The run status.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match run_status:
        case ApplicationRunStatus.RUNNING:
            return "directions_run", "info"
        case ApplicationRunStatus.CANCELED_USER:
            return "cancel", "warning"
        case ApplicationRunStatus.CANCELED_SYSTEM:
            return "sync_problem", "negative"
        case ApplicationRunStatus.COMPLETED:
            return "done_all", "positive"
        case ApplicationRunStatus.COMPLETED_WITH_ERROR:
            return "error", "negative"
        case ApplicationRunStatus.RECEIVED:
            return "call_received", "info"
        case ApplicationRunStatus.REJECTED:
            return "hand_gesture_off", "negative"
        case ApplicationRunStatus.RUNNING:
            return "directions_run", "info"
        case ApplicationRunStatus.SCHEDULED:
            return "schedule", "info"
    return "bug_report", "negative"


def run_item_status_to_icon_and_color(run_status: str) -> tuple[str, str]:  # noqa: PLR0911
    """Convert run item status to icon.

    Args:
        run_status (str): The run item status.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match run_status:
        case ItemStatus.PENDING:
            return "pending", "info"
        case ItemStatus.CANCELED_USER:
            return "cancel", "warning"
        case ItemStatus.CANCELED_SYSTEM:
            return "sync_problem", "negative"
        case ItemStatus.ERROR_USER:
            return "hand_gesture_off", "negative"
        case ItemStatus.ERROR_SYSTEM:
            return "error", "negative"
        case ItemStatus.SUCCEEDED:
            return "check", "positive"
    return "bug_report", "negative"


def mime_type_to_icon(mime_type: str) -> str:
    """Convert mime type to icon.

    Args:
        mime_type (str): The mime type.

    Returns:
        str: The icon name.
    """
    match mime_type:
        case "image/tiff":
            return "image"
        case "application/dicom":
            return "image"
        case "text/csv":
            return "table_rows"
        case "application/geo+json":
            return "place"
        case "application/json":
            return "data_object"
    return "bug_report"
