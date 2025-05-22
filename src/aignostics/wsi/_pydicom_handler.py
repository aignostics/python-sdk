"""Handler for wsi files using Pydicom."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import highdicom as hd
import numpy as np
import pydicom
import pydicom.errors
from pydicom.sr.codedict import codes
from pydicom.sr.coding import Code
from shapely.geometry import Polygon

from aignostics.utils import console, get_logger

logger = get_logger(__name__)


class PydicomHandler:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    @classmethod
    def from_file(cls, path: str | Path) -> "PydicomHandler":
        """Create a PydicomHandler instance from a file or directory path.

        Args:
            path (str | Path): Path to the DICOM file or directory.

        Returns:
            PydicomHandler: An instance of PydicomHandler.
        """
        return cls(Path(path))

    def get_metadata(self, verbose: bool = False) -> dict[str, Any]:
        files = self._scan_files(verbose)
        return self._organize_by_hierarchy(files)

    def _scan_files(self, verbose: bool = False) -> list[dict[str, Any]]:  # noqa: C901, PLR0912, PLR0914, PLR0915
        dicom_files = []

        for file_path in self.path.rglob("*.dcm"):  # noqa: PLR1702
            if not file_path.is_file():
                continue

            try:
                print(file_path)
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                # TODO(Helmut): Uncomment when DICOM is implemented
                # print(ds["Modality"].value)  # noqa: ERA001
                # print(getattr(ds, "Modality", "unknown"))  # noqa: ERA001
                # sys.exit()  # noqa: ERA001

                # Basic required DICOM fields
                file_info: dict[str, Any] = {
                    "path": str(file_path),
                    "study_uid": str(getattr(ds, "StudyInstanceUID", "unknown")),
                    "container_id": str(getattr(ds, "ContainerIdentifier", "unknown")),
                    "series_uid": str(getattr(ds, "SeriesInstanceUID", "unknown")),
                    "modality": str(getattr(ds, "Modality", "unknown")),
                    "type": "unknown",
                    "frame_of_reference_uid": str(getattr(ds, "FrameOfReferenceUID", "unknown")),
                }

                # Try to determine file type using highdicom
                try:
                    # TODO(Helmut): Check below, hd.sr.is_microscopy_bulk_simple_annotation(ds),
                    # hd.sr.is_microscopy_measurement(ds) for type annotation/measurement
                    if getattr(ds, "Modality", "") in {"SM", "WSI"}:
                        file_info["type"] = "image"
                except Exception:
                    logger.exception("Failed to analyze DICOM file with highdicom")
                    # If highdicom analysis fails, keep 'unknown' type

                # Add size and basic metadata
                file_info["size"] = file_path.stat().st_size
                file_info["metadata"] = {
                    "PatientID": str(getattr(ds, "PatientID", "unknown")),
                    "StudyDate": str(getattr(ds, "StudyDate", "unknown")),
                    "SeriesDescription": str(getattr(ds, "SeriesDescription", "")),
                }

                # Add to file_info dictionary after basic metadata
                if getattr(ds, "Modality", "") in {"SM", "WSI"}:
                    file_info.update({
                        "modality": getattr(ds, "Modality", ""),
                        "is_pyramidal": True,
                        "num_frames": int(getattr(ds, "NumberOfFrames", 1)),
                        "optical_paths": len(getattr(ds, "OpticalPathSequence", [])),
                        "focal_planes": len(getattr(ds, "DimensionIndexSequence", [])),
                        "total_pixel_matrix": (
                            int(getattr(ds, "TotalPixelMatrixColumns", 0)),
                            int(getattr(ds, "TotalPixelMatrixRows", 0)),
                        ),
                    })
                elif getattr(ds, "Modality", "") == "ANN":
                    ann = hd.ann.MicroscopyBulkSimpleAnnotations.from_dataset(ds)
                    group_infos = []
                    groups = ann.get_annotation_groups()
                    for group in groups:
                        # Calculate min/max coordinates for all points
                        col_min = row_min = float("inf")  # Initialize to positive infinity
                        col_max = row_max = float("-inf")  # Initialize to negative infinity
                        graphic_data_len = float("-inf")
                        first = None

                        if verbose:
                            graphic_data = group.get_graphic_data(ann.annotation_coordinate_type)
                            graphic_data_len = len(graphic_data)
                            first = graphic_data[0]
                            if graphic_data:
                                if group.graphic_type == hd.ann.GraphicTypeValues.POINT:
                                    # For points, each item is a single coordinate
                                    for point in graphic_data:
                                        col_min = min(col_min, point[0])
                                        col_max = max(col_max, point[0])
                                        row_min = min(row_min, point[1])
                                        row_max = max(row_max, point[1])
                                else:
                                    # For polygons/polylines, process all polygons
                                    for polygon in graphic_data:
                                        for point in polygon:
                                            col_min = min(col_min, point[0])
                                            col_max = max(col_max, point[0])
                                            row_min = min(row_min, point[1])
                                            row_max = max(row_max, point[1])

                        group_infos.append({
                            "uid": group.uid,
                            "label": group.label,
                            "property_type": group.annotated_property_type,
                            "graphic_type": group.graphic_type,
                            "count": graphic_data_len,
                            "first": first,
                            "col_min": float(col_min),
                            "row_min": float(row_min),
                            "col_max": float(col_max),
                            "row_max": float(row_max),
                        })
                    file_info.update({
                        "modality": "ANN",
                        "coordinate_type": ann.annotation_coordinate_type,
                        "annotation_groups": group_infos,
                    })

                # Extract pyramid levels from frame organization
                if getattr(ds, "DimensionOrganizationSequence", None):
                    # Get frame organization
                    frame_groups = {}
                    for frame in getattr(ds, "PerFrameFunctionalGroupsSequence", []):
                        level_idx = frame.DimensionIndexValues[0]
                        if level_idx not in frame_groups:
                            frame_groups[level_idx] = {
                                "count": 0,
                                "rows": int(frame.get("Rows", 0)),
                                "columns": int(frame.get("Columns", 0)),
                            }
                        frame_groups[level_idx]["count"] += 1

                    # Sort and store pyramid level information
                    pyramid_info = [
                        {
                            "level": int(level_idx),
                            "frame_count": frame_groups[level_idx]["count"],
                            "frame_size": (
                                frame_groups[level_idx]["columns"],
                                frame_groups[level_idx]["rows"],
                            ),
                        }
                        for level_idx in sorted(frame_groups.keys())
                    ]
                    file_info["pyramid_info"] = pyramid_info

                dicom_files.append(file_info)

            except pydicom.errors.InvalidDicomError:
                continue

        return dicom_files

    @staticmethod
    def _organize_by_hierarchy(files: list[dict[str, Any]]) -> dict[str, Any]:
        if not files:
            return {"type": "empty", "message": "No DICOM files found"}

        if len(files) == 1:
            return {"type": "file", "file_info": files[0]}

        # Group by study -> container -> series
        studies = defaultdict(
            lambda: {
                "study_info": {
                    "study_uid": "",
                    "study_id": "",
                    "study_date": "",
                    "study_time": "",
                    "accession_number": "",
                },
                "patient_info": {"id": "", "name": "", "gender": "", "birth_date": ""},
                "clinical_trial": {
                    "sponsor_name": "",
                    "protocol_id": "",
                    "protocol_name": "",
                    "site_name": "",
                },
                "slides": defaultdict(
                    lambda: {
                        "specimen_info": {
                            "description": "",
                            "anatomical_structure": "",
                            "collection_method": "",
                            "parent_specimens": [],
                            "embedding_medium": "",
                        },
                        "equipment_info": {
                            "manufacturer": "",
                            "model_name": "",
                            "device_serial_number": "",
                            "software_version": "",
                            "institution_name": "",
                        },
                        "series": defaultdict(lambda: {"description": "", "modality": "", "files": []}),
                    }
                ),
            }
        )

        for file_info in files:
            study_uid = file_info["study_uid"]
            container_id = file_info["container_id"]
            series_uid = file_info["series_uid"]
            ds = pydicom.dcmread(file_info["path"], stop_before_pixels=True)

            # Update study info if not already set
            if not studies[study_uid]["study_info"]["study_id"]:
                studies[study_uid]["study_info"].update({
                    "study_uid": study_uid,
                    "study_id": str(getattr(ds, "StudyID", "")),
                    "study_date": str(getattr(ds, "StudyDate", "")),
                    "study_time": str(getattr(ds, "StudyTime", "")),
                    "accession_number": str(getattr(ds, "AccessionNumber", "")),
                })

                # Update patient info
                studies[study_uid]["patient_info"].update({
                    "id": str(getattr(ds, "PatientID", "")),
                    "name": str(getattr(ds, "PatientName", "")),
                    "gender": str(getattr(ds, "PatientSex", "")),
                    "birth_date": str(getattr(ds, "PatientBirthDate", "")),
                })

                # Update clinical trial info
                studies[study_uid]["clinical_trial"].update({
                    "sponsor_name": str(getattr(ds, "ClinicalTrialSponsorName", "")),
                    "protocol_id": str(getattr(ds, "ClinicalTrialProtocolID", "")),
                    "protocol_name": str(getattr(ds, "ClinicalTrialProtocolName", "")),
                    "site_name": str(getattr(ds, "ClinicalTrialSiteName", "")),
                })

            # Update series info if not already set
            series = studies[study_uid]["slides"][container_id]["series"][series_uid]
            if not series["description"]:
                series.update({
                    "description": str(getattr(ds, "SeriesDescription", "")),
                    "modality": str(getattr(ds, "Modality", "")),
                })

            # Add file-specific info only
            file_specific = {
                "path": file_info["path"],
                "size": Path(file_info["path"]).stat().st_size,
                "instance_uid": str(getattr(ds, "SOPInstanceUID", "")),
                "frame_of_reference_uid": str(getattr(ds, "FrameOfReferenceUID", "")),
                "type": file_info["type"],
                "dimensions": None,  # Initialize dimensions as None,
            }

            # Add generic image dimensions for any image type
            if hasattr(ds, "Rows") and hasattr(ds, "Columns"):
                file_specific["dimensions"] = (int(ds.Rows), int(ds.Columns))
                file_specific["photometric_interpretation"] = str(getattr(ds, "PhotometricInterpretation", ""))
                file_specific["bits_allocated"] = int(getattr(ds, "BitsAllocated", 0))
                file_specific["bits_stored"] = int(getattr(ds, "BitsStored", 0))
                file_specific["samples_per_pixel"] = int(getattr(ds, "SamplesPerPixel", 0))
                file_specific["image_type"] = getattr(ds, "ImageType", [])

            # Copy pyramidal information if present
            if file_info.get("is_pyramidal"):
                file_specific.update({
                    "is_pyramidal": True,
                    "num_frames": file_info["num_frames"],
                    "optical_paths": file_info["optical_paths"],
                    "focal_planes": file_info["focal_planes"],
                    "total_pixel_matrix": file_info["total_pixel_matrix"],
                })
                if file_info.get("pyramid_info"):
                    file_specific["pyramid_info"] = file_info["pyramid_info"]
            else:
                file_specific.update(file_info)

            series["files"].append(file_specific)

            # Update the specimen and equipment info when processing files
            if not studies[study_uid]["slides"][container_id]["specimen_info"]["description"]:
                studies[study_uid]["slides"][container_id]["specimen_info"].update({
                    "description": str(
                        getattr(ds, "SpecimenDescriptionSequence", [""])[0].get("SpecimenShortDescription", "")
                        if getattr(ds, "SpecimenDescriptionSequence", [])
                        else ""
                    ),
                    "anatomical_structure": str(
                        getattr(ds, "SpecimenDescriptionSequence", [""])[0]
                        .get("PrimaryAnatomicStructureSequence", [{}])[0]
                        .get("CodeMeaning", "")
                        if getattr(ds, "SpecimenDescriptionSequence", [])
                        else ""
                    ),
                    "collection_method": str(
                        getattr(ds, "SpecimenDescriptionSequence", [""])[0].get(
                            "SpecimenCollectionProcedureDescription", ""
                        )
                        if getattr(ds, "SpecimenDescriptionSequence", [])
                        else ""
                    ),
                    "parent_specimens": [
                        str(x.get("SpecimenIdentifier", ""))
                        for x in getattr(ds, "SpecimenDescriptionSequence", [])
                        if x.get("SpecimenIdentifier")
                    ],
                    "embedding_medium": str(
                        getattr(ds, "SpecimenDescriptionSequence", [""])[0].get("SpecimenEmbeddingMethod", "")
                        if getattr(ds, "SpecimenDescriptionSequence", [])
                        else ""
                    ),
                })

                studies[study_uid]["slides"][container_id]["equipment_info"].update({
                    "manufacturer": str(getattr(ds, "Manufacturer", "")),
                    "model_name": str(getattr(ds, "ManufacturerModelName", "")),
                    "device_serial_number": str(getattr(ds, "DeviceSerialNumber", "")),
                    "software_version": str(getattr(ds, "SoftwareVersions", "")),
                    "institution_name": str(getattr(ds, "InstitutionName", "")),
                })

        return {"type": "root", "studies": studies}

    def __enter__(self) -> "PydicomHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        return

    @staticmethod
    def geojson_import(dicom_path: Path, geojson_path: Path) -> bool:  # noqa: C901, PLR0912, PLR0914, PLR0915
        """Convert GeoJSON to DICOM ANN instance.

        Args:
            dicom_path (Path): Path to the DICOM directory.
            geojson_path (Path): Path to the GeoJSON file.

        Returns:
            bool: True if the import was successful, False otherwise.
        """
        try:
            with open(geojson_path, encoding="utf-8") as f:
                geojson_data = json.load(f)

            largest_file = None
            largest_dimension = 0

            # determine the largest image in the directory
            for file_path in dicom_path.rglob("*"):
                if not file_path.is_file():
                    continue

                try:
                    ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                    if getattr(ds, "Modality", "") in {"SM", "WSI"}:
                        columns = int(getattr(ds, "TotalPixelMatrixColumns", 0))
                        rows = int(getattr(ds, "TotalPixelMatrixRows", 0))
                        dimension = columns * rows

                        if dimension > largest_dimension:
                            largest_dimension = dimension
                            largest_file = file_path

                except pydicom.errors.InvalidDicomError as e:
                    console.print(f"Failed to process file {file_path}: {e}")
                    continue

            if largest_file:
                ds = pydicom.dcmread(str(largest_file), stop_before_pixels=True)
                columns = int(getattr(ds, "TotalPixelMatrixColumns", 0))
                rows = int(getattr(ds, "TotalPixelMatrixRows", 0))
                graphic_data = []
                graphic_types = []
                area_measurement_values = []

                for feature in geojson_data["features"]:
                    # We consider the outer geometry only,
                    # not additional in properties of a feature (as is used for the "cell" objectType)
                    geometry = feature["geometry"]

                    if geometry["type"] == "Point":
                        coordinates = np.array(geometry["coordinates"], dtype=np.float32)
                        if not (0 <= coordinates[0] < columns and 0 <= coordinates[1] < rows):
                            console.print(f"Point coordinates {coordinates} out of bounds")
                            continue
                        graphic_data.append(coordinates)
                        graphic_types.append(hd.ann.GraphicTypeValues.POINT)

                    elif geometry["type"] == "Polygon":
                        # DICOM does only contain simple polygons, without holes
                        coordinates = np.array(geometry["coordinates"][0], dtype=np.float32)
                        # Remove last point if it's identical to first (closed polygon)
                        if np.array_equal(coordinates[0], coordinates[-1]):
                            coordinates = coordinates[:-1]

                        # convert to use shapely
                        polygon = Polygon(coordinates)

                        # Check if enough points remain for valid polygon
                        if not polygon.is_valid:
                            console.print("Not a valid polygon")
                            continue

                        # Check if coordinates are within bounds
                        in_bounds = Polygon([
                            (0, 0),
                            (columns, 0),
                            (columns, rows),
                            (0, rows),
                        ]).contains(polygon)
                        if not in_bounds:
                            continue

                        # Add polygon data
                        graphic_data.append(coordinates)
                        graphic_types.append(hd.ann.GraphicTypeValues.POLYGON)

                        # Add measurements
                        area_measurement_values.append(np.float32(polygon.area))

                    else:
                        continue

                area_measurement = hd.ann.Measurements(
                    name=codes.SCT.Area,
                    unit=codes.UCUM.SquareMicrometer,
                    values=np.array(area_measurement_values, dtype=np.float32),
                )

                annotation_group = hd.ann.AnnotationGroup(
                    number=1,
                    uid=pydicom.uid.generate_uid(),  # type: ignore
                    label="Cell nuclei",
                    description="Generated by Orion CLI",
                    annotated_property_category=codes.SCT.AnatomicalStructure,
                    annotated_property_type=Code(
                        "84640000", "SCT", "Nucleus"
                    ),  # https://termbrowser.nhs.uk/?perspective=full&conceptId1=84640000&edition=uk-edition&release=v20240925&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104
                    algorithm_type=hd.ann.AnnotationGroupGenerationTypeValues.AUTOMATIC,
                    algorithm_identification=hd.AlgorithmIdentificationSequence(
                        "aignx:heta",
                        hd.sr.CodedConcept(  # https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_cid_7162.html
                            "123110", "DCM", "Artificial Intelligence"
                        ),
                        "0.0.1",
                        source="Aignostics GmbH (https://www.aignostics.com)",
                        parameters={"runtime": "PAPI"},
                    ),
                    graphic_type=(graphic_types[0] if graphic_types else hd.ann.GraphicTypeValues.POINT),
                    graphic_data=graphic_data,
                    measurements=[area_measurement],
                )

                bulk_annotations = hd.ann.MicroscopyBulkSimpleAnnotations(
                    source_images=[ds],
                    annotation_coordinate_type=hd.ann.AnnotationCoordinateTypeValues.SCOORD,
                    annotation_groups=[annotation_group],
                    series_instance_uid=pydicom.uid.generate_uid(),
                    series_number=10,
                    sop_instance_uid=pydicom.uid.generate_uid(),
                    instance_number=1,
                    manufacturer="Aignostics GmbH",
                    manufacturer_model_name="aignx:heta",
                    software_versions="0.0.1",
                    device_serial_number="1234",
                    content_description=f"{geojson_path.stem} Annotations",
                )

                output_filename = f"{geojson_path.stem}_annotations.dcm"
                bulk_annotations.save_as(str(dicom_path / output_filename))

            return True

        except (OSError, json.JSONDecodeError) as e:
            console.print(f"Failed to import GeoJSON: {e}")
            return False
