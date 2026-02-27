"""Example script to run the test application with one example image."""

import tempfile

from aignostics import platform
from tests.constants_test import (
    SPOT_1_CRC32C,
    SPOT_1_GS_URL,
    SPOT_1_HEIGHT,
    SPOT_1_RESOLUTION_MPP,
    SPOT_1_WIDTH,
)

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
                    download_url=platform.generate_signed_url(SPOT_1_GS_URL),
                    metadata={
                        "checksum_base64_crc32c": SPOT_1_CRC32C,
                        "resolution_mpp": SPOT_1_RESOLUTION_MPP,
                        "width_px": SPOT_1_WIDTH,
                        "height_px": SPOT_1_HEIGHT,
                    },
                )
            ],
        ),
    ],
)
# wait for the results and download incrementally as they become available
tmp_folder = tempfile.gettempdir()
application_run.download_to_folder(tmp_folder)
