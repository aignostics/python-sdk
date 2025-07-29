---
itemId: SWR-NOTEBOOK-5
itemTitle: Handle Server Startup Timeout
itemHasParent: SHR-NOTEBOOK-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall handle timeout conditions when notebook servers fail to start within the specified timeout period. When servers fail to start within the timeout limit, the system shall raise a RuntimeError with the message "Marimo server didn't start within '[timeout]' seconds (URL not detected)." The system shall enforce startup time limits to prevent indefinite waiting during server initialization.