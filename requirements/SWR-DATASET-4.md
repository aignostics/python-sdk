---
itemId: SWR-DATASET-4
itemTitle: Validate Dataset File Integrity
itemHasParent: SHR-DATASET-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall validate the integrity of downloaded dataset files by verifying file sizes against expected values. After downloading files from external datasets, the system shall check that the actual file size matches the expected file size as specified in the dataset metadata. When file sizes match the expected values (e.g., 1369290 bytes, 14681750 bytes), the system shall consider the download successful and complete the operation.