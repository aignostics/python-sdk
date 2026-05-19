from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime


def send_betterstack_heartbeat(url: str, exit_code: str, label: str) -> None:
    if not url:
        print(f"INFO: No BetterStack {label} heartbeat URL configured, skipped.")
        return

    if urllib.parse.urlparse(url).scheme not in {"http", "https"}:
        print(f"WARNING: Refusing non-HTTP BetterStack URL for {label}, skipped.", file=sys.stderr)
        return

    payload = {
        "github": {
            "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "run_url": (
                f"{os.environ.get('GITHUB_SERVER_URL', '')}"
                f"/{os.environ.get('GITHUB_REPOSITORY', '')}"
                f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
            ),
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "job": os.environ.get("GITHUB_JOB", ""),
            "sha": os.environ.get("GITHUB_SHA", ""),
            "actor": os.environ.get("GITHUB_ACTOR", ""),
            "repository": os.environ.get("GITHUB_REPOSITORY", ""),
            "ref": os.environ.get("GITHUB_REF", ""),
            "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
        },
        "job": {"status": os.environ.get("JOB_STATUS", "")},
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(  # noqa: S310
        f"{url}/{exit_code}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)  # noqa: S310
        print(f"INFO: Sent {label} heartbeat to BetterStack (exit={exit_code})")
    except urllib.error.URLError as exc:
        print(f"WARNING: Failed to send {label} heartbeat to BetterStack: {exc}", file=sys.stderr)


if __name__ == "__main__":
    send_betterstack_heartbeat(
        url=os.environ.get("BETTERSTACK_HEARTBEAT_URL", ""),
        exit_code=os.environ.get("BETTERSTACK_EXIT_CODE", "1"),
        label=os.environ.get("BETTERSTACK_LABEL", "unknown"),
    )
