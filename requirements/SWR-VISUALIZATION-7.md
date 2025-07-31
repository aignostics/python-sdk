---
itemId: SWR-VISUALIZATION-7
itemTitle: Terminate QuPath Processes
itemHasParent: SHR-VISUALIZATION-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall terminate running QuPath processes when requested by users. When users execute the terminate command, the system shall terminate all running QuPath processes and display a confirmation message "Terminated [count] running QuPath processes." where count reflects the actual number of terminated processes. The system shall complete the termination operation with exit code 0.