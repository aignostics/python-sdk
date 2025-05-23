## Glossary

### A

**Administrator Role**  
A user role within an organization that has permissions to invite and manage additional users, define user-specific quotas, and monitor organizational usage.

**Aignostics CLI**  
Command-Line Interface that allows interaction with the Aignostics Platform directly from terminal or shell scripts, enabling dataset management and application runs.

**Aignostics Client Library**  
Python library for seamless integration of the Aignostics Platform with enterprise image management systems and scientific workflows.

**Aignostics Console**  
Web-based user interface for managing organizations, applications, quotas, users, and monitoring platform usage.

**Aignostics Launchpad**  
Graphical desktop application (available for Mac OS X, Windows, and Linux) that allows users to run computational pathology applications on whole slide images and inspect results with QuPath and Python Notebooks.

**Aignostics Platform**  
Comprehensive cloud-based service providing standardized, secure interface for accessing advanced computational pathology applications without requiring specialized expertise or complex infrastructure.

**Aignostics Platform API**  
RESTful web service that allows programmatic interaction with the Aignostics Platform, providing endpoints for submitting WSIs, checking application run status, and retrieving results.

**Aignostics Python SDK**  
Software Development Kit providing multiple pathways to interact with the Aignostics Platform, including the Launchpad, CLI, Client Library, and example notebooks.

**Application**  
Fully automated advanced machine learning workflow composed of specific tasks (e.g., Tissue Quality Control, Tissue Segmentation, Cell Detection, Cell Classification) designed for particular analysis purposes.

**Application Run**  
The execution instance of an application on submitted whole slide images, which can be in various states: received, scheduled, running, completed, rejected, cancelled by system, or cancelled by user.

**Application Version**  
Specific version of an application with defined input requirements, processing tasks, and output formats. Each application can have multiple versions.

**Atlas H&E-TME**  
Advanced computational pathology application for Hematoxylin and Eosin-stained Tumor Microenvironment analysis.

### B

**Base MPP (Microns Per Pixel)**  
Metadata parameter specifying the resolution of whole slide images, indicating the physical distance represented by each pixel.

**Business Agreement**  
Formal contract between an organization and Aignostics required for platform access, defining quotas, applications, and terms of service.

### C

**Checksum CRC32C**  
Cyclic Redundancy Check used to verify data integrity of uploaded whole slide images.

**Client**  
The main class in the Aignostics Python SDK used to initialize connections and interact with the platform API.

**Computational Pathology**  
Field combining digital pathology with artificial intelligence and machine learning to analyze histopathology slides quantitatively.

**Aignostics Console**  
Web-based user interface for managing organizations, applications, quotas, users, and monitoring platform usage.

### D

**DICOM (Digital Imaging and Communications in Medicine)**  
Standard format for medical imaging data, supported by the Aignostics Platform for whole slide images.

**Download URL**  
Signed URL that allows the Aignostics Platform to securely download image data during processing.

### G

**GeoJSON**  
Standard format used by QuPath for representing polygonal annotations and results.

**Google Storage Bucket**  
Cloud storage service where users can store whole slide images and generate signed URLs for platform access.

### H

**H&E (Hematoxylin and Eosin)**  
Common histological staining method for tissue visualization, used in Atlas H&E-TME application.

**Heatmaps**  
Visual representations of analysis results provided in TIFF format showing spatial distribution of measurements.

### I

**IDC (NCI Image Data Commons)**  
Public repository of medical imaging data that can be queried and downloaded through the Aignostics CLI.

**IMS (Imaging Management Systems)**  
Enterprise systems for managing medical imaging data that can be integrated with the Aignostics Platform.

**Input Artifact**  
Data object required for application processing, including the actual data file and associated metadata.

**Input Item**  
Individual unit of processing in an application run, containing one or more input artifacts with a unique reference identifier.

**Interactive API Explorer**  
Tool for exploring and testing API endpoints and parameters interactively.

### J

**Jupyter**  
Popular notebook environment supported by the Aignostics Platform for interactive analysis and visualization.

### L

**LIMS (Laboratory Information Management Systems)**  
Laboratory systems that can be integrated with the Aignostics Platform for workflow automation.

### M

**Marimo**  
Modern notebook environment supported by the Aignostics Platform as an alternative to Jupyter.

**Metadata**  
Descriptive information about whole slide images including dimensions, resolution, tissue type, and disease information required for processing.

**MPP (Microns Per Pixel)**  
See Base MPP.

### N

**NCI Image Data Commons (IDC)**  
See IDC.

### O

**Operational Excellence**  
Aignostics' commitment to high-quality software development practices including A-grade code quality, security scanning, and comprehensive documentation.

### P

**Pyramidal**  
Multi-resolution image format that stores the same image at different zoom levels for efficient viewing and processing.

**Python SDK**  
Software Development Kit providing multiple pathways to interact with the Aignostics Platform through Python programming language.

### Q

**QuPath**  
Open-source software for bioimage analysis that can be launched directly from the Aignostics Launchpad to view results.

**Quota**  
Limit on the number of whole slide images an organization or user can process per calendar month, as defined in business agreements.

### R

**Reference**  
Unique identifier string for each input item in an application run, used to match results with original inputs.

**Results**  
Output data from application processing, including measurements, statistics, heatmaps, and annotations, automatically deleted after 30 days.

**RESTful API**  
Architectural style for web services that the Aignostics Platform API follows, enabling language-agnostic integration.

### S

**Self-signed URLs**  
Secure URLs with embedded authentication that allow the platform to access user data without exposing credentials.

**SVS**  
Aperio ScanScope Virtual Slide format, commonly used for whole slide images and supported by the platform.

### T

**Test Application**  
Free application automatically available to all registered organizations for workflow configuration and integration testing.

**TIFF (Tagged Image File Format)**  
Standard image format supported for both input whole slide images and output heatmaps.

**Tissue Segmentation**  
Computational process of identifying and delineating different tissue regions within histopathology slides.

**TME (Tumor Microenvironment)**  
The cellular environment surrounding tumor cells, analyzed by the Atlas H&E-TME application.

**Two-Factor Authentication (2FA)**  
Mandatory security requirement for all user accounts on the Aignostics Platform.

### U

**UV**  
Modern Python package manager used for dependency management and project setup in the SDK documentation.

**UVX**  
Tool for running Python applications directly without explicit installation, used to execute Aignostics CLI commands.

### W

**Whole Slide Image (WSI)**  
High-resolution digital image of an entire histopathology slide, the primary input format for computational pathology applications.

**Workflow**  
Sequence of automated processing steps within an application that transform input images into analytical results.
