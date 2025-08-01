Feature: TEST-SWR-APPLICATION-10-MANAGE-APPLICATION-RUN-LIFECYCLE

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-10 @id:TEST-SWR-APPLICATION-10-LIST-RUNS
  Scenario: System lists runs with pagination and status information
    When User runs the CLI run list command with limit "10"
    Then User should see "Application Run IDs:" in output
    And User should see run count message "Listed 'X' run(s)."

  @tests:SWR-APPLICATION-10 @id:TEST-SWR-APPLICATION-10-CANCEL-RUNS
  Scenario: System cancels active runs using valid identifiers
    When User runs the CLI run cancel command with valid run identifier
    Then User should see "Run with ID '[run_id]' has been canceled." message
    And System should update run status to "CANCELED_USER"