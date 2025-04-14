"""Example script to run the test application with one example image."""

import tempfile

from aignx.codegen.models import (
    ApplicationVersion,
    InputArtifactCreationRequest,
    ItemCreationRequest,
    RunCreationRequest,
)

import aignostics.client
from aignostics.client._utils import generate_signed_url  # noqa: PLC2701

# please look at the IPython or Marimo notebooks for a detailed explanation of the payload
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

# initialize the client
client = aignostics.client.Client()
# create application run
application_run = client.runs.create(
    RunCreationRequest(
        application_version=ApplicationVersion("60e7b441-307a-4b41-8a97-5b02e7bc73a4"),
        items=payload,
    )
)
# wait for the results and download incrementally as they become available
tmp_folder = tempfile.gettempdir()
application_run.download_to_folder(tmp_folder)
