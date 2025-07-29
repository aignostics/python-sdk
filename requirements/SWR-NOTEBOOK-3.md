---
itemId: SWR-NOTEBOOK-3
itemTitle: Serve Notebook Content via HTTP
itemHasParent: SHR-NOTEBOOK-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: API (external interfaces)
---

System shall serve notebook content through HTTP endpoints with embedded iframe functionality. When users access notebook endpoints with query parameters (e.g., "/notebook/4711?results_folder=/tmp"), the system shall return HTTP status code 200 and serve content containing an embedded iframe. The iframe shall include a source URL pointing to localhost or 127.0.0.1 with application run ID parameters, enabling integration of notebook functionality within the web interface.