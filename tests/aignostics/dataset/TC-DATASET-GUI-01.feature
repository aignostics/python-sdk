Feature: Dataset Download GUI Operations

  The system provides graphical interface for dataset download operations
  including dataset selection, destination configuration, and download
  execution with progress feedback and completion validation.

  @tests:SWR-DATASET-1-1
  @tests:SWR-DATASET-1-2
  @tests:SWR-DATASET-1-3
  @id:TC-DATASET-GUI-01
  Scenario: System processes dataset download through GUI interface
    Given the user navigates to the dataset download page
    When the user selects example dataset and configures custom dataset identifier
    And the user configures download destination through GUI controls
    Then the system shall initiate dataset download process
    And the system shall provide download progress notifications
    When the download process completes
    Then the system shall confirm download completion
    And the system shall validate downloaded files exist with correct structure and size
