"""Service of the example module."""

from aignostics.utils import BaseService, get_logger

logger = get_logger(__name__)


class Service(BaseService):
    """Example service for demonstration purposes."""

    def __init__(self) -> None:
        """Initialize the example service."""
        super().__init__()
        logger.info("Example service initialized")

    @staticmethod
    def get_example_data() -> dict[str, str]:
        """Get some example data.

        Returns:
            dict[str, str]: Example data dictionary.
        """
        return {"message": "Hello from Example module!", "status": "active", "module": "example"}

    @staticmethod
    def process_example(input_text: str) -> str:
        """Process example input.

        Args:
            input_text (str): Text to process.

        Returns:
            str: Processed text.
        """
        return f"Processed: {input_text}"
