---
itemId: SWR-SYSTEM-CLI-HEALTH-1
itemTitle: CLI System Health Check
itemHasParent: SHR-SYSTEM-1
itemType: Requirement
Requirement type: REGULATORY
Module: System
Layer: CLI
---

As a user, I want to check the health of the system via the CLI so that I can ensure the system is operational.

I can run the command `system health` to get the current status of the system. The expected output should indicate that the system is "UP" and operational.

The command allows for output in different formats, that is JSON or YAML. The default output format is JSON.
