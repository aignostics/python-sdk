---
itemId: SWR-APPLICATION-4-2
itemTitle: Create and Revoke Share Token Access to Application Run
itemHasParent: SHR-APPLICATION-4
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall enable run submitters and organization admins to create revocable share tokens with an optional expiry date
and to grant read access to a specific application run via such a token, allowing secure sharing with other platform 
users. The system shall list all active share tokens for the authenticated user. The system shall list all grants 
associated with a given share token. The system shall revoke a share token's grant on a specific run on demand. The 
token secret shall be returned only at creation time and shall not be retrievable subsequently.
