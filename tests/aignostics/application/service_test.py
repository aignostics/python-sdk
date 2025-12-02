"""Tests to verify the service functionality of the application module."""

from collections.abc import Callable
from pathlib import Path

import pydicom
import pytest

from aignostics.application import Service as ApplicationService


@pytest.fixture
def create_dicom() -> Callable[..., pydicom.Dataset]:
    """Fixture that returns a function to create minimal but valid DICOM datasets."""

    def _create_dicom(
        pyramid_uid: str | None,
        rows: int,
        cols: int,
        sop_class_uid: str = "1.2.840.10008.5.1.4.1.1.77.1.6",  # VL WSI by default
        image_type: list[str] | None = None,
    ) -> pydicom.Dataset:
        """Create a minimal but valid DICOM dataset for WSI.

        Args:
            pyramid_uid: The pyramid UID (None for standalone images)
            rows: Total image rows (TotalPixelMatrixRows) for the full WSI
            cols: Total image columns (TotalPixelMatrixColumns) for the full WSI
            sop_class_uid: SOP Class UID (defaults to VL WSI)
            image_type: Optional ImageType attribute

        Returns:
            A valid pydicom Dataset for whole slide imaging
        """
        ds = pydicom.Dataset()

        # File Meta Information
        ds.file_meta = pydicom.Dataset()
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = sop_class_uid
        ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()

        # Required DICOM attributes
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.SOPClassUID = sop_class_uid
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.Modality = "SM"

        # Tile dimensions (typically 256x256 for WSI)
        ds.Rows = 256
        ds.Columns = 256

        # CRITICAL: Total image dimensions for whole slide imaging
        # These represent the full image size and are what differentiate pyramid levels
        ds.TotalPixelMatrixRows = rows
        ds.TotalPixelMatrixColumns = cols

        # Add PyramidUID if provided (optional for standalone images)
        if pyramid_uid:
            ds.PyramidUID = pyramid_uid

        # Add ImageType if provided
        if image_type:
            ds.ImageType = image_type

        return ds

    return _create_dicom


@pytest.mark.unit
def test_filter_dicom_pyramid_single_file(
    tmp_path: Path,
    create_dicom: Callable[..., pydicom.Dataset],
) -> None:
    """Test that single DICOM files with PyramidUID are not filtered."""
    ds = create_dicom("1.2.3.4.5", 1024, 1024)
    dcm_file = tmp_path / "test.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)
    assert len(excluded) == 0


@pytest.mark.unit
def test_filter_dicom_pyramid_standalone_no_pyramid_uid(
    tmp_path: Path,
    create_dicom: Callable[..., pydicom.Dataset],
) -> None:
    """Test that standalone DICOM files without PyramidUID are not filtered."""
    ds = create_dicom(None, 1024, 1024)  # No PyramidUID
    dcm_file = tmp_path / "test.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)
    assert len(excluded) == 0


@pytest.mark.unit
def test_filter_dicom_pyramid_multi_file(tmp_path: Path, create_dicom: Callable[..., pydicom.Dataset]) -> None:
    """Test that for multi-file DICOM pyramid, only the highest resolution file is kept."""
    pyramid_uid = "1.2.3.4.5"

    # Create low resolution DICOM file (smallest pyramid level)
    ds_low = create_dicom(pyramid_uid, 512, 512)
    dcm_file_low = tmp_path / "test_low.dcm"
    ds_low.save_as(dcm_file_low, write_like_original=False)

    # Create medium resolution DICOM file
    ds_med = create_dicom(pyramid_uid, 1024, 1024)
    dcm_file_med = tmp_path / "test_med.dcm"
    ds_med.save_as(dcm_file_med, write_like_original=False)

    # Create high resolution DICOM file (base layer - highest resolution)
    ds_high = create_dicom(pyramid_uid, 2048, 2048)
    dcm_file_high = tmp_path / "test_high.dcm"
    ds_high.save_as(dcm_file_high, write_like_original=False)

    # Filter the pyramid
    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)

    # Should exclude 2 files (low and medium), keeping only the highest resolution
    assert len(excluded) == 2
    assert dcm_file_low in excluded
    assert dcm_file_med in excluded
    assert dcm_file_high not in excluded


@pytest.mark.unit
def test_filter_dicom_pyramid_multiple_pyramids(tmp_path: Path, create_dicom: Callable[..., pydicom.Dataset]) -> None:
    """Test that files from different pyramids are not filtered against each other."""
    # Pyramid 1 - two files (pyramid with 2 levels)
    ds1_low = create_dicom("1.2.3.4.5", 512, 512)
    dcm_file1_low = tmp_path / "pyramid1_low.dcm"
    ds1_low.save_as(dcm_file1_low, write_like_original=False)

    ds1_high = create_dicom("1.2.3.4.5", 1024, 1024)
    dcm_file1_high = tmp_path / "pyramid1_high.dcm"
    ds1_high.save_as(dcm_file1_high, write_like_original=False)

    # Pyramid 2 - single file (standalone, single level)
    ds2 = create_dicom("6.7.8.9.0", 512, 512)
    dcm_file2 = tmp_path / "pyramid2.dcm"
    ds2.save_as(dcm_file2, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)

    # Should exclude only the low-res file from pyramid 1
    assert len(excluded) == 1
    assert dcm_file1_low in excluded
    assert dcm_file1_high not in excluded
    assert dcm_file2 not in excluded


