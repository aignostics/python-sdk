---
itemId: SWR-APPLICATION-2-2
itemTitle: Validate MPP Resolution Against Application Limits
itemHasParent: SHR-APPLICATION-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall validate slide resolution in microns per pixel (MPP) against application-specific limits before processing application runs. The system shall reject submissions when MPP exceeds the configured threshold and shall provide error messages indicating the specific resolution value that exceeds limits.