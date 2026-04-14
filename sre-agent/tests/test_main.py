"""Tests for the SRE agent orchestrator."""

from __future__ import annotations

import json

from sre_agent.main import SAMPLE_INCIDENT, build_prompt, is_python_sdk_incident


class TestIsPythonSdkIncident:
    """Tests for the incident filter."""

    def test_matches_metadata_component(self) -> None:
        incident = {"attributes": {"name": "Something", "metadata": {"component": "python-sdk"}}}
        assert is_python_sdk_incident(incident) is True

    def test_matches_name_with_slash(self) -> None:
        incident = {"attributes": {"name": "Python SDK / Scheduled Audit on GitHub", "metadata": {}}}
        assert is_python_sdk_incident(incident) is True

    def test_matches_name_with_hyphen(self) -> None:
        incident = {"attributes": {"name": "python-sdk staging tests", "metadata": {}}}
        assert is_python_sdk_incident(incident) is True

    def test_matches_name_case_insensitive(self) -> None:
        incident = {"attributes": {"name": "New incident for PYTHON SDK", "metadata": {}}}
        assert is_python_sdk_incident(incident) is True

    def test_rejects_unrelated_incident(self) -> None:
        incident = {"attributes": {"name": "Platform API / Health Check", "metadata": {}}}
        assert is_python_sdk_incident(incident) is False

    def test_rejects_empty_incident(self) -> None:
        incident = {"attributes": {"name": "", "metadata": {}}}
        assert is_python_sdk_incident(incident) is False

    def test_rejects_missing_attributes(self) -> None:
        incident: dict = {}
        assert is_python_sdk_incident(incident) is False

    def test_matches_url_style_name(self) -> None:
        name = "Aignostics Platform (staging) / Applications / Scheduled Testing (Hourly) on https://github.com/aignostics/python-sdk"
        incident = {"attributes": {"name": name, "metadata": {}}}
        assert is_python_sdk_incident(incident) is True


class TestBuildPrompt:
    """Tests for prompt construction from incident data."""

    def test_basic_prompt_fields(self) -> None:
        prompt = build_prompt(SAMPLE_INCIDENT)
        assert "Python SDK / Scheduled Audit on GitHub" in prompt
        assert "Reported failure with code 2" in prompt
        assert "Started" in prompt

    def test_includes_github_run_url(self) -> None:
        prompt = build_prompt(SAMPLE_INCIDENT)
        assert "https://github.com/aignostics/python-sdk/actions/runs/24261996590" in prompt

    def test_includes_workflow_name(self) -> None:
        prompt = build_prompt(SAMPLE_INCIDENT)
        assert "Scheduled Audit (Hourly)" in prompt

    def test_includes_commit_sha(self) -> None:
        prompt = build_prompt(SAMPLE_INCIDENT)
        assert "1b1b4b6b" in prompt

    def test_handles_missing_response_content(self) -> None:
        incident = {
            "attributes": {
                "name": "Test incident",
                "cause": "Unknown",
                "status": "Started",
                "started_at": "2026-01-01T00:00:00Z",
                "response_content": None,
            },
        }
        prompt = build_prompt(incident)
        assert "Test incident" in prompt
        assert "Failed GitHub Actions Run" not in prompt

    def test_handles_response_content_without_github(self) -> None:
        incident = {
            "attributes": {
                "name": "Test incident",
                "cause": "Unknown",
                "status": "Started",
                "started_at": "2026-01-01T00:00:00Z",
                "response_content": json.dumps({"some": "other data"}),
            },
        }
        prompt = build_prompt(incident)
        assert "Test incident" in prompt
        assert "Failed GitHub Actions Run" not in prompt

    def test_ends_with_triage_instruction(self) -> None:
        prompt = build_prompt(SAMPLE_INCIDENT)
        assert prompt.endswith("Please triage this incident following the SRE runbook skill.")