@pytest.mark.unit
def test_filter_dicom_pyramid_exclude_non_wsi(
    tmp_path: Path,
    create_dicom: Callable[..., pydicom.Dataset],
) -> None:
    """Test that non-WSI DICOM files (e.g., segmentations) are excluded."""
    # Create a segmentation storage DICOM
    ds_seg = create_dicom(
        "1.2.3.4.5",
        1024,
        1024,
        sop_class_uid="1.2.840.10008.5.1.4.1.1.66.4",  # Segmentation Storage
    )
    dcm_file_seg = tmp_path / "segmentation.dcm"
    ds_seg.save_as(dcm_file_seg, write_like_original=False)

    # Create a valid WSI
    ds_wsi = create_dicom("1.2.3.4.5", 1024, 1024)
    dcm_file_wsi = tmp_path / "wsi.dcm"
    ds_wsi.save_as(dcm_file_wsi, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)

    # Should exclude only the segmentation file
    assert len(excluded) == 1
    assert dcm_file_seg in excluded
    assert dcm_file_wsi not in excluded


@pytest.mark.unit
def test_filter_dicom_pyramid_exclude_thumbnails(
    tmp_path: Path,
    create_dicom: Callable[..., pydicom.Dataset],
) -> None:
    """Test that thumbnail images are excluded."""
    # Create a thumbnail
    ds_thumb = create_dicom(
        "1.2.3.4.5",
        256,
        256,
        image_type=["DERIVED", "PRIMARY", "THUMBNAIL", "RESAMPLED"],
    )
    dcm_file_thumb = tmp_path / "thumbnail.dcm"
    ds_thumb.save_as(dcm_file_thumb, write_like_original=False)

    # Create a regular WSI image
    ds_wsi = create_dicom(
        "1.2.3.4.5",
        1024,
        1024,
        image_type=["DERIVED", "PRIMARY", "VOLUME", "NONE"],
    )
    dcm_file_wsi = tmp_path / "wsi.dcm"
    ds_wsi.save_as(dcm_file_wsi, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)

    # Should exclude only the thumbnail
    assert len(excluded) == 1
    assert dcm_file_thumb in excluded
    assert dcm_file_wsi not in excluded


@pytest.mark.unit
def test_filter_dicom_pyramid_missing_attributes(
    tmp_path: Path,
) -> None:
    """Test that DICOM files without required WSI attributes are skipped gracefully."""
    # Create a DICOM without TotalPixelMatrix attributes
    ds = pydicom.Dataset()
    ds.file_meta = pydicom.Dataset()
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.6"
    ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()

    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.6"
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.Modality = "SM"
    ds.Rows = 512
    ds.Columns = 512
    ds.PyramidUID = "1.2.3.4.5"
    # Note: No TotalPixelMatrixRows/Columns

    dcm_file = tmp_path / "incomplete_wsi.dcm"
    ds.save_as(dcm_file, write_like_original=False)

    # Should not crash, and should not exclude anything (file is skipped gracefully)
    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)
    assert len(excluded) == 0


@pytest.mark.unit
def test_filter_dicom_pyramid_mixed_scenario(
    tmp_path: Path,
    create_dicom: Callable[..., pydicom.Dataset],
) -> None:
    """Test complex scenario with multiple pyramids, thumbnails, and segmentations."""
    # Pyramid 1: 3 levels (keep highest)
    ds1_low = create_dicom("pyramid1", 512, 512)
    dcm_file1_low = tmp_path / "p1_low.dcm"
    ds1_low.save_as(dcm_file1_low, write_like_original=False)

    ds1_high = create_dicom("pyramid1", 2048, 2048)
    dcm_file1_high = tmp_path / "p1_high.dcm"
    ds1_high.save_as(dcm_file1_high, write_like_original=False)

    # Thumbnail for pyramid 1 (exclude)
    ds1_thumb = create_dicom("pyramid1", 256, 256, image_type=["DERIVED", "PRIMARY", "THUMBNAIL"])
    dcm_file1_thumb = tmp_path / "p1_thumb.dcm"
    ds1_thumb.save_as(dcm_file1_thumb, write_like_original=False)

    # Segmentation file (exclude)
    ds_seg = create_dicom("pyramid1", 2048, 2048, sop_class_uid="1.2.840.10008.5.1.4.1.1.66.4")
    dcm_file_seg = tmp_path / "seg.dcm"
    ds_seg.save_as(dcm_file_seg, write_like_original=False)

    # Standalone WSI without PyramidUID (keep)
    ds_standalone = create_dicom(None, 1024, 1024)
    dcm_file_standalone = tmp_path / "standalone.dcm"
    ds_standalone.save_as(dcm_file_standalone, write_like_original=False)

    excluded = ApplicationService._filter_dicom_pyramid_files(tmp_path)

    # Should exclude: low-res from pyramid1, thumbnail, segmentation
    assert len(excluded) == 3
    assert dcm_file1_low in excluded
    assert dcm_file1_thumb in excluded
    assert dcm_file_seg in excluded
    # Should keep: high-res from pyramid1, standalone
    assert dcm_file1_high not in excluded
    assert dcm_file_standalone not in excluded
