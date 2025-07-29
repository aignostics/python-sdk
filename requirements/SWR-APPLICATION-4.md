---
itemId: SWR-APPLICATION-4
itemTitle: Handle Unknown Application Requests
itemHasParent: SHR-APPLICATION-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall return an error when users request information about non-existent application identifiers. The system shall respond with exit code 2 and include an error message in the format "Application with ID '[identifier]' not found."