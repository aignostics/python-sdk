---
itemId: SWR-APPLICATION-4-2
itemTitle: Create and Revoke Share Token Access to Application Run
itemHasParent: SHR-APPLICATION-4
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall enable data scientists to create revocable share tokens with an optional expiry date and to grant read access to a specific application run via such a token, allowing secure sharing with parties who do not hold a platform account. The system shall list all active share tokens for the authenticated user, optionally filtered by run. The system shall list all grants associated with a given share token. The system shall revoke a share token's grant on a specific run on demand, without invalidating the token for other runs. The one-time token secret shall be returned only at creation time and shall not be retrievable subsequently. All token operations shall operate on the Aignostics Platform access control API; each mutating operation shall invalidate the local operation cache.
