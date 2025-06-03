# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "aignostics==0.2.32",
# ]
# ///

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Initialize the Client

        As a first step, you need to initialize the client to interact with the Aignostics Platform. This will execute an OAuth flow depending on the environment you run:
        - In case you have a browser available, an interactive login flow in your browser is started.
        - In case there is no browser available, a device flow is started.

        **NOTE:** By default, the client caches the access token in your operation systems application cache folder. If you do not want to store the access token, please initialize the client like this:

        ```python
        import aignostics.client as platform
        # initialize the client
        client = platform.Client(cache_token=False)
        ```
        """
    )
    return


@app.cell
def _():
    import pandas as pd
    from pydantic import BaseModel

    # the following function is used for visualizing the results nicely in this notebook
    def show(models: BaseModel | list[BaseModel]) -> pd.DataFrame:
        if isinstance(models, BaseModel):
            items = [models.model_dump()]
        else:
            items = (a.model_dump() for a in models)
        return pd.DataFrame(items)
    return (show,)


@app.cell
def _():
    from aignostics import platform
    # initialize the client
    client = platform.Client(cache_token=False)
    return client, platform


@app.cell
def _(mo):
    mo.md(
        r"""
        # List our available applications

        Next, let us list the applications that are available in your organization:
        """
    )
    return


@app.cell
def _(client, show):
    applications = client.applications.list()
    # visualize
    show(applications)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        # List all available versions of an application

        Now that we know the applications that are available, we can list all the versions of a specific application. In this case, we will use the `TwoTask Dummy Application` as an example, which has the `application_id`: `two-task-dummy`. Using the `application_id`, we can list all the versions of the application:
        """
    )
    return


@app.cell
def _(client, show):
    application_versions = client.applications.versions.list(application="two-task-dummy")
    # visualize
    show(application_versions)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        # Inspect the application version details

        Now that we have the list of versions, we can inspect the details of a specific version. While we could directly use the list of application version returned by the `list` method, we want to directly query details for a specific application version. In this case, we will use version `0.35.0`, which has the `application_version_id`: `two-task-dummy:v0.35.0`. We use the `application_version_id` to retrieve further details about the application version:
        """
    )
    return


@app.cell
def _(client):
    two_task_app = client.applications.versions.details(application_version="two-task-dummy:v0.35.0")

    # view the `input_artifacts` to get insights in the required fields of the application version payload
    two_task_app.input_artifacts[0].to_json()
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        # Trigger an application run

        Now, let's trigger an application run for the `Test Application`. We will use the `application_version_id` that we retrieved in the previous step. To create an application run, we need to provide a payload that consists of 1 or more items. We provide the Pydantic model `InputItem` an item and the data that comes with it:
        ```python
        platform.InputItem(
            reference="<a unique reference associate outputs to this input item>",
            input_artifacts=[platform.InputArtifact]
        )
        ```
        The `InputArtifact` defines the actual data that you provide aka. in this case the image that you want to be processed. The expected values are defined by the application version and have to align with the `input_artifacts` schema of the application version. In the case of the two task dummy application, we only require a single artifact per item, which is the image to process on. The artifact name is defined as `user_slide`. The `download_url` is a signed URL that allows the Aignostics Platform to download the image data later during processing. In addition to the image data itself, you have to provide the metadata defined in the input artifact schema, i.e., `checksum_crc32c`, `base_mpp`, `width`, and `height`. The metadata is used to validate the input data and is required for the processing of the image. The following example shows how to create an item with a single input artifact:

        ```python
        platform.InputArtifact(
            name="user_slide", # as defined by the application version input_artifact schema
            download_url="<a signed url to download the data>",
            metadata={
                "checksum_crc32c": "<checksum>",
                "base_mpp": "<base_mpp>",
                "width": "<width>",
                "height": "<height>"
            }
        )
        ```
        """
    )
    return


@app.cell
def _(client, platform):
    application_run = client.runs.create(
        application_version="two-task-dummy:v0.0.5",
        items=[
            platform.InputItem(
                reference="wsi-1",
                input_artifacts=[
                    platform.InputArtifact(
                        name="user_slide",
                        download_url=platform.generate_signed_url("<signed-url>"),
                        metadata={
                            "checksum_crc32c": "AAAAAA==",
                            "base_mpp": 0.25,
                            "width": 10000,
                            "height": 10000,
                        },
                    )
                ],
            ),
        ],
    )
    print(application_run)
    return (application_run,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Observe the status of the application run and download

        While you can observe the status of an application run directly via the `status()` method and also retrieve the results via the `results()` method, you can also download the results directly to a folder of your choice. The `download_to_folder()` method will download all the results to the specified folder. The method will automatically create a sub-folder in the specified folder with the name of the application run. The results for each individual input item will be stored in a separate folder named after the `reference` you defined in the `Item`.

        The method downloads the results for a slide as soon as they are available. There is no need to keep the method running until all results are available. The method will automatically check for the status of the application run and download the results as soon as they are available. If you invoke the method on a run you already downloaded some results before, it will only download the missing artifacts.
        """
    )
    return


@app.cell
def _(application_run):
    download_folder = "/tmp/"
    application_run.download_to_folder(download_folder)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        # Continue to retrieve results for an application run

        In case you just triggered an application run and want to check on the results later or you had a connection loss, you can simply initialize an applicaiton run object via it's `application_run_id`. If you do not have the `application_run_id` anymore, you can simple list all currently running application version via the `client.runs.list()` method. The `application_run_id` is part of the `ApplicationRun` object returned by the `list()` method. You can then use the `download_to_folder()` method to continue downloading the results.
        """
    )
    return


@app.cell
def _(client):
    # list currently running applications
    application_runs = client.runs.list()
    for run in application_runs:
        print(run)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        from aignostics.client.resources.runs import ApplicationRun
        application_run = ApplicationRun.for_application_run_id("<application_run_id>")
        # download
        download_folder = "/tmp/"
        application_run.download_to_folder(download_folder)
        """
    )
    return


if __name__ == "__main__":
    app.run()
