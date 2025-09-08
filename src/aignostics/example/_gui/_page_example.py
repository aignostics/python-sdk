"""Example page for the example module."""

from nicegui import ui

from aignostics.application import application_frame
from aignostics.example import Service
from aignostics.utils import get_logger

logger = get_logger(__name__)

# Constants
SECTION_HEADER_CLASSES = "text-2xl font-semibold mb-4"


async def _page_example() -> None:
    """Example page displaying module functionality."""
    ui.page_title("Example Module")

    # Set client content styling to work with frame layout
    ui.context.client.content.classes(remove="nicegui-content")
    ui.context.client.content.classes(add="pl-5 pt-5")

    await application_frame(
        navigation_title="🔬 Example Module",
        navigation_icon="science",
        navigation_icon_color="primary",
        navigation_icon_tooltip="Example Module for learning SDK architecture",
        left_sidebar=True,
    )

    with ui.row().classes("p-4 pt-2 pr-0"), ui.column().classes("w-full max-w-4xl"):
        # Header
        ui.label("🔬 Example Module").classes("text-4xl font-bold mb-4")
        ui.label("This is a template module for learning the SDK architecture.").classes("text-xl text-gray-600 mb-8")

        # Example data section
        with ui.card().classes("w-full mb-6"):
            ui.label("📊 Example Data").classes(SECTION_HEADER_CLASSES)
            example_data = Service.get_example_data()

            with ui.grid(columns=2).classes("w-full gap-4"):
                for key, value in example_data.items():
                    ui.label(f"{key.title()}:").classes("font-medium")
                    ui.label(value).classes("text-blue-600")

        # Interactive section
        with ui.card().classes("w-full mb-6"):
            ui.label("🛠️ Text Processing").classes(SECTION_HEADER_CLASSES)

            input_field = ui.input(label="Enter text to process", placeholder="Type something here...").classes(
                "w-full mb-4"
            )

            result_area = ui.label("").classes("text-green-600 font-medium")

            def process_text() -> None:
                """Process the input text and display result."""
                if input_field.value:
                    processed = Service.process_example(input_field.value)
                    result_area.text = processed
                else:
                    result_area.text = "Please enter some text first!"

            ui.button("Process Text", on_click=process_text).classes("bg-blue-500 text-white")

        # Navigation section
        with ui.card().classes("w-full"):
            ui.label("🧭 Navigation").classes(SECTION_HEADER_CLASSES)
            ui.label("This example module demonstrates:").classes("mb-2")

            with ui.column().classes("ml-4"):
                ui.label("• Service layer with static methods")
                ui.label("• CLI commands (try: uv run aignostics example --help)")
                ui.label("• GUI page registration and routing")
                ui.label("• Module auto-discovery via dependency injection")

            ui.button("← Back to Home", on_click=lambda: ui.navigate.to("/")).classes("mt-4")
