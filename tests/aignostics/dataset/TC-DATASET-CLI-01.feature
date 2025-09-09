Feature: Dataset Download Management

  The system provides dataset download capabilities with file validation, 
  integrity verification, and completion confirmation.

  @tests:SWR-DATASET-1-1
  @tests:SWR-DATASET-1-2
  @tests:SWR-DATASET-1-3
  @id:TC-DATASET-CLI-01
  Scenario: System downloads dataset through user request
    Given the user specifies a valid dataset identifier or URL
    When the user initiates dataset download with destination directory
    Then the system shall download the dataset successfully with proper directory structure
    And the system shall verify downloaded files are complete, uncorrupted, and have valid format integrity
    And the system shall provide download completion confirmation
