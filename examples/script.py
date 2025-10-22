"""Example script to run the test application with one example image."""

import tempfile

from aignostics import platform

# initialize the client
client = platform.Client()
# submit application run
# for details, see the IPython or Marimo notebooks for a detailed explanation of the payload
application_run = client.runs.submit(
    application_id="two-task-dummy",
    items=[
        platform.InputItem(
            external_id="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
                    ),
                    metadata={
                        "checksum_base64_crc32c": "N+LWCg==",
                        "resolution_mpp": 0.46499982,
                        "width_px": 3728,
                        "height_px": 3640,
                    },
                )
            ],
        ),
    ],
)
# wait for the results and download incrementally as they become available
tmp_folder = tempfile.gettempdir()
application_run.download_to_folder(tmp_folder)
