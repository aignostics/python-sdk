---
itemId: SWR-BUCKET-1
itemTitle: Upload Files to Cloud Storage
itemHasParent: SHR-BUCKET-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

System shall upload files and directories to cloud storage with directory structure preservation and destination prefix support. When users execute upload commands, the system shall transfer all files maintaining their relative paths, apply specified destination prefixes, and display "All files uploaded successfully!" upon completion with exit code 0.