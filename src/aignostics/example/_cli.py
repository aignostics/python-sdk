"""CLI of example module.

This module demonstrates how to create CLI commands using Typer that integrate
with the main Aignostics CLI system. The CLI follows a modular pattern where
each module can register its own commands.

Usage examples:
    uv run aignostics example hello
    uv run aignostics example hello "Your Name"
    uv run aignostics example data
    uv run aignostics example process "some text to process"
"""

from typing import Annotated

import typer

from aignostics.utils import console, get_logger

from ._service import Service

logger = get_logger(__name__)

# Create a Typer instance for this module's CLI commands
# - name="example": This becomes the subcommand name (aignostics example ...)
# - help: Shown when user runs "aignostics example --help"
# This CLI object is automatically discovered and registered with the main CLI
# through the module's __init__.py file which exports it in __all__
cli = typer.Typer(name="example", help="Example module commands")


@cli.command()
def hello(name: Annotated[str, typer.Argument(help="Name to greet")] = "World") -> None:
    """Say hello to someone.

    This is a simple command that demonstrates:
    - How to use Typer's @cli.command() decorator to register a function as a CLI command
    - How to use Annotated types for command arguments with help text
    - How to provide default values for optional arguments
    - How to use the console utility for colored output

    Usage:
        uv run aignostics example hello           # Uses default "World"
        uv run aignostics example hello "Alice"  # Custom name

    Args:
        name (str): Name to greet. This is a positional argument with a default value.
    """
    # Use the console utility from aignostics.utils for rich text output
    # The [green] syntax is Rich markup for colored text
    console.print(f"[green]Hello {name} from Example module![/green]")


@cli.command()
def data() -> None:
    """Get example data.

    This command demonstrates:
    - How to create a command with no arguments
    - How to call service layer methods from CLI commands
    - How to format and display structured data in the terminal

    Usage:
        uv run aignostics example data
    """
    # Call the service layer to get data - this follows the separation of concerns pattern
    # where CLI commands are thin wrappers around business logic in the service layer
    example_data = Service.get_example_data()

    # Display the data with formatting
    console.print("[blue]Example Data:[/blue]")
    for key, value in example_data.items():
        console.print(f"  {key}: {value}")


@cli.command()
def process(text: Annotated[str, typer.Argument(help="Text to process")]) -> None:
    """Process some text.

    This command demonstrates:
    - How to use required positional arguments
    - How to pass user input to service layer methods
    - How to display processed results

    Usage:
        uv run aignostics example process "Hello World"
        uv run aignostics example process "Any text you want to process"

    Args:
        text (str): Text to process. This is a required positional argument.
    """
    # Process the text using the service layer
    result = Service.process_example(text)

    # Display the result with yellow coloring
    console.print(f"[yellow]{result}[/yellow]")
