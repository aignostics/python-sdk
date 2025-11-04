---
itemId: SWR-SYSTEM-CLI-HEALTH-1
itemHasParent: SHR-SYSTEM-1
itemType: Requirement
Requirement type: REGULATORY # Software requirement (system)
Module: System
Layer: CLI
---

As a user, I want to check the health of the system via the CLI so that I can ensure the system is operational.

I can run the command `system health` to get the current status of the system. The expected output should indicate that the system is "UP" and operational.

The command allows for output in different formats, that is JSON or YAML. The default output format is JSON.
