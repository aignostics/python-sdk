---
itemId: SWR-VISUALIZATION-3
itemTitle: Launch QuPath User Interface
itemHasParent: SHR-VISUALIZATION-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall launch QuPath user interface when requested and manage the application process. When users execute the launch command, the system shall start QuPath as a new process and display a confirmation message "QuPath launched successfully with process id '[pid]'." The system shall complete the launch operation with exit code 0. When QuPath is not installed, the system shall respond with exit code 2 and display the error message "QuPath is not installed. Use 'uvx aignostics qupath install' to install it."