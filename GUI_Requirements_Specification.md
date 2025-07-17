# GUI Requirements Specification

## Aignostics Launchpad Application

**Document Information:**

- **Document ID:** SWR-GUI-REQ-001
- **Version:** 1.0
- **Date:** July 17, 2025
- **Author:** Requirements Engineering Team
- **Status:** Draft

---

## Table of Contents

1. [Introduction](#introduction)
2. [Stakeholder Requirements (SHRs)](#stakeholder-requirements-shrs)
3. [Software Requirements (SWRs)](#software-requirements-swrs)
4. [Requirements Traceability Matrix](#requirements-traceability-matrix)
5. [Glossary](#glossary)

---

## Introduction

This document defines the requirements for the Aignostics Launchpad GUI application based on existing test cases. The requirements follow the Aignostics Requirements Engineering guidelines and are structured in three hierarchical levels: Stakeholder Requirements (SHRs), Software Requirements (SWRs), and Software Specifications (SPECs).

The GUI application enables data scientists to interact with AI applications for whole slide image analysis through a web-based interface.

---

## Stakeholder Requirements (SHRs)

### SHR-GUI-001: Home Page Access

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to access the Aignostics Launchpad homepage to begin their analysis workflow.

**Rationale:** Users need a clear entry point to the application to understand available functionality and begin their analysis tasks.

### SHR-GUI-002: Application Discovery

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to discover and access available AI applications for whole slide image analysis.

**Rationale:** Users need to identify and select appropriate AI applications for their specific analysis needs.

### SHR-GUI-003: Application Run Management

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to manage their application runs including submission, monitoring, and cancellation.

**Rationale:** Users need control over their analysis jobs to efficiently manage computational resources and respond to changing requirements.

### SHR-GUI-004: Data Upload Workflow

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to upload whole slide images through a guided workflow for analysis.

**Rationale:** Users need an intuitive process to prepare and submit their data for analysis without technical complexity.

### SHR-GUI-005: Results Download

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to download completed analysis results from their application runs.

**Rationale:** Users need access to their analysis results for further research and clinical decision-making.

### SHR-GUI-006: Dataset Integration

**Type:** User Requirement  
**Priority:** Medium  
Data scientists shall be able to access and download public datasets for testing purposes.

**Rationale:** Users need access to standardized datasets for testing and validation of analysis workflows.

### SHR-GUI-007: File Selection Interface

**Type:** User Requirement  
**Priority:** High  
Data scientists shall be able to select local directories containing whole slide images for analysis.

**Rationale:** Users need an efficient way to select and prepare their local data files for upload and analysis.

---

## Software Requirements (SWRs)

### 1. Navigation and Homepage Requirements

#### SWR-GUI-001.1: Homepage Display

**Parent:** SHR-GUI-001  
**Priority:** High  
The system shall display the Aignostics Launchpad homepage with welcome message and application overview.

**Acceptance Criteria:**

- Welcome message is visible to users
- Application overview content is displayed
- Page loads within acceptable time limits

#### SWR-GUI-001.2: Application List Display

**Parent:** SHR-GUI-002  
**Priority:** High  
The system shall display available AI applications including "Atlas H&E-TME" in the sidebar navigation.

**Acceptance Criteria:**

- Sidebar contains list of available applications
- "Atlas H&E-TME" application is visible
- Applications are clickable for navigation

#### SWR-GUI-001.3: Dataset Access Link

**Parent:** SHR-GUI-006  
**Priority:** Medium  
The system shall provide a "Download Datasets" link accessible from the main menu.

**Acceptance Criteria:**

- "Download Datasets" link is visible on homepage
- Link is accessible from main navigation

### 2. Application Navigation Requirements

#### SWR-GUI-002.1: Application Navigation

**Parent:** SHR-GUI-002  
**Priority:** High  
The system shall allow users to navigate from the homepage to specific application pages via sidebar selection.

**Acceptance Criteria:**

- Sidebar applications are clickable
- Navigation redirects to correct application page
- Application pages load within 100 retry attempts

#### SWR-GUI-002.2: Application Description Display

**Parent:** SHR-GUI-002  
**Priority:** High  
The system shall display application-specific information when users select an application, including descriptive text such as "The Atlas H&E TME is an AI application".

**Acceptance Criteria:**

- Application description is visible on application page
- Description text matches expected content for each application
- Multiple applications supported (he-tme, test-app)

### 3. Run Management Requirements

#### SWR-GUI-003.1: Run Display in Sidebar

**Parent:** SHR-GUI-003  
**Priority:** High  
The system shall display application runs in the sidebar with application version identifiers.

**Acceptance Criteria:**

- Runs section visible in sidebar
- Run items display application version identifiers
- Run items are clickable for navigation

#### SWR-GUI-003.2: Run Status Display

**Parent:** SHR-GUI-003  
**Priority:** High  
The system shall display run status including "RUNNING", "COMPLETED", and "CANCELED_USER" states.

**Acceptance Criteria:**

- Run status is clearly visible on run pages
- Status updates reflect current run state
- Supported statuses: RUNNING, COMPLETED, CANCELED_USER

#### SWR-GUI-003.3: Run Cancellation

**Parent:** SHR-GUI-003  
**Priority:** High  
The system shall provide a cancel button for running applications and update the run status to "CANCELED_USER" upon successful cancellation.

**Acceptance Criteria:**

- Cancel button is visible for running applications
- Button click triggers cancellation process
- Run status updates to "CANCELED_USER" after cancellation

#### SWR-GUI-003.4: Run Cancellation Notifications

**Parent:** SHR-GUI-003  
**Priority:** High  
The system shall display notification messages during run cancellation including "Canceling application run with id" and "Application run cancelled!" confirmations.

**Acceptance Criteria:**

- Initial cancellation notification displays with run ID
- Completion notification confirms successful cancellation
- Notifications are visible to user during process

#### SWR-GUI-003.5: Run Detail Navigation

**Parent:** SHR-GUI-003  
**Priority:** High  
The system shall allow users to navigate to detailed run pages using the run ID in the URL format "/application/run/{run_id}".

**Acceptance Criteria:**

- URL routing supports run ID parameter
- Run details page loads for valid run IDs
- Run information displays correctly on detail page

### 4. File Upload and Selection Requirements

#### SWR-GUI-004.1: File Picker Interface

**Parent:** SHR-GUI-004, SHR-GUI-007  
**Priority:** High  
The system shall provide a file picker interface with "Ok" and "Cancel" buttons for directory selection.

**Acceptance Criteria:**

- File picker dialog opens when requested
- "Ok" and "Cancel" buttons are visible
- User can interact with both buttons

#### SWR-GUI-004.2: File Selection Validation

**Parent:** SHR-GUI-004, SHR-GUI-007  
**Priority:** High  
The system shall notify users with "You did not make a selection" when canceling file selection without choosing a directory.

**Acceptance Criteria:**

- Cancellation without selection triggers notification
- Notification message matches expected text
- User receives clear feedback about action

#### SWR-GUI-004.3: Directory Selection Confirmation

**Parent:** SHR-GUI-004, SHR-GUI-007  
**Priority:** High  
The system shall display confirmation messages showing the selected directory path when users choose a folder.

**Acceptance Criteria:**

- Confirmation message displays selected directory path
- Message format includes full path information
- User receives immediate feedback on selection

#### SWR-GUI-004.4: Slide Detection

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall automatically detect and count compatible slide files in the selected directory with notifications such as "Found 1 slides for analysis".

**Acceptance Criteria:**

- System scans selected directory for compatible files
- Notification displays count of found slides
- Process completes within 20 seconds

#### SWR-GUI-004.5: Metadata Generation

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall provide metadata generation functionality with validation messaging including "Your metadata is now valid! Feel free to continue to the next step."

**Acceptance Criteria:**

- Metadata generation process is available
- Validation confirms metadata completeness
- Success message enables workflow continuation

### 5. Upload and Submission Requirements

#### SWR-GUI-004.6: Upload Interface

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall provide an upload interface displaying the number of slides ready for submission in the format "Upload and submit your X slide(s) for analysis."

**Acceptance Criteria:**

- Upload interface displays slide count
- Message format includes dynamic slide number
- Interface is accessible after metadata validation

#### SWR-GUI-004.7: Upload Process Control

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall disable the upload button during the upload process to prevent multiple simultaneous uploads.

**Acceptance Criteria:**

- Upload button becomes disabled when clicked
- Button remains disabled during upload process
- Prevents multiple concurrent uploads

#### SWR-GUI-004.8: Upload Progress Notifications

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall display upload progress notifications including "Uploading whole slide images to Aignostics Platform ..." and "Upload to Aignostics Platform completed."

**Acceptance Criteria:**

- Initial upload notification displays
- Completion notification confirms successful upload
- Progress is visible to user throughout process

#### SWR-GUI-004.9: Submission Notifications

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall display submission progress notifications including "Submitting application run ..." and "Application run submitted with id".

**Acceptance Criteria:**

- Submission progress notification displays
- Success notification includes run ID
- User receives confirmation of successful submission

#### SWR-GUI-004.10: Upload Timeout Handling

**Parent:** SHR-GUI-004  
**Priority:** High  
The system shall complete upload operations within 30 seconds and submission operations within 10 seconds.

**Acceptance Criteria:**

- Upload operations complete within 30 seconds
- Submission operations complete within 10 seconds
- Timeout handling prevents indefinite waiting

### 6. Results Download Requirements

#### SWR-GUI-005.1: Download Button Access

**Parent:** SHR-GUI-005  
**Priority:** High  
The system shall provide a download button for completed application runs.

**Acceptance Criteria:**

- Download button is visible on completed run pages
- Button is clickable and functional
- Only available for completed runs

#### SWR-GUI-005.2: Download Destination Selection

**Parent:** SHR-GUI-005  
**Priority:** High  
The system shall provide destination selection options for downloaded results including a "Data" destination option.

**Acceptance Criteria:**

- Download dialog provides destination options
- "Data" option is available for selection
- User can select preferred download location

#### SWR-GUI-005.3: Download Completion Notification

**Parent:** SHR-GUI-005  
**Priority:** High  
The system shall display "Download completed." notification within 60 seconds of initiating download.

**Acceptance Criteria:**

- Download completion notification displays
- Notification appears within 60 seconds
- User receives confirmation of successful download

#### SWR-GUI-005.4: Download Directory Structure

**Parent:** SHR-GUI-005  
**Priority:** High  
The system shall create a directory structure with the run ID as the parent directory and organize downloaded files in subdirectories.

**Acceptance Criteria:**

- Parent directory uses run ID as name
- Subdirectories are created for organization
- Directory structure is logical and navigable

#### SWR-GUI-005.5: Download File Validation

**Parent:** SHR-GUI-005  
**Priority:** High  
The system shall ensure downloaded results contain exactly 9 files per analysis item in the appropriate subdirectory structure.

**Acceptance Criteria:**

- Each analysis item subdirectory contains exactly 9 files
- File count validation is enforced
- Download integrity is maintained

### 7. Performance Requirements

#### SWR-GUI-006.1: Page Load Responsiveness

**Parent:** SHR-GUI-001, SHR-GUI-002  
**Priority:** Medium  
The system shall load application pages with up to 100 retry attempts for reliable content display.

**Acceptance Criteria:**

- Page loading supports up to 100 retry attempts
- Content displays reliably across different conditions
- Retry mechanism handles temporary failures

#### SWR-GUI-006.2: Run Status Updates

**Parent:** SHR-GUI-003  
**Priority:** Medium  
The system shall update run status displays within 200 retry attempts for status changes.

**Acceptance Criteria:**

- Status updates complete within 200 retry attempts
- Status changes are reflected accurately
- Update mechanism handles network variability

#### SWR-GUI-006.3: Sidebar Item Display

**Parent:** SHR-GUI-003  
**Priority:** Medium  
The system shall display sidebar run items within 1000 retry attempts for reliable navigation.

**Acceptance Criteria:**

- Sidebar items load within 1000 retry attempts
- Navigation elements are consistently available
- Retry mechanism ensures reliability

---

## Requirements Traceability Matrix

| SHR ID      | SWR ID         | Test Case                                               | Verification Method |
| ----------- | -------------- | ------------------------------------------------------- | ------------------- |
| SHR-GUI-001 | SWR-GUI-001.1  | test_gui_index                                          | Automated GUI Test  |
| SHR-GUI-002 | SWR-GUI-001.2  | test_gui_index                                          | Automated GUI Test  |
| SHR-GUI-002 | SWR-GUI-002.1  | test_gui_home_to_application                            | Automated GUI Test  |
| SHR-GUI-002 | SWR-GUI-002.2  | test_gui_home_to_application                            | Automated GUI Test  |
| SHR-GUI-003 | SWR-GUI-003.1  | test_gui_cli_to_run_cancel                              | Automated GUI Test  |
| SHR-GUI-003 | SWR-GUI-003.2  | test_gui_cli_to_run_cancel                              | Automated GUI Test  |
| SHR-GUI-003 | SWR-GUI-003.3  | test_gui_cli_to_run_cancel                              | Automated GUI Test  |
| SHR-GUI-003 | SWR-GUI-003.4  | test_gui_cli_to_run_cancel                              | Automated GUI Test  |
| SHR-GUI-003 | SWR-GUI-003.5  | test_gui_cli_to_run_cancel                              | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.1  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.2  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.3  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.4  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.5  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.6  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.7  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.8  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.9  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-004 | SWR-GUI-004.10 | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-005 | SWR-GUI-005.1  | test_gui_run_download                                   | Automated GUI Test  |
| SHR-GUI-005 | SWR-GUI-005.2  | test_gui_run_download                                   | Automated GUI Test  |
| SHR-GUI-005 | SWR-GUI-005.3  | test_gui_run_download                                   | Automated GUI Test  |
| SHR-GUI-005 | SWR-GUI-005.4  | test_gui_run_download                                   | Automated GUI Test  |
| SHR-GUI-005 | SWR-GUI-005.5  | test_gui_run_download                                   | Automated GUI Test  |
| SHR-GUI-006 | SWR-GUI-001.3  | test_gui_index                                          | Automated GUI Test  |
| SHR-GUI-007 | SWR-GUI-004.1  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-007 | SWR-GUI-004.2  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |
| SHR-GUI-007 | SWR-GUI-004.3  | test_gui_download_dataset_via_application_to_run_cancel | Automated GUI Test  |

---

## Glossary

**Data Scientist:** Primary user of the Aignostics Launchpad who analyzes whole slide images using AI applications.

**Whole Slide Image (WSI):** Digital representation of microscopy slides used for pathological analysis.

**Application Run:** An instance of an AI application processing submitted data, with states including RUNNING, COMPLETED, and CANCELED_USER.

**Aignostics Platform:** The cloud-based infrastructure that executes AI applications and stores results.

**Atlas H&E-TME:** Specific AI application for analyzing Hematoxylin and Eosin stained tissue for tumor microenvironment analysis.

**Run ID:** Unique identifier assigned to each application run, following the format of alphanumeric characters with hyphens.

**Launchpad:** The GUI application that provides the interface for interacting with Aignostics Platform services.

**Metadata:** Information about whole slide images including resolution, dimensions, staining method, tissue type, and disease classification.

---

**Document Control:**

- This document was generated from existing GUI test cases following Aignostics Requirements Engineering guidelines
- All requirements use "shall" for mandatory and "should" for recommended functionality
- Requirements are atomic, measurable, and implementation-independent
- Traceability is maintained between stakeholder requirements, software requirements, and test cases
