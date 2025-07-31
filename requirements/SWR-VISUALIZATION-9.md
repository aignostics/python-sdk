---
itemId: SWR-VISUALIZATION-9
itemTitle: Inspect Whole Slide Image Metadata
itemHasParent: SHR-VISUALIZATION-1
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: CLI (command-line interface)
---

System shall inspect whole slide image files and extract metadata information including format type, pixel dimensions, tile size, and microns per pixel (MPP) values. When users execute inspection commands on supported image formats including DICOM files, the system shall display metadata in a structured format showing Format, MPP (x), MPP (y), Dimensions in pixels, and Tile size information, and complete the operation with exit code 0.