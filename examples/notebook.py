import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


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
        client = aignostics.client.Client(cache_token=False)
        ```
        """
    )
    return


@app.cell
def _():
    import aignostics.client
    import pandas as pd
    from pydantic import BaseModel

    # the following function is used for visualizing the results nicely in this notebook
    def show(models: BaseModel | list[BaseModel]) -> pd.DataFrame:
        if isinstance(models, BaseModel):
            items = [models.model_dump()]
        else:
            items = (a.model_dump() for a in models)
        return pd.DataFrame(items)
    return BaseModel, aignostics, pd, show


@app.cell
def _(aignostics):
    # initialize the client
    client = aignostics.client.Client()
    return (client,)


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
    return (applications,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # List all available versions of an application

        Now that we know the applications that are available, we can list all the versions of a specific application. In this case, we will use the `TwoTask Dummy Application` as an example, which has the `application_id`: `ee5566d2-d3cb-4303-9e23-8a5ab3e5b8ed`. Using the `application_id`, we can list all the versions of the application:
        """
    )
    return


@app.cell
def _(client, show):
    application_versions = client.applications.versions.list(for_application="ee5566d2-d3cb-4303-9e23-8a5ab3e5b8ed")
    # visualize
    show(application_versions)
    return (application_versions,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Inspect the application version details

        Now that we have the list of versions, we can inspect the details of a specific version. While we could directly use the list of application version returned by the `list` method, we want to directly query details for a specific application version. In this case, we will use version `0.0.3`, which has the `application_version_id`: `60e7b441-307a-4b41-8a97-5b02e7bc73a4`. We use the `application_version_id` to retrieve further details about the application version:
        """
    )
    return


@app.cell
def _(client):
    two_task_app = client.applications.versions.details(for_application_version_id="60e7b441-307a-4b41-8a97-5b02e7bc73a4")

    # view the `input_artifacts` to get insights in the required fields of the application version payload
    two_task_app.input_artifacts[0].to_json()
    return (two_task_app,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Trigger an application run

        Now, let's trigger an application run for the `TwoTask Dummy Application`. We will use the `application_version_id` that we retrieved in the previous step. To create an application run, we need to provide a payload that consists of 1 or more `Items`. We provide the Pydantic model `ItemCreationRequest` an item and the data that comes with it:
        ```python
        ItemCreationRequest(
            reference="<a unique reference associate outputs to this input item>",
            input_artifacts=[InputArtifactCreationRequest]
        )
        ```
        The `InputArtifactCreationRequest` defines the actual data that you provide aka. in this case the image that you want to be processed. The expected values are defined by the application version and have to align with the `input_artifacts` schema of the application version. In the case of the two task dummy application, we only require a single artifact per item, which is the image to process on. The artifact name is defined as `user_slide`. The `download_url` is a signed URL that allows the Aignostics Platform to download the image data later during processing. In addition to the image data itself, you have to provide the metadata defined in the input artifact schema, i.e., `checksum_crc32c`, `base_mpp`, `width`, and `height`. The metadata is used to validate the input data and is required for the processing of the image. The following example shows how to create an item with a single input artifact:

        ```python
        InputArtifactCreationRequest(
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
def _(client):
    from aignostics.client.utils import generate_signed_url
    from aignx.codegen.models import (
        ApplicationVersion,
        RunCreationRequest,
        ItemCreationRequest,
        InputArtifactCreationRequest
    )

    payload = [
        ItemCreationRequest(
            reference="1",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "N+LWCg==",
                        "base_mpp": 0.46499982,
                        "width": 3728,
                        "height": 3640,
                    },
                )
            ],
        ),
    ]

    application_run = client.runs.create(
        RunCreationRequest(
            application_version=ApplicationVersion("60e7b441-307a-4b41-8a97-5b02e7bc73a4"),
            items=payload,
        )
    )
    print(application_run)
    return (
        ApplicationVersion,
        InputArtifactCreationRequest,
        ItemCreationRequest,
        RunCreationRequest,
        application_run,
        payload,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        # Observe the status of the application run and download

        While you can observe the status of an application run directly via the `status()` method and also retrieve the results via the `results()` method, you can also download the results directly to a folder of your choice. The `download_to_folder()` method will download all the results to the specified folder. The method will automatically create a sub-folder in the specified folder with the name of the application run. The results for each individual input item will be stored in a separate folder named after the `reference` you defined in the `ItemCreationRequest`.

        The method downloads the results for a slide as soon as they are available. There is no need to keep the method running until all results are available. The method will automatically check for the status of the application run and download the results as soon as they are available. If you invoke the method on a run you already downloaded some results before, it will only download the missing artifacts.
        """
    )
    return


@app.cell
def _(application_run):
    download_folder = "/tmp/"
    application_run.download_to_folder(download_folder)
    return (download_folder,)


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
    return application_runs, run


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
