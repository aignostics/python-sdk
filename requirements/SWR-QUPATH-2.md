---
itemId: SWR-QUPATH-2
itemTitle: Uninstall QuPath Application
itemHasParent: SHR-QUPATH-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall uninstall QuPath application when requested by users. When users execute the uninstall command, the system shall remove QuPath from the user data directory and display a confirmation message "QuPath uninstalled successfully." The system shall complete the uninstallation with exit code 0. The system shall support platform-specific uninstallation and allow platform specification via command-line parameters to match the installation configuration.