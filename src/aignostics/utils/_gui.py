import platform
from abc import ABC, abstractmethod
from pathlib import Path
from types import EllipsisType

from nicegui import ui

from ._constants import __is_running_in_container__, __project_name__
from ._di import locate_subclasses
from ._log import get_logger

logger = get_logger(__name__)

WINDOW_SIZE = (1280, 768)  # Default window size for the GUI


class BasePageBuilder(ABC):
    """Base class for all page builders."""

    @staticmethod
    @abstractmethod
    def register_pages() -> None:
        """Register pages."""


def gui_register_pages() -> None:
    """Register pages.

    This function is called by the GUI to register all pages.
    """
    page_builders = locate_subclasses(BasePageBuilder)
    for page_builder in page_builders:
        page_builder: BasePageBuilder  # type: ignore[no-redef]
        page_builder.register_pages()


def gui_run(  # noqa: PLR0913, PLR0917
    native: bool = True,
    show: bool = False,
    host: str | None = None,
    port: int | None = None,
    title: str = __project_name__,
    icon: str = "",
    watch: bool = False,
    with_api: bool = False,
    dark_mode: bool = False,
) -> None:
    """Start the GUI.

    Args:
        native: Whether to run the GUI in native mode.
        show: Whether to show the GUI.
        host: Host to run the GUI on.
        port: Port to run the GUI on.
        title: Title of the GUI.
        icon: Icon for the GUI.
        watch: Whether to watch for changes and reload the GUI.
        with_api: Whether to mount the API.
        dark_mode: Whether to use dark mode.

    Raises:
        ValueError: If with_notebook is True but notebook_path is None,
            or trying to run native within container.
    """
    from nicegui import native as native_app  # noqa: PLC0415

    if __is_running_in_container__ and native:
        message = "Native GUI cannot be run in a container. Please run with uvx or in browser."
        raise ValueError(message)

    if with_api:
        message = "with_api is not supported in this project."
        raise ValueError(message)

    if native and platform.system() == "Linux":
        native = False
        show = True

    gui_register_pages()

    ui.run(
        title=title,
        favicon=icon,
        native=native,
        reload=watch,
        dark=dark_mode,
        host=host,
        port=port or native_app.find_open_port(),
        frameless=native and platform.system() == "Darwin",
        show_welcome_message=native is False,
        show=show,
        window_size=WINDOW_SIZE if native else None,
        reconnect_timeout=60 * 60 * 24 * 7,
    )


