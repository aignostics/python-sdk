---
itemId: SWR-APPLICATION-16
itemTitle: Validate Downloaded Result Integrity
itemHasParent: SHR-APPLICATION-3
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall validate the integrity of downloaded analysis results by comparing file checksums against artifact metadata. The system shall calculate file checksums for downloaded artifacts and compare them against the checksum values stored in artifact metadata using the specified checksum attribute key. When checksums do not match, the system shall raise an assertion error with the message "Metadata checksum != file checksum [metadata_value] <> [calculated_value]".