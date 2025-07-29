---
itemId: SWR-NOTEBOOK-7
itemTitle: Handle Already Running Server
itemHasParent: SHR-NOTEBOOK-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall handle requests to start notebook servers when a server is already running. When servers are already running and users attempt to start another server, the system shall log "Marimo server is already running" warnings and return the existing server URL without starting a new server instance.