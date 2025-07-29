---
itemId: SWR-NOTEBOOK-6
itemTitle: Stop Notebook Server
itemHasParent: SHR-NOTEBOOK-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall provide shutdown capabilities for running notebook servers. When users request server shutdown, the system shall terminate the notebook server and log "Marimo server stopped" and "Service stopped" messages upon completion. The system shall properly clean up server resources during the shutdown process.