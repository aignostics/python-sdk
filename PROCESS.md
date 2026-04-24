# Engineering Process Guide

This document describes how the tools and processes used in this repository — GitHub, Jira, Ketryx, and the Confluence-based QMS — relate to each other and how to follow them correctly as an engineer or AI assistant.

## Tool Roles

| Tool | Role |
|------|------|
| **GitHub** | Source code, pull requests, CI/CD, code review |
| **Jira** | Ticket tracking for anomalies, change requests, tasks |
| **Ketryx** | Regulated release management — links Jira tickets to releases, collects approvals, enforces traceability |
| **Confluence (QMS)** | SOPs and work instructions that define the mandatory processes |

Ketryx sits on top of Jira: it reads Jira tickets of specific types (Anomaly, Change Request) and enforces that they are approved and linked before a release can be closed. A Ketryx release cannot be approved unless all linked items in Jira are in `Closed` status with the required approvals.

---

## Process 1: Fixing a Bug (Anomaly → PR)

Governed by [PR-SOP-01](https://aignx.atlassian.net/wiki/spaces/QMS/pages/1992786094) and [CC-WI-01](https://aignx.atlassian.net/wiki/spaces/QMSYSTEM/pages/2847604792).

### When to open an Anomaly ticket

Open a Jira Anomaly ticket (type `Anomaly`) on the `PYSDK` board when:

- A bug is found in **Staging or Production** deployment environments
- A known issue will be shipped to Production in an upcoming release

Issues found only during local development or in feature branches do **not** require an Anomaly ticket.

### Step-by-step

```
1. Open Anomaly ticket in Jira (PYSDK board, type: Anomaly)
   - Fill: Description, Deployment Environment, Severity, Introduced in Version
   - Status: Entry → In Progress

2. Investigate root cause
   - Determine Root Cause Category:
     a. Implementation Error → fix code, no Change Request needed
     b. Specification Defect or Requirement Defect → open a Change Request ticket (CC-WI-01)
     c. Duplicate → link to original, resolve
     d. No Change Required → document rationale, resolve

3. Create a GitHub PR
   - Title: follow conventional commits (fix: ...)
   - PR body: include link to the Jira Anomaly ticket
     Example: "Resolves PYSDK-78: https://aignx.atlassian.net/browse/PYSDK-78"
   - Add label: skip:test:long_running

4. Link back from Jira to GitHub
   - Add the PR URL to the "Resolved by" field in the Anomaly ticket
   - This creates bidirectional traceability:
       GitHub PR → Jira Anomaly (in PR description)
       Jira Anomaly → GitHub PR (in "Resolved by" field)

5. After PR is merged
   - Set "Obsolete in Version" to the pending release version
   - Transition ticket to: Resolved

6. Closure (Assignee + Tech Lead approve; QM for IVD products)
   - Ticket transitions automatically to: Closed

7. Ketryx picks up the closed Anomaly ticket for release approval
```

### Bidirectional linking — required fields

| Direction | Where | What to put |
|-----------|-------|-------------|
| PR → Jira | GitHub PR description | `Resolves PYSDK-XX` + full Jira URL |
| Jira → PR | "Resolved by" field | GitHub PR URL |

---

## Process 2: Adding a Feature or Making a Planned Change (Change Request → PR)

Governed by [CC-WI-01](https://aignx.atlassian.net/wiki/spaces/QMSYSTEM/pages/2847604792).

### When to open a Change Request

Open a Jira Change Request ticket (type `Ketryx Change Request`) when:

- Implementing a new feature
- Changing existing behaviour, requirements, or specifications
- Updating a Software Item Specification (SIS) or Software Requirement (SWR)
- Resolving an anomaly whose root cause requires a specification change

### Step-by-step

```
1. Open Change Request ticket (PYSDK board, type: Ketryx Change Request)
   - Fill: Description, Impact of Change, Affected Items, Introduced Items,
           Introduced in Version, Required Testing, Long-Lived Documents Affected
   - Status: Entry → In Progress

2. Evaluate risk impact
   - Link new or affected risk items
   - If a new supplier (library/service) is introduced: initiate supplier evaluation
   - Status: → Resolved

3. CR is reviewed and approved by PM + Tech Lead + QM
   - Status: → Closed (automatic after all approvals)

4. Create GitHub PR
   - PR description: link to the CR ticket
     Example: "Implements PYSDK-CR-XX: https://aignx.atlassian.net/browse/PYSDK-XX"
   - Add label: skip:test:long_running

5. Link PR back in Jira
   - Add PR URL to "Resolved by" or as a comment on the CR ticket

6. After merge: verify implementation as specified in the CR
   - Ketryx includes the CR in the release report
   - Release cannot be approved until all linked CRs and affected items are Closed
```

---

## Process 3: Releases (Ketryx)

The release process is documented in the root [CLAUDE.md](CLAUDE.md) (Version Bumping and Releases section). From a compliance perspective:

```
Phase 1: make prepare-release x.y.z
  → Creates release/vX.Y.Z branch, bumps version

Phase 2: Point Ketryx release to release/vX.Y.Z
  → All linked Anomaly and Change Request tickets must be Closed
  → Collect PM + Tech Lead + QM approvals in Ketryx

Phase 3: make publish-release
  → Tag created, PyPI publish triggered
  → Ketryx check must pass before publish

Phase 4: make merge-release
  → Merges release branch back to main
```

Ketryx enforces that every item linked to the release (Anomaly, CR, Test Report) has been approved. A release cannot be signed off in Ketryx if any linked ticket is still open.

---

## Quick Reference: Which ticket type for what?

| Situation | Ticket Type | Board |
|-----------|-------------|-------|
| Bug in Staging/Production | Anomaly | PYSDK |
| New feature or planned change | Ketryx Change Request | PYSDK |
| Bug whose fix changes a spec/requirement | Anomaly + Change Request | PYSDK |
| Documentation-only change | No ticket required | — |
| Dependency bump (no behaviour change) | No ticket required | — |
| Security finding with code impact | Anomaly | PYSDK |

---

## Claude Code Workflow

When I (Claude Code) create a PR that fixes a bug in Staging or Production, I will:

1. Check if a Jira Anomaly ticket already exists for the issue
2. If not, create one using the Atlassian MCP tools
3. Include the Jira link in the PR description
4. After PR creation, update the Anomaly ticket's "Resolved by" field with the PR URL
5. Set "Obsolete in Version" to the current release version

When I create a PR that implements a new feature, I will:

1. Check if a Change Request ticket already exists
2. Include the CR link in the PR description
3. Remind you to get CR approval before merging if the CR is not yet Closed

> **Note**: Anomaly tickets are only required for bugs observed in Staging or Production.
> Changes made purely during development (before any deployment) do not need an Anomaly ticket per PR-SOP-01.
