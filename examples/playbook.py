import marimo

__generated_with = "0.12.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Login

        As a first step, you need to initialize the client to interact with the Aignostics Platform. This will execute an OAuth flow depending on the environment you run:
        - In case you have a browser available, an interactive login flow in your browser is started.
        - In case there is no browser available, a device flow is started.

        **NOTE:** By default, the client caches the access token in your operation systems application cache folder. If you do not want to store the access token, please initialize the client like this:

        ```python
        client = aignostics.client.Client(cache_token=False)
        ```
        """
    )


@app.cell
def _():
    import aignostics.client

    client = aignostics.client.Client()

    # the following functions is just used to visualize the results nicely in this notebook
    import pandas as pd
    from pydantic import BaseModel

    def show(models: BaseModel | list[BaseModel]) -> pd.DataFrame:
        if isinstance(models, BaseModel):
            items = [models.model_dump()]
        else:
            items = (a.model_dump() for a in models)
        return pd.DataFrame(items)

    return BaseModel, aignostics, client, pd, show


@app.cell
def _(mo):
    mo.md(r"""# List our available applications""")


@app.cell
def _(client, show):
    show(client.applications.list())


@app.cell
def _(mo):
    mo.md(r"""# List all available versions of an application""")


@app.cell
def _(client, show):
    # let's show the available version for the `TwoTaskDummy` application
    show(client.applications.versions.list(for_application="ee5566d2-d3cb-4303-9e23-8a5ab3e5b8ed"))


@app.cell
def _(mo):
    mo.md(r"""# Inspect the input payload for an application version""")


@app.cell
def _(client):
    # get a reference to the application version you are interested in
    # in our case, let us inspect the latest version `0.0.4`
    application_version = client.versions.details(for_application_version_id="212470c6-103e-429e-a9a0-0f662166faf5")

    # view the `input_artifacts` to get insights in the required fields of the application version payload
    for artifact in application_version.input_artifacts:
        print(artifact.to_json())
    return application_version, artifact


@app.cell
def _(mo):
    mo.md(r"""# Trigger an run for an application version""")


@app.cell
def _(client):
    import os

    from aignx.codegen.models import ApplicationVersion, RunCreationRequest

    from aignostics.samples import input_samples

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        "/Users/akunft/Downloads/aignx-platform-api-shsodcule-9086ce65109a.json"
    )

    application_run = client.runs.create(
        RunCreationRequest(
            application_version=ApplicationVersion("212470c6-103e-429e-a9a0-0f662166faf5"),
            items=input_samples.three_spots_payload(),
        )
    )
    print(application_run)
    return (
        ApplicationVersion,
        RunCreationRequest,
        application_run,
        input_samples,
        os,
    )


@app.cell
def _(mo):
    mo.md(r"""# Download application run results""")


@app.cell
def _(application_run):
    from aignostics.resources.runs import ApplicationRun

    # if you have a reference to an application run
    download_folder = "/tmp/"
    application_run.download_to_folder(download_folder)

    # if you want to check on the status when you do not have a reference to the application run anymore
    # ApplicationRun.for_application_run_id("<application_run_id>").download_to_folder(download_folder)
    return ApplicationRun, download_folder


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
