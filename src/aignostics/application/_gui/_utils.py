"""Utility functions for the application GUI."""

from aignostics.platform import ItemState, ItemTerminationReason, RunState, RunTerminationReason


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


def run_status_to_icon_and_color(
    run_status: str, termination_reason: str | None, item_count: int, item_succeeded_count: int
) -> tuple[str, str]:
    """Convert run status and termination reason to icon and color.

    Args:
        run_status (str): The run status.
        termination_reason (str): The termination reason.
        item_count (int): The total number of items in the run.
        item_succeeded_count (int): The number of items that succeeded in the run.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match run_status:
        case RunState.PENDING:
            return "schedule", "info"
        case RunState.PROCESSING:
            return "directions_run", "info"
        case RunState.TERMINATED:
            icon = "bug_report"
            if termination_reason == RunTerminationReason.CANCELED_BY_USER:
                icon = "cancel"
            if termination_reason == RunTerminationReason.CANCELED_BY_SYSTEM:
                icon = "error"
            if termination_reason == RunTerminationReason.ALL_ITEMS_PROCESSED:
                icon = "sports_score"
            color = "negative"
            if item_succeeded_count <= 0:
                color = "negative"
            elif item_succeeded_count < item_count:
                color = "warning"
            elif item_succeeded_count == item_count:
                color = "positive"
            return (icon, color)
    return "bug_report", "negative"


def run_item_status_and_termination_reason_to_icon_and_color(  # noqa: PLR0911
    item_status: str, termination_reason: str | None
) -> tuple[str, str]:
    """Convert item status and termination reason to icon and color.

    Args:
        item_status (str): The item status.
        termination_reason (str | None): The termination reason.

    Returns:
        tuple[str, str]: The icon name and color.
    """
    match item_status:
        case ItemState.PENDING:
            return "schedule", "info"
        case ItemState.PROCESSING:
            return "directions_run", "info"
        case ItemState.TERMINATED:
            if termination_reason == ItemTerminationReason.SKIPPED:
                return "next_plan", "warning"
            if termination_reason == ItemTerminationReason.SUCCEEDED:
                return "check_circle", "positive"
            if termination_reason == ItemTerminationReason.SYSTEM_ERROR:
                return "error", "negative"
            if termination_reason == ItemTerminationReason.USER_ERROR:
                return "warning", "negative"
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
