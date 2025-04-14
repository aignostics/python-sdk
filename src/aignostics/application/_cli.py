"""CLI (Command Line Interface) of Aignostics Python SDK."""

import typer

import aignostics.client
from aignostics.utils import console, get_logger

logger = get_logger(__name__)

cli = typer.Typer(name="application", help="Application commands")

bucket_app = typer.Typer()
cli.add_typer(bucket_app, name="bucket", help="Transfer bucket provide by platform")

datasset_app = typer.Typer()
cli.add_typer(datasset_app, name="dataset", help="Datasets for use as input for applications")

metadata_app = typer.Typer()
cli.add_typer(metadata_app, name="metadata", help="Metadata required as input for applications")

run_app = typer.Typer()
cli.add_typer(run_app, name="run", help="Runs of applications")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Results of applications runs")


@bucket_app.command("ls")
def bucket_ls() -> None:
    """List contents of tranfer bucket."""
    console.print("bucket ls")


@bucket_app.command("purge")
def bucket_purge() -> None:
    """Purge content of transfer bucket."""
    console.print("bucket purged.")


@cli.command("list")
def application_list() -> None:
    """List available applications."""
    client = aignostics.client.Client()
    applications = client.applications.list()
    console.print(applications)


@cli.command("describe")
def application_describe() -> None:
    """Describe application."""
    console.print("describe application")


@datasset_app.command("download")
def dataset_download() -> None:
    """Download dataset."""
    console.print("dataset download")


@metadata_app.command("generate")
def metadata_generate() -> None:
    """Generate metadata."""
    console.print("generate metadata")


@run_app.command("submit")
def run_submit() -> None:
    """Create run."""
    console.print("submit run")


@run_app.command("list")
def run_list() -> None:
    """List runs."""
    client = aignostics.client.Client()
    runs = client.runs.list()
    console.print(runs)


@run_app.command("describe")
def run_describe() -> None:
    """Describe run."""
    console.print("The run")


@run_app.command("cancel")
def run_cancel() -> None:
    """Cancel run."""
    console.print("canceled run")


@result_app.command("describe")
def result_describe() -> None:
    """Describe the result of an application run."""
    console.print("describe result")


@result_app.command("download")
def result_download() -> None:
    """Download the result of an application run."""
    console.print("download result")


@result_app.command("delete")
def result_delete() -> None:
    """Delete the result of an application run."""
    console.print("delete resuilt")
