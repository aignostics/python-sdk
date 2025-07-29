---
itemId: SWR-DATASET-1
itemTitle: Download External Dataset Files
itemHasParent: SHR-DATASET-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall allow users to download files from external datasets using dataset identifiers. When users provide valid dataset identifiers, the system shall download the corresponding files to specified destination directories and display a confirmation message "Successfully downloaded" along with the filename. The system shall complete the download operation with exit code 0 and create files with the expected file sizes as specified in the dataset metadata.