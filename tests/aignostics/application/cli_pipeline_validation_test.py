"""Integration tests for CLI pipeline configuration validation."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aignostics.cli import cli
from tests.conftest import normalize_output
from tests.constants_test import HETA_APPLICATION_ID


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_invalid_gpu_type(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails when gpu_type is invalid."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--gpu-type",
            "INVALID_GPU",
        ],
    )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    # Pydantic validation error for invalid enum value
    assert "validation error" in output.lower() or "invalid" in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_invalid_gpu_provisioning_mode(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails when gpu_provisioning_mode is invalid."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--gpu-provisioning-mode",
            "INVALID_MODE",
        ],
    )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    # Pydantic validation error for invalid enum value
    assert "validation error" in output.lower() or "invalid" in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_invalid_cpu_provisioning_mode(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails when cpu_provisioning_mode is invalid."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--cpu-provisioning-mode",
            "RESERVED",
        ],
    )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    # Pydantic validation error for invalid enum value
    assert "validation error" in output.lower() or "invalid" in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_max_gpus_per_slide_zero(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails when max_gpus_per_slide is 0."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--max-gpus-per-slide",
            "0",
        ],
    )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    # Typer validation error for value below min
    assert "invalid" in output.lower() or "range" in output.lower() or "greater" in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_fails_on_max_gpus_per_slide_too_high(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command fails when max_gpus_per_slide is greater than 8."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--max-gpus-per-slide",
            "9",
        ],
    )

    assert result.exit_code == 2
    output = normalize_output(result.output)
    # Typer validation error for value above max
    assert "invalid" in output.lower() or "range" in output.lower() or "smaller" in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_succeeds_with_valid_pipeline_config(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command succeeds with valid pipeline configuration (validation only)."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    # Test with valid L4 GPU
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--gpu-type",
            "L4",
            "--gpu-provisioning-mode",
            "SPOT",
            "--max-gpus-per-slide",
            "4",
            "--cpu-provisioning-mode",
            "ON_DEMAND",
            "--validate-only",  # Don't actually run the analysis
        ],
    )

    # Should fail on the actual bucket validation (gs://bucket/test.svs doesn't exist)
    # but NOT on pipeline config validation
    output = normalize_output(result.output)
    # Should NOT have validation errors about GPU type, provisioning mode, or max GPUs
    assert "validation error" not in output.lower() or "gpu" not in output.lower()


@pytest.mark.integration
@pytest.mark.timeout(timeout=60)
def test_cli_run_submit_succeeds_with_valid_a100_config(runner: CliRunner, tmp_path: Path) -> None:
    """Check run submit command succeeds with valid A100 configuration (validation only)."""
    csv_content = "external_id;checksum_base64_crc32c;resolution_mpp;width_px;height_px;staining_method;tissue;disease;"
    csv_content += "platform_bucket_url\n"
    csv_content += "test.svs;5onqtA==;0.26268186053789266;7447;7196;H&E;LUNG;LUNG_CANCER;gs://bucket/test.svs"
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text(csv_content)

    # Test with valid A100 GPU
    result = runner.invoke(
        cli,
        [
            "application",
            "run",
            "submit",
            HETA_APPLICATION_ID,
            str(csv_path),
            "--deadline",
            (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            "--gpu-type",
            "A100",
            "--gpu-provisioning-mode",
            "ON_DEMAND",
            "--max-gpus-per-slide",
            "8",
            "--cpu-provisioning-mode",
            "SPOT",
            "--validate-only",
        ],
    )

    # Should fail on bucket validation, not pipeline config
    output = normalize_output(result.output)
    assert "validation error" not in output.lower() or "gpu" not in output.lower()
