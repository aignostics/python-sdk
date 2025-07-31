---
itemId: SWR-BUCKET-4
itemTitle: Delete Cloud Storage Objects
itemHasParent: SHR-BUCKET-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

System shall delete objects from cloud storage with confirmation and error handling. When users execute delete commands with object keys, the system shall remove matching objects and display confirmation messages in the format "Deleted X object(s) matching ['key']". When no objects match the deletion criteria, the system shall display "No objects found matching pattern ['key']" and complete the operation with exit code 0.