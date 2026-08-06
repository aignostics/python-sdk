"""Unit tests for the pure metadata helpers of the application describe/submit page.

These cover the single-source-of-truth specimen indication lists and the pure helpers
derived from them (validation, dropdown/column definitions, cell-coloring expressions),
without building the NiceGUI page itself.
"""

import pytest
from aignostics.application._gui._page_application_describe import (
    DISEASE_TYPES,
    TISSUE_TYPES,
    _js_set_membership,
    _metadata_row_is_valid,
    _specimen_metadata_column_defs,
)


@pytest.mark.unit
def test_supported_indication_lists_match_platform_api() -> None:
    """The GUI lists mirror the platform API's whole_slide_image metadata_schema.

    Exact tuple equality pins the supported values (including the prostate/pancreatic/stomach
    additions from Atlas H&E-TME v1.2.0), their dropdown display order, and the absence of
    duplicates in one assertion.
    """
    assert TISSUE_TYPES == (
        "ADRENAL_GLAND",
        "BLADDER",
        "BONE",
        "BRAIN",
        "BREAST",
        "COLON",
        "LIVER",
        "LUNG",
        "LYMPH_NODE",
        "OTHER",
        "PANCREAS",
        "PROSTATE",
        "SPLEEN",
        "STOMACH",
    )
    assert DISEASE_TYPES == (
        "BLADDER_CANCER",
        "BREAST_CANCER",
        "COLORECTAL_CANCER",
        "LIVER_CANCER",
        "LUNG_CANCER",
        "PANCREATIC_CANCER",
        "PROSTATE_CANCER",
        "STOMACH_CANCER",
    )


@pytest.mark.unit
def test_js_set_membership_positive() -> None:
    """Without negation the expression is a plain Set membership test on x."""
    assert _js_set_membership(("LUNG", "OTHER")) == "new Set(['LUNG', 'OTHER']).has(x)"


@pytest.mark.unit
def test_js_set_membership_negated() -> None:
    """With negation the expression is prefixed with the JS not operator."""
    assert _js_set_membership(("LUNG", "OTHER"), negate=True) == "!new Set(['LUNG', 'OTHER']).has(x)"


@pytest.mark.unit
def test_js_set_membership_covers_all_current_values() -> None:
    """Every supported value is embedded in the generated expressions."""
    tissue_expr = _js_set_membership(TISSUE_TYPES)
    disease_expr = _js_set_membership(DISEASE_TYPES)
    for tissue in TISSUE_TYPES:
        assert f"'{tissue}'" in tissue_expr
    for disease in DISEASE_TYPES:
        assert f"'{disease}'" in disease_expr


@pytest.mark.unit
def test_specimen_column_defs_structure() -> None:
    """The helper returns the Tissue and Disease columns wired to the supported lists."""
    columns = _specimen_metadata_column_defs()
    assert [c["field"] for c in columns] == ["tissue", "disease"]

    tissue_col, disease_col = columns
    assert tissue_col["cellEditorParams"]["values"] == list(TISSUE_TYPES)
    assert disease_col["cellEditorParams"]["values"] == list(DISEASE_TYPES)

    for col, values in ((tissue_col, TISSUE_TYPES), (disease_col, DISEASE_TYPES)):
        assert col["editable"] is True
        assert col["cellEditor"] == "agSelectCellEditor"
        assert col["cellClassRules"]["bg-green-300"] == _js_set_membership(values)
        assert col["cellClassRules"]["bg-red-300"] == _js_set_membership(values, negate=True)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("tissue", "disease"),
    [
        ("LUNG", "LUNG_CANCER"),
        ("PROSTATE", "PROSTATE_CANCER"),
        ("PANCREAS", "PANCREATIC_CANCER"),
        ("STOMACH", "STOMACH_CANCER"),
        ("LYMPH_NODE", "COLORECTAL_CANCER"),
    ],
)
def test_metadata_row_is_valid_accepts_supported_combinations(tissue: str, disease: str) -> None:
    """Rows with supported tissue and disease pass validation."""
    assert _metadata_row_is_valid({"tissue": tissue, "disease": disease}) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "row",
    [
        {"tissue": "LUNG", "disease": "UNSUPPORTED_CANCER"},
        {"tissue": "UNSUPPORTED_TISSUE", "disease": "LUNG_CANCER"},
        {"tissue": "OTHER", "disease": None},
        {"tissue": None, "disease": "LUNG_CANCER"},
        {},
    ],
)
def test_metadata_row_is_valid_rejects_unsupported_or_missing(row: dict) -> None:
    """Rows with an unsupported or missing tissue/disease fail validation."""
    assert _metadata_row_is_valid(row) is False
