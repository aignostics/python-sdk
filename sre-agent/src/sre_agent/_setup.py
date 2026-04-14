"""One-time setup: create agent, environment, skill, and vault on Anthropic.

Usage:
    SRE_GITHUB_PAT=ghp_... uv run python -m sre_agent._setup

Prints the resource IDs to store as GitHub Actions secrets.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import anthropic

SYSTEM_PROMPT = """\
You are an SRE incident response agent for the Aignostics Python SDK
(github.com/aignostics/python-sdk).

You have been triggered by a BetterStack incident alert. The alert
includes the incident name, cause, and -- critically -- the GitHub
Actions run URL from the failed workflow.

Your job:

1. Read the incident details: name, cause, and the failed run URL.
2. Use the GitHub MCP to read the failed workflow run's logs. This is
   your primary source of diagnostic information.
3. Investigate the root cause:
   - Read the workflow run logs to identify the specific failure.
   - Check recent commits on main (git log in the mounted repo).
   - Read the relevant GitHub Actions workflow YAML files.
   - Use web_search to look up error messages, CVE details, or docs.
4. Determine if the issue is fixable with a code change.
5. If fixable: use the GitHub MCP to create a branch, commit the fix,
   and open a draft PR with your analysis in the body.
6. If not fixable or uncertain: use the GitHub MCP to create an issue
   with your triage findings and recommended next steps.

Constraints:
- Always create DRAFT PRs, never regular PRs. Humans must review and merge.
- Always cite evidence for your root cause analysis.
- For dependency CVEs: bump the minimum safe version, run the audit check.
- For test failures: check if the test is flaky (search for prior failures)
  before proposing a code fix.
- Never modify credentials, secrets, or authentication code.
- Add the label "sre-agent" to any PR or issue you create.
- Add the label "skip:test:long_running" to any PR you create.

The repo uses: uv (package manager), pytest (testing), ruff (linting),
mypy + pyright (type checking). CI runs on GitHub Actions.
"""

SKILL_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "sre-runbook"


def main() -> None:
    github_pat = os.environ.get("SRE_GITHUB_PAT", "")
    if not github_pat:
        print("Error: SRE_GITHUB_PAT environment variable is required.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic()

    # 1. Upload runbook skill
    skill_md = (SKILL_DIR / "SKILL.md").read_bytes()
    skill = client.beta.skills.create(
        display_title="sre-runbook",
        files=[("sre-runbook/SKILL.md", skill_md, "text/markdown")],
    )
    print(f"Skill created: {skill.id} (version {skill.latest_version})")

    # 2. Create environment
    environment = client.beta.environments.create(
        name="sre-incident-response",
        config={"type": "cloud", "networking": {"type": "limited"}},
    )
    print(f"Environment created: {environment.id}")

    # 3. Create vault with GitHub PAT
    vault = client.beta.vaults.create(name="sre-github")
    client.beta.vaults.credentials.create(
        vault_id=vault.id,
        name="github",
        token=github_pat,
    )
    print(f"Vault created: {vault.id}")

    # 4. Create agent
    agent = client.beta.agents.create(
        name="Aignostics SRE Incident Responder",
        model="claude-sonnet-4-6",
        system=SYSTEM_PROMPT,
        mcp_servers=[
            {
                "type": "url",
                "name": "github",
                "url": "https://api.githubcopilot.com/mcp/",
            },
        ],
        tools=[
            {"type": "agent_toolset_20260401"},
            {"type": "mcp_toolset", "mcp_server_name": "github"},
        ],
        skills=[
            {"type": "custom", "skill_id": skill.id, "version": skill.latest_version},
        ],
    )
    print(f"Agent created: {agent.id} (version {agent.version})")

    # Print secrets to configure in GitHub Actions
    print("\n--- Store these as GitHub Actions secrets ---")
    print(f"SRE_AGENT_ID={agent.id}")
    print(f"SRE_ENVIRONMENT_ID={environment.id}")
    print(f"SRE_VAULT_ID={vault.id}")


if __name__ == "__main__":
    main()
