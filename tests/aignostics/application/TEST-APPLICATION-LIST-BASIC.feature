Feature: Application List Command

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-1 @id:TEST-APPLICATION-LIST-BASIC
  Scenario: Running the CLI application list command should return available applications
    When User runs the CLI application list command
    Then User should see application names in the output

  @tests:SWR-APPLICATION-1 @id:TEST-APPLICATION-LIST-YAML
  Scenario: Running the CLI application list command with YAML format should return "applications:"
    When User runs the CLI application list command with output format set to YAML
    Then User should see "applications:" in the output