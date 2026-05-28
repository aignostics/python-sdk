"""Utils for printing wsi files."""

from collections import defaultdict
from pathlib import Path
from typing import Any

import humanize
import pydicom
from loguru import logger

from aignostics.utils import console


def print_file_info(file_info: dict[str, Any], indent: int = 0) -> None:  # noqa: C901, PLR0912, PLR0915
    """Print formatted file information.

    Args:
        file_info (dict): Dictionary containing file information.
        indent (int): Indentation level for formatting.
    """
    prefix = "  " * indent

    # Keep existing basic info
    console.print(f"{prefix}[key]Path:[/key] {Path(file_info['path']).name}")
    console.print(f"{prefix}[key]Size:[/key] {humanize.naturalsize(file_info['size'])}")
    console.print(f"{prefix}[key]Type:[/key] {file_info['type']}")

    if "instance_uid" in file_info:
        console.print(f"{prefix}[key]Instance UID:[/key] {file_info['instance_uid']}")

    console.print(f"{prefix}[key]Frame of reference UID:[/key] {file_info['frame_of_reference_uid']}")

    # Add WSI/pyramidal specific information

    if file_info.get("is_pyramidal"):
        console.print(f"{prefix}[key]Image Type:[/key] Pyramidal WSI")
        console.print(f"{prefix}[key]Number of Frames:[/key] {file_info['num_frames']}")
        if file_info.get("optical_paths"):
            console.print(f"{prefix}[key]Optical Paths:[/key] {file_info['optical_paths']}")
        if file_info.get("focal_planes"):
            console.print(f"{prefix}[key]Focal Planes:[/key] {file_info['focal_planes']}")
        if file_info.get("total_pixel_matrix"):
            matrix = file_info["total_pixel_matrix"]
            console.print(f"{prefix}[key]Total Pixel Matrix:[/key] {matrix[0]} x {matrix[1]}")

    if file_info.get("modality") == "ANN":
        console.print(f"{prefix}[key]Coordinate type:[/key] {file_info['coordinate_type']}")
        console.print(f"{prefix}[key]Annotation Groups:[/key] {len(file_info['annotation_groups'])}")
        prefix = "  " + prefix
        for group in file_info["annotation_groups"]:
            console.print("")
            console.print(f"{prefix}[key]UUID:[/key] {group['uid']}")
            console.print(f"{prefix}[key]Label:[/key] {group['label']}")
            console.print(f"{prefix}[key]Property type:[/key] {group['property_type']}")
            console.print(f"{prefix}[key]Graphic type:[/key] {group['graphic_type']}")
            console.print(f"{prefix}[key]Count:[/key] {group['count']}")
            col_range = f"[{group['col_min']:.1f}, {group['col_max']:.1f}]"
            row_range = f"[{group['row_min']:.1f}, {group['row_max']:.1f}]"
            console.print(f"{prefix}[key]Column [Min,Max]:[/key] {col_range}")
            console.print(f"{prefix}[key]Row [Min,Max]:[/key] {row_range}")
            console.print(f"{prefix}[key]First:[/key] {group['first']}")
        console.print("")

    prefix = "  " * indent

    # Keep existing image-specific information
    if "dimensions" in file_info:
        if isinstance(file_info["dimensions"], tuple):
            dim_str = f"{file_info['dimensions'][0]} x {file_info['dimensions'][1]}"
        else:
            dim_str = str(file_info["dimensions"])
        console.print(f"{prefix}[key]Dimensions:[/key] {dim_str}")

        if "photometric_interpretation" in file_info:
            console.print(f"{prefix}[key]Color Space:[/key] {file_info['photometric_interpretation']}")

        if "bits_allocated" in file_info and "bits_stored" in file_info:
            bits_str = f"{file_info['bits_allocated']} allocated, {file_info['bits_stored']} stored"
            console.print(f"{prefix}[key]Bits:[/key] {bits_str}")

        if "samples_per_pixel" in file_info:
            console.print(f"{prefix}[key]Samples per Pixel:[/key] {file_info['samples_per_pixel']}")

        if "image_type" in file_info:
            console.print(f"{prefix}[key]DICOM Image Type:[/key] {' / '.join(file_info['image_type'])}")

    if file_info.get("pyramid_info"):
        console.print(f"\n{prefix}[key]Pyramid Structure:[/key]")
        for level in file_info["pyramid_info"]:
            frame_size = f"{level['frame_size'][0]} x {level['frame_size'][1]}"
            console.print(f"{prefix}  Level {level['level']}: {level['frame_count']} frames @ {frame_size} pixels")


def print_series_info(series_data: dict[str, Any], indent: int = 0) -> None:
    """Print formatted series information."""
    prefix = "  " * indent
    console.print(f"{prefix}[key]Files:[/key] {series_data['file_count']}")
    console.print(f"{prefix}[key]Modality:[/key] {series_data['modality']}")


