Feature: TEST-SWR-APPLICATION-2-PROVIDE-DETAILED-APPLICATION-INFORMATION

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-2 @id:TEST-APPLICATION-DESCRIBE-VERBOSE
  Scenario: System provides detailed application information with verbose output
    When User runs the CLI application list command with verbose flag
    Then User should see detailed information about AI applications
    And User should see "he-tme" in the output
    And User should see "test-app" in the output
    And User should see artifact counts in format "Artifacts: X input(s), Y output(s)"
    And User should see "Artifacts: 1 input(s), 6 output(s)" for he-tme application