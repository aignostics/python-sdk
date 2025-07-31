Feature: Application Describe Command with Detailed Information

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-2 @id:TEST-APPLICATION-DESCRIBE-VERBOSE
  Scenario: Running the CLI application describe command with verbose output should return "Artifacts:"
    When User runs the CLI application describe command with verbose output enabled
    Then User should see "Artifacts:" in the output

  @tests:SWR-APPLICATION-2 @id:TEST-APPLICATION-DESCRIBE-ARTIFACTS-COUNT
  Scenario: Running the CLI application describe command with verbose output should show artifact counts
    When User runs the CLI application describe command with verbose output enabled
    Then User should see input and output artifact counts in the format "X input(s), Y output(s)"