def format_dicom_time(time_str: str) -> str:
    """Format DICOM time string to HH:MM:SS.

    Args:
        time_str (str): DICOM time string in the format HHMMSS.

    Returns:
        str: Formatted time string in the format HH:MM:SS or the original string if invalid.
    """
    if not time_str or len(time_str) < 6:  # noqa: PLR2004
        return time_str
    return f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}"


def print_study_info(study_data: dict[str, Any], indent: int = 0) -> None:
    """Print formatted study information.

    Args:
        study_data (dict): Dictionary containing study information.
        indent (int): Indentation level for formatting.
    """
    prefix = "  " * indent

    # Patient Section
    console.print(f"{prefix} [header]('Patient:')[/header]")
    console.print(f"{prefix}  [key]ID:[/key] {study_data['patient_info']['id']}")
    console.print(f"{prefix}  [key]Name:[/key] {study_data['patient_info']['name']}")
    console.print(f"{prefix}  [key]Gender:[/key] {study_data['patient_info']['gender']}")
    console.print(f"{prefix}  [key]Birth Date:[/key] {study_data['patient_info']['birth_date']}")

    # Study Section
    console.print(f"\n{prefix}[header]('Study:')[/header]")
    console.print(f"{prefix}  [key]Accession #:[/key] {study_data['study_info']['accession_number']}")
    console.print(f"{prefix}  [key]ID:[/key] {study_data['study_info']['study_id']}")
    console.print(f"{prefix}  [key]Date:[/key] {study_data['study_info']['study_date']}")
    console.print(f"{prefix}  [key]Time:[/key] {format_dicom_time(study_data['study_info']['study_time'])}")
    console.print(f"{prefix}  [key]UID:[/key] {study_data['study_info']['study_uid']}")

    # Clinical Trial Section
    if any(study_data["clinical_trial"].values()):  # Only show if any values exist
        console.print(f"\n{prefix}[header]('Clinical Trial:')[/header]")
        console.print(f"{prefix}  [key]Sponsor:[/key] {study_data['clinical_trial']['sponsor_name']}")
        console.print(f"{prefix}  [key]Protocol ID:[/key] {study_data['clinical_trial']['protocol_id']}")
        console.print(f"{prefix}  [key]Protocol Name:[/key] {study_data['clinical_trial']['protocol_name']}")
        console.print(f"{prefix}  [key]Site Name:[/key] {study_data['clinical_trial']['site_name']}")


def print_slide_info(slide_data: dict[str, Any], indent: int = 0, verbose: bool = False) -> None:
    """Print formatted slide (container) information.

    Args:
        slide_data (dict): Dictionary containing slide information.
        indent (int): Indentation level for formatting.
        verbose (bool): If True, print detailed file information.
    """
    prefix = "  " * indent

    # Specimen Section
    console.print(f"{prefix}[header]('Specimen:')[/header]")
    console.print(f"{prefix}  [key]Description:[/key] {slide_data['specimen_info']['description']}")
    console.print(f"{prefix}  [key]Anatomical Structure:[/key] {slide_data['specimen_info']['anatomical_structure']}")
    console.print(f"{prefix}  [key]Collection Method:[/key] {slide_data['specimen_info']['collection_method']}")
    if slide_data["specimen_info"]["parent_specimens"]:
        console.print(
            f"{prefix}  [key]Parent Specimens:[/key] {', '.join(slide_data['specimen_info']['parent_specimens'])}"
        )
    console.print(f"{prefix}  [key]Embedding Medium:[/key] {slide_data['specimen_info']['embedding_medium']}")

    # Equipment Section
    console.print(f"\n{prefix}[header]('Equipment:')[/header]")
    console.print(f"{prefix}  [key]Manufacturer:[/key] {slide_data['equipment_info']['manufacturer']}")
    console.print(f"{prefix}  [key]Model Name:[/key] {slide_data['equipment_info']['model_name']}")
    console.print(f"{prefix}  [key]Serial Number:[/key] {slide_data['equipment_info']['device_serial_number']}")
    console.print(f"{prefix}  [key]Software Version:[/key] {slide_data['equipment_info']['software_version']}")
    console.print(f"{prefix}  [key]Institution:[/key] {slide_data['equipment_info']['institution_name']}")

    # Series Section
    console.print(f"\n{prefix}[header]('Series:')[/header]")
    total_files = sum(len(series["files"]) for series in slide_data["series"].values())
    console.print(f"{prefix}  [key]Total Files:[/key] {total_files}")
    console.print(f"{prefix}  [key]Series Count:[/key] {len(slide_data['series'])}")

    # Individual Series with their files
    for series_uid, series_data in slide_data["series"].items():
        console.print(f"\n{prefix}  [key]Series UID:[/key] {series_uid}")
        console.print(f"{prefix}    [key]Description:[/key] {series_data['description']}")
        console.print(f"{prefix}    [key]Modality:[/key] {series_data['modality']}")
        console.print(f"{prefix}    [key]Files:[/key] {len(series_data['files'])}")

        # Print file details if verbose
        if verbose:
            for file_info in series_data["files"]:
                console.print()
                print_file_info(file_info, indent=indent + 3)


