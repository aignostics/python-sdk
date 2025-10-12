import tempfile
from pathlib import Path

from aignostics import platform
from aignostics.platform import ApplicationRun
from aignx.codegen.models import ArtifactOutput
from aignx.codegen.models import ArtifactState
from aignx.codegen.models import ItemOutput
from aignx.codegen.models import ItemState
from aignx.codegen.models import RunOutput
from aignx.codegen.models import RunState


def _validate_output(
    application_run: ApplicationRun,
    output_base_folder: Path,
    checksum_attribute_key: str = "checksum_base64_crc32c",
) -> None:
    """Validate the output of an application run.

    This function checks if the application run has completed successfully and verifies the output artifact checksum

    Args:
        application_run (ApplicationRun): The application run to validate.
        output_base_folder (Path): The base folder where the output is stored.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
    """
    run_details = application_run.details()
    assert run_details.status == RunState.TERMINATED and run_details.output == RunOutput.FULL, (
        f"Run {application_run.run_id}: Did not finish in state `FULL` for its output, but '{run_details.output}'."
    )

    run_result_folder = output_base_folder / application_run.run_id
    assert run_result_folder.exists(), f"Application run {application_run.run_id}: result folder does not exist"

    run_results = application_run.results()

    for item in run_results:
        # validate state
        assert item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL, (
            f"Application run {application_run.run_id}: "
            f"output for item {item.external_id} is {item.output}, expected `FULL`"
        )
        # validate results
        item_dir = run_result_folder / item.external_id
        assert item_dir.exists(), (
            f"Application run {application_run.run_id}: result folder for item {item.external_id} does not exist"
        )
        for artifact in item.output_artifacts:
            assert artifact.state == ArtifactState.TERMINATED and artifact.output == ArtifactOutput.AVAILABLE, (
                f"Application run {application_run.run_id}: artifact {artifact} should have output state `AVAILABLE`"
            )
            assert artifact.download_url is not None, (
                f"Application run {application_run.run_id}: artifact {artifact} should provide a download url"
            )
            file_ending = platform.mime_type_to_file_ending(platform.get_mime_type_for_artifact(artifact))
            file_path = item_dir / f"{artifact.name}{file_ending}"
            assert file_path.exists(), (
                f"Application run {application_run.run_id}: artifact {artifact} was not downloaded"
            )
            checksum = artifact.metadata[checksum_attribute_key]
            file_checksum = platform.calculate_file_crc32c(file_path)
            assert file_checksum == checksum, (
                f"Application run {application_run.run_id}: "
                f"metadata checksum != file checksum {checksum} <> {file_checksum}"
            )


client = platform.Client(cache_token=False)

for version in client.versions.list(application="he-tme"):
    print(version)

# apps = []
# print("Applications:")
# for i in client.applications.list():
#     print(i)
#     apps.append(i)
#
# print("Versions:")
# versions = []
# for app in apps:
#     for version in client.versions.list(application=app.application_id):
#         print(f"{app.application_id}: {version} {version.number}")
#         versions.append((app.application_id, version.number))
#
# print("Version Details:")
# for version in versions:
#     version_details = client.versions.details(version[0], version[1])
#     print(version_details)


# app_run_id = client.runs.create(
#     application_id="test-app",
#     application_version="0.0.3",
#     custom_metadata={"pub_api_test": True},
#     items=[
#         platform.InputItem(
#             external_id="1",
#             custom_metadata={
#                 "key": "1"
#             },
#             input_artifacts=[
#                 platform.InputArtifact(
#                     name="user_slide",
#                     download_url=platform.generate_signed_url(
#                         "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
#                         360,
#                     ),
#                     metadata={
#                         "checksum_base64_crc32c": "9l3NNQ==",
#                         "width_px": 3728,
#                         "height_px": 3640,
#                         "resolution_mpp": 0.46499982,
#                     },
#                 )
#             ],
#         ),
#         platform.InputItem(
#             external_id="2",
#             input_artifacts=[
#                 platform.InputArtifact(
#                     name="user_slide",
#                     download_url=platform.generate_signed_url(
#                         "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff",
#                         360,
#                     ),
#                     metadata={
#                         "checksum_base64_crc32c": "w+ud3g==",
#                         "width_px": 3616,
#                         "height_px": 3400,
#                         "resolution_mpp": 0.46499982,
#                     },
#                 )
#             ],
#         ),
#         platform.InputItem(
#             external_id="3",
#             custom_metadata={
#                 "key": "3"
#             },
#             input_artifacts=[
#                 platform.InputArtifact(
#                     name="user_slide",
#                     download_url=platform.generate_signed_url(
#                         "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff",
#                         360,
#                     ),
#                     metadata={
#                         "checksum_base64_crc32c": "Zmx0wA==",
#                         "width_px": 4016,
#                         "height_px": 3952,
#                         "resolution_mpp": 0.46499982,
#                     },
#                 )
#             ],
#         ),
#     ],
# )
#
# print(app_run_id)

# for run in client.runs.list():
#     print(run)

# run = ApplicationRun.for_run_id(run_id="f2222c26-ba60-43f2-b3fa-20bbd875e476")
#
# with tempfile.TemporaryDirectory() as temp_dir:
#     run.download_to_folder(temp_dir)
#     validate the output
    # _validate_output(run, Path(temp_dir))
#