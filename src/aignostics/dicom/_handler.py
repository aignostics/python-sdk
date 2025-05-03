import datetime
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import highdicom as hd
import numpy as np
import pydicom
import pydicom.errors
import wsidicom
import wsidicom.conceptcode
import wsidicom.file
import wsidicom.metadata
from dicom_validator.spec_reader.edition_reader import EditionReader
from dicom_validator.validator.dicom_file_validator import DicomFileValidator
from pydicom.sr.codedict import codes
from pydicom.sr.coding import Code
from shapely.geometry import Polygon
from wsidicomizer.metadata import WsiDicomizerMetadata
from wsidicomizer.wsidicomizer import WsiDicomizer

from aignostics.utils import console, get_logger

logger = get_logger(__name__)


class DicomHandler:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    @classmethod
    def from_file(cls, path: str | Path) -> "DicomHandler":
        """Create a DicomHandler instance from a file or directory path.

        Args:
            path (str | Path): Path to the DICOM file or directory.

        Returns:
            DicomHandler: An instance of DicomHandler.
        """
        return cls(Path(path))

    def get_metadata(self, verbose: bool = False) -> dict[str, Any]:
        files = self._scan_files(verbose)
        return self._organize_by_hierarchy(files)

    def _scan_files(self, verbose: bool = False) -> list[dict[str, Any]]:  # noqa: C901, PLR0912, PLR0915
        dicom_files = []

        for file_path in self.path.rglob("*"):  # noqa: PLR1702
            if not file_path.is_file():
                continue

            try:
                print(file_path)
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                print(ds)
                continue
                # print(ds["Modality"].value)
                # print(getattr(ds, "Modality", "unknown"))
                # sys.exit()

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
                    if hd.sr.is_microscopy_bulk_simple_annotation(ds):
                        file_info["type"] = "annotation"
                    elif hd.sr.is_microscopy_measurement(ds):
                        file_info["type"] = "measurement"
                    elif getattr(ds, "Modality", "") in {"SM", "WSI"}:
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
                    assert isinstance(ann, hd.ann.MicroscopyBulkSimpleAnnotations)
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
                    pyramid_info = []
                    for level_idx in sorted(frame_groups.keys()):
                        pyramid_info.append({
                            "level": int(level_idx),
                            "frame_count": frame_groups[level_idx]["count"],
                            "frame_size": (
                                frame_groups[level_idx]["columns"],
                                frame_groups[level_idx]["rows"],
                            ),
                        })
                    file_info["pyramid_info"] = pyramid_info

                dicom_files.append(file_info)

            except pydicom.errors.InvalidDicomError:
                continue

        return dicom_files

    def _organize_by_hierarchy(self, files: list[dict[str, Any]]) -> dict[str, Any]:
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

    def __enter__(self) -> "DicomHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass  # No cleanup needed for now

    def _get_specimen_info(self, ds) -> dict:
        """Extract specimen information from DICOM dataset.

        Args:
            ds: The DICOM dataset from which to extract specimen information.

        Returns:
            dict: A dictionary containing specimen information
        """
        specimen_info = {
            "description": "",
            "anatomical_structure": "",
            "collection_method": "",
            "parent_specimens": [],
            "embedding_medium": "",
        }

        # Get specimen sequence
        specimen_seq = getattr(ds, "SpecimenPreparationSequence", [])
        if specimen_seq:
            # Get description from first item
            specimen_info["description"] = str(getattr(ds, "ContainerDescription", ""))

            for item in specimen_seq:
                # Collect all parent specimen IDs
                if hasattr(item, "ParentSpecimenSequence"):
                    for parent in item.ParentSpecimenSequence:
                        parent_id = str(getattr(parent, "SpecimenIdentifier", ""))
                        if parent_id and parent_id not in specimen_info["parent_specimens"]:
                            specimen_info["parent_specimens"].append(parent_id)

                # Get first non-empty values for other fields
                if not specimen_info["anatomical_structure"]:
                    specimen_info["anatomical_structure"] = str(getattr(item, "PrimaryAnatomicStructure", ""))
                if not specimen_info["collection_method"]:
                    specimen_info["collection_method"] = str(getattr(item, "SamplingMethodDescription", ""))
                if not specimen_info["embedding_medium"]:
                    specimen_info["embedding_medium"] = str(getattr(item, "FixationMethod", ""))

        return specimen_info

    @staticmethod
    def geojson_import(dicom_path: Path, geojson_path: Path) -> bool:
        """Convert GeoJSON to DICOM ANN instance"""
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
                    if getattr(ds, "Modality", "") in ["SM", "WSI"]:
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
                    uid=pydicom.uid.generate_uid(),
                    label="Cell nuclei",
                    description="Generated by Orion CLI",
                    annotated_property_category=codes.SCT.AnatomicalStructure,
                    # annotated_property_type=Code('53982002', "SCT", "Cell membrane"),
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

    @staticmethod
    def default_metadata(id_base: int) -> WsiDicomizerMetadata:
        no = id_base
        study = wsidicom.metadata.Study(
            identifier=f"Study id {no}",
            accession_number=f"Accession {no}",
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            referring_physician_name="Dr. Who",
        )
        series = wsidicom.metadata.Series(number=no)
        patient = wsidicom.metadata.Patient(
            identifier="helmuthva",
            name="Hoffer von Ankershoffen^Helmut",
            birth_date=datetime.date(1973, 9, 30),
            sex=wsidicom.metadata.PatientSex("male"),
        )
        label = wsidicom.metadata.Label(
            text="Label text",
            barcode="123",
            label_in_volume_image=True,
            label_in_overview_image=False,
            label_is_phi=False,
        )
        equipment = wsidicom.metadata.Equipment(
            manufacturer="Scanner manufacturer",
            model_name="Scanner model name",
            device_serial_number="Scanner serial number",
            software_versions=["Scanner software versions"],
        )
        specimen = wsidicom.metadata.Specimen(
            identifier=f"spec {no}",
            extraction_step=wsidicom.metadata.Collection(
                method=wsidicom.conceptcode.SpecimenCollectionProcedureCode("Excision")
            ),
            type=wsidicom.conceptcode.AnatomicPathologySpecimenTypesCode("Gross specimen"),
            container=wsidicom.conceptcode.ContainerTypeCode("Specimen container"),
            steps=[
                wsidicom.metadata.Fixation(
                    fixative=wsidicom.conceptcode.SpecimenFixativesCode("Neutral Buffered Formalin")
                )
            ],
        )
        optical_path = wsidicom.metadata.OpticalPath(
            identifier=f"opt {no}",
            description="Optical path description",
            illumination_types=[wsidicom.conceptcode.IlluminationCode("Brightfield illumination")],
            illumination=wsidicom.conceptcode.IlluminationColorCode("Full spectrum"),
            # light_path_filter=wsidicom.metadata.LightPathFilter(
            #   filters=[wsidicom.conceptcode.LightPathFilterCode("Hoffman modulator")],
            #    nominal=1,
            #    low_pass=-0,
            #    high_pass=3
            # ),
            # image_path_filter=wsidicom.metadata.ImagePathFilter(
            #    filters=[wsidicom.conceptcode.ImagePathFilterCode("Condenser annulus")],
            #    nominal=1,
            #    low_pass=-0,
            #    high_pass=3
            # ),
            objective=wsidicom.metadata.Objectives(
                lenses=[wsidicom.conceptcode.LenseCode("High power non-immersion lens")],
                condenser_power=2525,
                objective_power=4711,
                objective_numerical_aperture=1.0,
            ),
        )
        block = wsidicom.metadata.Sample(
            identifier=f"block/sample {no}",
            sampled_from=[specimen.sample(method=wsidicom.conceptcode.SpecimenSamplingProcedureCode("Dissection"))],
            type=wsidicom.conceptcode.AnatomicPathologySpecimenTypesCode("tissue specimen"),
            container=wsidicom.conceptcode.ContainerTypeCode("Tissue cassette"),
            steps=[wsidicom.metadata.Embedding(medium=wsidicom.conceptcode.SpecimenEmbeddingMediaCode("Paraffin wax"))],
        )
        slide_sample = wsidicom.metadata.SlideSample(
            identifier=f"Sample {no}",
            sampled_from=block.sample(method=wsidicom.conceptcode.SpecimenSamplingProcedureCode("Block sectioning")),
        )
        slide = wsidicom.metadata.Slide(
            identifier=f"Slide {no}",
            stainings=[
                wsidicom.metadata.Staining(
                    substances=[
                        wsidicom.conceptcode.SpecimenStainsCode("hematoxylin stain"),
                        wsidicom.conceptcode.SpecimenStainsCode("water soluble eosin stain"),
                    ]
                )
            ],
            samples=[slide_sample],
        )
        metadata = WsiDicomizerMetadata(
            study=study,
            series=series,
            patient=patient,
            equipment=equipment,
            optical_paths=[optical_path],
            slide=slide,
            label=label,
        )
        return metadata

    @staticmethod
    def wsi_convert(wsi_path: Path, dicom_path: Path, id_base: int) -> bool:
        """Convert whole slide image to DICOM SM series.

        Args:
            wsi_path (Path): Path to the WSI file.
            dicom_path (Path): Path to save the DICOM file.
            id_base (int): Base ID for generating unique identifiers.

        Returns:
            bool: True if conversion was successful, False otherwise.
        """
        try:
            console.print(wsi_path)
            console.print(dicom_path)
            created_files = WsiDicomizer.convert(
                filepath=wsi_path,
                output_path=dicom_path,
                metadata=DicomHandler.default_metadata(id_base),
                default_metadata=None,
                tile_size=256,
                add_missing_levels=True,
                include_label=True,
                include_overview=True,
                include_confidential=True,
                workers=None,  # Use all available cores
                chunk_size=None,  # Use 16
                encoding=None,
                offset_table=wsidicom.file.OffsetTableType.BASIC,
                label=None,
            )
            console.print(created_files)
            return True

        except Exception:
            logger.exception("Error converting WSI to DICOM")
            return False

    @staticmethod
    def load_datasets(dicom_path: Path, full: bool) -> list[pydicom.FileDataset]:
        """Load datasets from file or directory"""
        datasets = []
        # Handle directory or glob pattern
        if "*" in str(dicom_path):
            files = Path().glob(str(dicom_path))
        else:
            path = Path(dicom_path)
            files = path.rglob("*") if path.is_dir() else [path]

        for file_path in files:
            if not file_path.is_file():
                continue
            try:
                console.print(f"{file_path} ...")
                if full:
                    dataset = pydicom.dcmread(file_path)
                else:
                    dataset = pydicom.dcmread(file_path, defer_size=True, stop_before_pixels=True)
                datasets.append(dataset)
            except pydicom.errors.InvalidDicomError:
                console.print(f"Skipping non-DICOM file: {file_path}")
                continue
        return datasets

    @staticmethod
    def validate(
        dicom_path: Path,
        *,
        standard_path: Path = None,
        revision: str = "current",
        force_read: bool = False,
        suppress_vr_warnings: bool = False,
        recreate_json: bool = False,
        verbose: bool = False,
    ) -> int:
        """Validate DICOM files using dicom-validator.

        Args:
            dicom_path: Path or glob pattern to DICOM files
            standard_path: Path to DICOM validator files
            revision: DICOM standard revision to use
            force_read: Whether to force read non-DICOM files
            suppress_vr_warnings: Whether to suppress VR warnings
            recreate_json: Whether to recreate JSON files

        Returns:
            Number of validation errors found
        """
        if standard_path is None:
            standard_path = Path.home() / "dicom-validator"

        try:
            # Setup validator
            edition_reader = EditionReader(standard_path)
            destination = edition_reader.get_revision(revision, recreate_json, True)
            if destination is None:
                logger.error("Failed to get DICOM edition %s - aborting", revision)
                return 1

            json_path = Path(destination, "json")
            dicom_info = EditionReader.load_dicom_info(json_path)
            validator = DicomFileValidator(
                dicom_info,
                force_read=force_read,
                suppress_vr_warnings=suppress_vr_warnings,
            )

            # Process files
            total_errors = 0
            total_files = 0

            # Get all file paths
            if "*" in str(dicom_path):
                files = Path().glob(str(dicom_path))
            else:
                path = Path(dicom_path)
                files = path.rglob("*") if path.is_dir() else [path]

            # Validate each file path
            for file_path in files:
                if not file_path.is_file():
                    continue
                total_files += 1
                dataset = pydicom.dcmread(file_path, stop_before_pixels=True)
                if dataset.SOPClassUID == "1.2.840.10008.5.1.4.1.1.91.1":
                    # skip for ANN (bulk annotations)
                    continue
                errors = validator.validate(file_path)
                error_count = sum(len(err_list) for err_list in errors.values())
                total_errors += error_count

                if error_count > 0:
                    logger.error("Validation errors in %s:", file_path)
                    for tag, err_list in errors.items():
                        for error in err_list:
                            logger.error("%s: %s", tag, error)
                else:
                    logger.info("%s is valid", file_path)

            if total_files == 0:
                logger.warning("No DICOM files found matching pattern: %s", dicom_path)
            else:
                logger.info("Validated %d files with %d total errors", total_files, total_errors)

            return total_errors

        except ValueError:
            logger.exception("Validation failed")
            return 1
        except OSError:
            logger.exception("File system error")
            return 1
