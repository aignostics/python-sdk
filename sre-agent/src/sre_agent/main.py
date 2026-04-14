"""SRE incident response orchestrator.

Fetches a BetterStack incident, filters for Python SDK relevance,
creates a Managed Agent session, and streams it to completion.

Usage:
    # From GitHub Actions (env vars set by workflow):
    uv run python -m sre_agent.main

    # Locally with simulated incident:
    SIMULATE=true SRE_AGENT_ID=... SRE_ENVIRONMENT_ID=... SRE_VAULT_ID=... \
        ANTHROPIC_API_KEY=... uv run python -m sre_agent.main
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

import anthropic

from sre_agent._config import SREAgentSettings

# Sample incident for testing without BetterStack access.
# Mirrors the real API structure from uptime.betterstack.com/api/v2/incidents.
SAMPLE_INCIDENT: dict = {
    "id": "000000000",
    "type": "incident",
    "attributes": {
        "name": "Python SDK / Scheduled Audit on GitHub",
        "cause": "Reported failure with code 2",
        "status": "Started",
        "started_at": "2026-04-10T20:10:58.539Z",
        "response_content": json.dumps({
            "github": {
                "workflow": "+ Scheduled Audit (Hourly)",
                "run_url": "https://github.com/aignostics/python-sdk/actions/runs/24261996590",
                "run_id": "24261996590",
                "sha": "1b1b4b6b4dfdc88a65b745f4ebd6d63995b35b20",
                "actor": "github-actions",
                "repository": "aignostics/python-sdk",
                "ref": "refs/heads/main",
                "event_name": "schedule",
            },
            "job": {"status": "success"},
        }),
        "metadata": {"component": "python-sdk"},
    },
}


def is_python_sdk_incident(incident: dict) -> bool:
    """Check if incident is for the Python SDK."""
    attrs = incident.get("attributes", {})
    if attrs.get("metadata", {}).get("component") == "python-sdk":
        return True
    return bool(re.search(r"python[\s-]sdk", attrs.get("name", ""), re.IGNORECASE))


def fetch_incident(incident_id: str, token: str) -> dict:
    """Fetch full incident details from BetterStack API."""
    req = urllib.request.Request(
        f"https://uptime.betterstack.com/api/v2/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["data"]  # type: ignore[no-any-return]


def build_prompt(incident: dict) -> str:
    """Build the agent's first message from incident data."""
    attrs = incident["attributes"]
    parts = [
        f"# BetterStack Incident: {attrs['name']}",
        f"**Status**: {attrs['status']}",
        f"**Cause**: {attrs['cause']}",
        f"**Started**: {attrs['started_at']}",
    ]

    if attrs.get("response_content"):
        ctx = json.loads(attrs["response_content"])
        gh = ctx.get("github", {})
        if gh.get("run_url"):
            parts.extend([
                "\n## Failed GitHub Actions Run",
                f"**Run URL**: {gh['run_url']}",
                f"**Workflow**: {gh.get('workflow', 'unknown')}",
                f"**Commit**: {gh.get('sha', 'unknown')}",
                f"**Job**: {gh.get('job', 'unknown')}",
            ])

    parts.append("\nPlease triage this incident following the SRE runbook skill.")
    return "\n".join(parts)


def main() -> None:
    simulate = os.environ.get("SIMULATE", "false").lower() == "true"
    incident_id = os.environ.get("INCIDENT_ID", "")

    if simulate:
        print("Using simulated incident for testing.")
        incident = SAMPLE_INCIDENT
    elif incident_id:
        settings = SREAgentSettings()  # type: ignore[call-arg]
        incident = fetch_incident(incident_id, settings.betterstack_api_token.get_secret_value())
    else:
        print("No INCIDENT_ID provided and SIMULATE is not true. Exiting.")
        sys.exit(0)

    if not is_python_sdk_incident(incident):
        print(f"Skipping non-Python-SDK incident: {incident.get('attributes', {}).get('name', 'unknown')}")
        sys.exit(0)

    settings = SREAgentSettings()  # type: ignore[call-arg]
    client = anthropic.Anthropic()

    prompt = build_prompt(incident)
    print(f"Creating agent session for: {incident['attributes']['name']}")
    print(f"Prompt:\n{prompt}\n")

    # Create session with GitHub MCP auth via vault
    session = client.beta.sessions.create(
        agent=settings.agent_id,
        environment_id=settings.environment_id,
        vault_ids=[settings.vault_id],
        resources=[
            {
                "type": "github_repository",
                "url": f"https://github.com/{settings.github_repo}",
                "mount_path": "/workspace/python-sdk",
                "checkout": {"type": "branch", "name": "main"},
            },
        ],
    )
    print(f"Session created: {session.id}")

    # Send incident as first message
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [{"type": "text", "text": prompt}],
            },
        ],
    )

    # Stream until completion
    with client.beta.sessions.stream(session_id=session.id) as stream:
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text)
            elif event.type in ("session.status_idle", "session.status_terminated"):
                break

    print(f"\nSession {session.id} complete.")
    client.beta.sessions.archive(session_id=session.id)


if __name__ == "__main__":
    main()