def _find_highest_resolution_files(
    pyramid_groups: dict[str, list[tuple[Path, int, int]]],
) -> list[Path]:
    """Find the highest resolution file for each multi-file pyramid.

    For each pyramid (identified by PyramidUID), selects the file with the
    largest total pixel count (rows x cols). All other files in the pyramid
    are excluded, as OpenSlide can find them automatically.

    Args:
        pyramid_groups: Dictionary mapping PyramidUID to list of (file_path, rows, cols).

    Returns:
        List of file paths to keep (one per pyramid, the highest resolution).

    Note:
        Single-file pyramids (only one file per PyramidUID) are included without
        comparison.
    """
    files_to_keep: list[Path] = []

    for pyramid_uid, files_with_dims in pyramid_groups.items():
        if len(files_with_dims) > 1:
            highest_res_file_with_dims = max(files_with_dims, key=lambda x: x[1] * x[2])
            highest_res_file, rows, cols = highest_res_file_with_dims
            files_to_keep.append(highest_res_file)

            logger.debug(
                f"DICOM pyramid {pyramid_uid}: keeping {highest_res_file.name} "
                f"({rows}x{cols}), excluding {len(files_with_dims) - 1} related files"
            )
        else:
            files_to_keep.append(files_with_dims[0][0])

    return files_to_keep


def select_dicom_files(path: Path) -> list[Path]:
    """Select WSI files only from the path, excluding auxiliary and redundant files.

    For multi-file DICOM pyramids (WSI images split across multiple DICOM instances),
    keeps only the highest resolution file. Excludes segmentations, annotations,
    thumbnails, labels, and other non-image DICOM files. OpenSlide will automatically
    find related pyramid files in the same directory when needed.

    See here for more info on the DICOM data model:
    https://dicom.nema.org/medical/dicom/current/output/chtml/part03/chapter_7.html

    Filtering Strategy:
    - Only processes VL Whole Slide Microscopy Image Storage
        (SOPClassUID 1.2.840.10008.5.1.4.1.1.77.1.6)
        Reference: https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_b.5.html
    - Excludes auxiliary images by ImageType Value 3 (keeps only VOLUME images)
        Reference: https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.12.4.html#sect_C.8.12.4.1.1
    - Groups files by PyramidUID (unique identifier for multi-resolution pyramids)
    - For pyramids with multiple files, selects only the highest resolution based
        on TotalPixelMatrixRows x TotalPixelMatrixColumns
    - Preserves standalone WSI files without PyramidUID

    Returns:
        List of DICOM file paths to process. All other DICOM files are excluded.

    Note:
        Files that cannot be read or are missing required attributes are logged and skipped.
    """
    pyramid_groups: dict[str, list[tuple[Path, int, int]]] = defaultdict(list)
    included_dicom_files: list[Path] = []

    # Scan all DICOM files and filter based on SOPClassUID and ImageType
    for dcm_file in path.glob("**/*.dcm"):
        try:
            ds = pydicom.dcmread(dcm_file, stop_before_pixels=True)

            # Exclude non-WSI image files by SOPClassUID
            # Only process VL Whole Slide Microscopy Image Storage (1.2.840.10008.5.1.4.1.1.77.1.6)
            if ds.SOPClassUID != "1.2.840.10008.5.1.4.1.1.77.1.6":
                logger.debug(f"Excluding {dcm_file.name} - not a WSI image (SOPClassUID: {ds.SOPClassUID})")
                continue

            # Exclude auxiliary images by ImageType Value 3
            # Per DICOM PS3.3 C.8.12.4.1.1: Value 3 should be VOLUME, THUMBNAIL, LABEL, or OVERVIEW.
            # We only want VOLUME images
            if hasattr(ds, "ImageType") and len(ds.ImageType) >= 3:  # noqa: PLR2004
                image_type_value_3 = ds.ImageType[2].upper()

                if image_type_value_3 != "VOLUME":
                    logger.debug(f"Excluding {dcm_file.name} - ImageType Value 3: {image_type_value_3}")
                    continue
            else:
                # No ImageType Value 3 - could be standalone WSI or non-standard file
                logger.debug(f"DICOM {dcm_file.name} has no ImageType Value 3 - treating as standalone")

            # Try to group by PyramidUID for pyramid resolution selection
            if hasattr(ds, "PyramidUID"):
                # PyramidUID is Type 1C (conditional) - required if part of a multi-file pyramid
                # TotalPixelMatrix attributes are Type 1 for WSI - should always be present
                pyramid_uid = ds.PyramidUID
                rows = int(ds.TotalPixelMatrixRows)
                cols = int(ds.TotalPixelMatrixColumns)

                pyramid_groups[pyramid_uid].append((dcm_file, rows, cols))
            else:
                # Treat as standalone file
                included_dicom_files.append(dcm_file)

        except Exception as e:
            logger.debug(f"Could not process DICOM file {dcm_file}: {e}")
            continue

    # For each pyramid with multiple files, select only the highest resolution
    pyramid_files_to_include = _find_highest_resolution_files(pyramid_groups)
    included_dicom_files.extend(pyramid_files_to_include)

    return included_dicom_files
