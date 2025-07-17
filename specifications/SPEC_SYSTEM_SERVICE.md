---
itemId: SPEC-SYSTEM-SERVICE
itemType: Software Item Spec
itemFulfills: RQ-SYSTEM-CLI-1, RQ-SYSTEM-GUI-1
Module: System
Layer: Service
Regulatory: RUO
---

The system module provides a service to check the health of the system which is accessible via the CLI and the GUI. The service is designed to return the current operational status of the system.

The service auto-masks secrets in the output, which can as well be switched off. For that a set of patterns is used to identify keys containing secrets.