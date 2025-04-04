from aignx.codegen.models import InputArtifactCreationRequest, ItemCreationRequest

from aignostics.client.utils import _generate_signed_url


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
                    },
                )
            ],
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
                    },
                )
            ],
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
                    },
                )
            ],
        ),
    ]
