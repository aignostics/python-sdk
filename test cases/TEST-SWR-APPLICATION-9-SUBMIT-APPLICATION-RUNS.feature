Feature: TEST-SWR-APPLICATION-9-SUBMIT-APPLICATION-RUNS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-9 @id:TEST-SWR-APPLICATION-9-SUCCESSFUL-SUBMISSION
  Scenario: System submits application runs with valid parameters
    When User runs the CLI run submit command with valid metadata CSV
    Then System should validate application version identifiers
    And User should see run submission confirmation with unique identifier

  @tests:SWR-APPLICATION-9 @id:TEST-SWR-APPLICATION-9-VALIDATION-ERRORS
  Scenario: System validates metadata and prevents invalid submissions
    When User submits application run with invalid MPP values
    Then User should see "Invalid metadata for artifact `user_slide`" error
    And User should see "8.065226874391001 is greater than" validation message