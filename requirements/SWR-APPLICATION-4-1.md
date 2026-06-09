---
itemId: SWR-APPLICATION-4-1
itemTitle: Grant and Revoke Organization Access to Application Run
itemHasParent: SHR-APPLICATION-4
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall enable data scientists to grant read access to a specific application run to another authenticated platform user or to all users belonging to a specified organization. The system shall list all active access grants for a given run, including for each grant the subject type, subject identifier, relation, and creation metadata. The system shall revoke any individual grant on demand, removing the associated access immediately. All grant operations shall operate on the Aignostics Platform access control API; each mutating operation shall invalidate the local operation cache.
