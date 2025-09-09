Feature: Bucket GUI File Management Operations

  The system provides graphical interface for bucket file operations including
  file upload verification, grid display, download functionality, and deletion
  with real-time UI updates and confirmation.

  @tests:SWR-BUCKET-1-5
  @tests:SWR-BUCKET-1-6
  @tests:SWR-BUCKET-1-7
  @tests:SWR-BUCKET-1-8
  @tests:SWR-BUCKET-1-9
  @id:TC-BUCKET-GUI-01
  Scenario: System processes bucket file operations through GUI interface
    Given the user creates test files and uploads them via CLI
    When the user navigates to the bucket page in GUI
    Then the system shall display uploaded files in the bucket grid
    And the system shall show download and delete buttons in disabled state
    When the user selects files in the grid interface
    Then the system shall enable download and delete operation buttons
    When the user triggers file download through GUI controls
    Then the system shall download selected files and confirm completion
    When the user triggers file deletion through GUI controls
    Then the system shall remove selected files from bucket storage
    And the system shall update the grid to reflect file removal