class GUILocalFilePicker:
    """Local File Picker dialog class that lazy-loads NiceGUI dependencies."""

    def __new__(  # noqa: C901
        cls,
        directory: str,
        *,
        upper_limit: str | EllipsisType | None = ...,
        multiple: bool = False,
        show_hidden_files: bool = False,
    ) -> "GUILocalFilePicker":
        """Create a new instance with lazy-loaded dependencies.

        Args:
            directory: The directory to start in.
            upper_limit: The directory to stop at. None for no limit, default is same as starting directory.
            multiple: Whether to allow multiple files to be selected.
            show_hidden_files: Whether to show hidden files.

        Returns:
            An instance of the dialog with lazy-loaded dependencies.
        """
        from nicegui import app, events  # noqa: PLC0415
        # Lazy import ui only when actually creating an instance

        # Define the actual implementation class with the imports available
        class GUILocalFilePickerImpl(ui.dialog):
            def __init__(
                self,
                directory: str,
                *,
                upper_limit: str | EllipsisType | None = ...,
                multiple: bool = False,
                show_hidden_files: bool = False,
            ) -> None:
                """Local File Picker.

                A simple file picker that allows selecting files from the local filesystem where NiceGUI is running.

                Args:
                    directory: The directory to start in.
                    upper_limit: The directory to stop at. None for no limit, default is same as starting directory.
                    multiple: Whether to allow multiple files to be selected.
                    show_hidden_files: Whether to show hidden files.
                """
                super().__init__()

                self.path = Path(directory).expanduser()
                if upper_limit is None:
                    self.upper_limit = None
                elif upper_limit is ...:
                    self.upper_limit = Path(directory).expanduser()
                else:
                    self.upper_limit = Path(upper_limit).expanduser()
                self.show_hidden_files = show_hidden_files

                with self, ui.card():
                    self.add_drives_toggle()
                    self.grid = (
                        ui.aggrid(
                            {
                                "columnDefs": [{"field": "name", "headerName": "File"}],
                                "rowSelection": "multiple" if multiple else "single",
                            },
                            html_columns=[0],
                        )
                        .classes("w-96")
                        .classes(
                            "ag-theme-balham-dark" if app.storage.general.get("dark_mode", False) else "ag-theme-balham"
                        )
                        .on("cellDoubleClicked", self.handle_double_click)
                    )
                    with ui.row().classes("w-full justify-between"):
                        ui.button("Create Folder", on_click=self._create_folder, icon="create_new_folder").props(
                            "outline"
                        ).mark("BUTTON_FILEPICKER_CREATE_FOLDER")
                        with ui.row():
                            ui.button("Cancel", on_click=self.close).props("outline").mark("BUTTON_FILEPICKER_CANCEL")
                            ui.button("Ok", on_click=self._handle_ok).mark("BUTTON_FILEPICKER_OK")
                self.update_grid()

            def add_drives_toggle(self) -> None:
                if platform.system() == "Windows":
                    import win32api  # type: ignore[unused-ignore] # type: ignore # noqa: PLC0415

                    drives = win32api.GetLogicalDriveStrings().split("\000")[:-1]
                    self.drives_toggle = ui.toggle(drives, value=drives[0], on_change=self.update_drive)

            def update_drive(self) -> None:
                self.path = Path(str(self.drives_toggle.value)).expanduser()
                self.update_grid()

            def update_grid(self) -> None:
                paths = list(self.path.glob("*"))
                if not self.show_hidden_files:
                    paths = [p for p in paths if not p.name.startswith(".")]
                paths.sort(key=lambda p: p.name.lower())
                paths.sort(key=lambda p: not p.is_dir())

                self.grid.options["rowData"] = [
                    {
                        "name": f"📁 <strong>{p.name}</strong>" if p.is_dir() else p.name,
                        "path": str(p),
                    }
                    for p in paths
                ]
                if (self.upper_limit is None and self.path != self.path.parent) or (
                    self.upper_limit is not None and self.path != self.upper_limit
                ):
                    self.grid.options["rowData"].insert(
                        0,
                        {
                            "name": "📁 <strong>..</strong>",
                            "path": str(self.path.parent),
                        },
                    )
                self.grid.update()

            def handle_double_click(self, e: events.GenericEventArguments) -> None:
                self.path = Path(e.args["data"]["path"])
                if self.path.is_dir():
                    self.update_grid()
                else:
                    self.submit([str(self.path)])

            async def _handle_ok(self) -> None:
                rows = await self.grid.get_selected_rows()
                self.submit([r["path"] for r in rows])

            async def _create_folder(self) -> None:
                """Create a new folder in the current directory.

                Displays a modal dialog prompting for folder name, validates input,
                creates the folder using pathlib.Path.mkdir(), and refreshes the file grid.
                Cross-platform compatible (Windows, Linux, macOS) using pathlib abstraction.
                """
                # Prompt user for folder name
                with ui.dialog() as dialog, ui.card():
                    ui.label("Create New Folder").classes("text-h6")
                    folder_name_input = (
                        ui.input(label="Folder name", placeholder="Enter folder name")
                        .props("autofocus")
                        .classes("w-full")
                    )

                    def create_and_close() -> None:
                        """Create folder and refresh the grid.

                        Validates folder name, checks for duplicates, creates folder using
                        pathlib.Path.mkdir() (cross-platform), and handles OS/permission errors.
                        """
                        folder_name = folder_name_input.value.strip()
                        if not folder_name:
                            ui.notify("Folder name cannot be empty", type="warning")
                            return

                        new_folder_path = self.path / folder_name
                        if new_folder_path.exists():
                            ui.notify(f"Folder '{folder_name}' already exists", type="warning")
                            return

                        try:
                            # pathlib.Path.mkdir() is cross-platform compatible
                            new_folder_path.mkdir(parents=True, exist_ok=False)
                            ui.notify(f"Created folder: {folder_name}", type="positive")
                            self.update_grid()
                            dialog.close()
                        except (OSError, PermissionError) as e:
                            ui.notify(f"Failed to create folder: {e!s}", type="negative")

                    with ui.row().classes("w-full justify-end"):
                        ui.button("Cancel", on_click=dialog.close).props("flat")
                        ui.button("Create", on_click=create_and_close).props("flat")

                dialog.open()

        # Create and return an instance but tell mypy it's a GUILocalFilePicker
        return GUILocalFilePickerImpl(  # type: ignore[return-value]
            directory=directory,
            upper_limit=upper_limit,
            multiple=multiple,
            show_hidden_files=show_hidden_files,
        )
