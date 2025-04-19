from pathlib import Path

import numpy as np
from nicegui import ui

from aignostics.gui import LocalFilePicker


async def pick_file() -> None:
    result = await LocalFilePicker(str(Path.cwd() / "examples"), multiple=True)
    ui.notify(f"You chose {result}")


@ui.page("/")
def home() -> None:
    ui.button("Choose file2", on_click=pick_file, icon="folder")

    with ui.matplotlib(figsize=(4, 3)).figure as fig:
        x = np.linspace(0.0, 5.0)
        y = np.cos(2 * np.pi * x) * np.exp(-x)
        ax = fig.gca()
        ax.plot(x, y, "-")
