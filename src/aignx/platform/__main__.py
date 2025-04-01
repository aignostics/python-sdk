from pathlib import Path

import aignx.platform
from aignx.codegen.models import (
    ApplicationVersion,
    InputArtifactCreationRequest,
    ItemCreationRequest,
    RunCreationRequest,
)
from aignx.platform.utils import _generate_signed_url

DEMO_SLIDE_URL = "gs://platform-api-application-test-data/heta/slides/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
DOWNLOAD_PATH = (Path(__file__) / "../../../../out").resolve()


def printall(list):
    for i in list:
        print(i)


def three_spots_payload():
    return [
        ItemCreationRequest(
            reference="1",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=_generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "N+LWCg==",
                        "base_mpp": 0.46499982,
                        "width": 3728,
                        "height": 3640,
                    }
                )
            ]
        ),
        ItemCreationRequest(
            reference="2",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=_generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "w+ud3g==",
                        "base_mpp": 0.46499982,
                        "width": 3616,
                        "height": 3400,
                    }
                )
            ]
        ),
        ItemCreationRequest(
            reference="3",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=_generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "Zmx0wA==",
                        "base_mpp": 0.46499982,
                        "width": 4016,
                        "height": 3952,
                    }
                )
            ]
        )
    ]


def main():
    platform = aignx.platform.Client()
    printall(platform.applications.list())
    printall(platform.versions.list(for_application="f7aa7f53-3b4c-476a-bc25-561ef9cfbf6d"))
    # # heta v0.3.4
    application_version_id = "8fbd3a43-d08d-41c1-8ad7-90ee69743b9d"
    application_run = platform.runs.create(
        RunCreationRequest(
            application_version=ApplicationVersion(application_version_id),
            items=three_spots_payload()
        )
    )
    print(application_run)
    # run = ApplicationRun.for_application_run_id("0feb2cc6-c6c0-4c31-90ba-e452266f9195")
    # run.download_to_folder("/Users/akunft/tmp/papi_pre_alpha")


if __name__ == "__main__":
    main()
