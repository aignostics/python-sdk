---
itemId: SWR-DATASET-3
itemTitle: Handle Dataset Download Errors
itemHasParent: SHR-DATASET-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall handle various dataset download error conditions with appropriate error messages. When no dataset identifiers are provided, the system shall display "Download failed: No IDs provided." When invalid identifiers are provided that don't match any dataset identifiers, the system shall display "Download failed: None of the values passed matched any of the identifiers: collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID." The system shall validate input parameters before attempting download operations.