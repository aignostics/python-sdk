---
itemId: SWR-APPLICATION-4-3
itemTitle: Read a Shared Application Run via Share Token
itemHasParent: SHR-APPLICATION-4
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall enable an authenticated user who holds a share token secret to read an application run shared with them through the CLI, without requiring the run to have been granted to their account directly. The user shall be able to retrieve run status and details, dump run and item custom metadata, and download run results by supplying the share token secret; OAuth authentication remains required and the share token elevates the authenticated user's access to the shared run. When access is denied because the token is invalid, expired, or revoked, the system shall report a clear access-denied message and exit with code 1; when the run does not exist, the system shall exit with code 2. When no share token is supplied, the commands shall behave exactly as for a normal authenticated read.
