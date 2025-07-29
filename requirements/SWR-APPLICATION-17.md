---
itemId: SWR-APPLICATION-17
itemTitle: Handle Download Destination Errors
itemHasParent: SHR-APPLICATION-3
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall handle download destination directory creation failures appropriately based on the operating system. When the system cannot create the destination directory due to permissions or path issues, it shall respond with exit code 2 and display an error message in the format "Failed to create destination directory '[path]/[run_id]'" on Unix-like systems. On Windows systems, the system shall complete with exit code 0 even when directory creation fails, accommodating different file system behaviors.