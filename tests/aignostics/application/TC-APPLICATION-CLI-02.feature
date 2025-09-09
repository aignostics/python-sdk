Feature: Application Run CLI Commands

  The system provides CLI commands for basic application run operations
  including submission, status inquiry, cancellation, and result download
  with proper functionality across different run states.

  @tests:SWR-APPLICATION-2-5
  @tests:SWR-APPLICATION-2-6
  @tests:SWR-APPLICATION-2-7
  @tests:SWR-APPLICATION-3-1
  @id:TC-APPLICATION-CLI-02
  Scenario: System processes CLI commands for run management operations
    Given the system receives a run submission request via CLI
    When the system processes the submission
    Then the system shall create a run and return a unique run identifier
    When the system receives a describe command for the run
    Then the system shall return run details and current status
    When the system receives a download command for the active run
    Then the system shall download results and indicate running state
    When the system receives a cancel command for the run
    Then the system shall cancel the run and confirm the operation
    When the system receives another describe command for the canceled run
    Then the system shall return updated status showing canceled state
    When the system receives a download command for the canceled run
    Then the system shall download results and indicate canceled state
    And the system shall handle path verification for download destinations
