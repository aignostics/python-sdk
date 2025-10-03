"""Utility functions for the application GUI."""

from aignostics.platform import ApplicationRunStatus, ItemStatus, RunTerminationReason


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


def run_status_to_icon_and_color(run_status: str, termination_reason: str | None) -> tuple[str, str]:
    """Convert run status and termination reason to icon and color.

    Args:
        run_status (str): The run status.
        termination_reason (str): The termination reason.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match run_status:
        case ApplicationRunStatus.PENDING:
            return "schedule", "info"
        case ApplicationRunStatus.PROCESSING:
            return "directions_run", "info"
        case ApplicationRunStatus.TERMINATED:
            if termination_reason == RunTerminationReason.CANCELED_BY_USER:
                return "hand_gesture_off", "negative"
            if termination_reason == RunTerminationReason.CANCELED_BY_SYSTEM:
                return "sync_problem", "negative"
            if termination_reason == RunTerminationReason.ALL_ITEMS_PROCESSED:
                return "line_end_circle", "positive"
    return "bug_report", "negative"


def run_item_status_to_icon_and_color(item_status: str) -> tuple[str, str]:  # noqa: PLR0911
    """Convert item status to icon.

    Args:
        item_status (str): The item status.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match item_status:
        case ItemStatus.PENDING:
            return "pending", "info"
        case ItemStatus.CANCELED_USER:
            return "cancel", "warning"
        case ItemStatus.CANCELED_SYSTEM:
            return "sync_problem", "negative"
        case ItemStatus.USER_ERROR:
            return "hand_gesture_off", "negative"
        case ItemStatus.SYSTEM_ERROR:
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
