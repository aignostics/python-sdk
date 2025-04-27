"""Example script to run the test application with one example image."""

import tempfile

from aignostics import platform

# initialize the client
client = platform.Client()
# create application run
# for details, see the IPython or Marimo notebooks for a detailed explanation of the payload
application_run = client.runs.create(
    application_version="two-task-dummy:v0.35.0",
    items=[
        platform.InputItem(
            reference="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
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
    ],
)
# wait for the results and download incrementally as they become available
tmp_folder = tempfile.gettempdir()
application_run.download_to_folder(tmp_folder)
