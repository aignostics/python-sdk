Feature: TEST-SWR-APPLICATION-1-LIST-APPLICATIONS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-1 @id:TEST-APPLICATION-LIST-BASIC
  Scenario: System provides list of available AI applications
    When User runs the CLI application list command
    Then User should see available AI applications with their identifiers
    And User should see "he-tme" in the output
    And User should see "test-app" in the output

  @tests:SWR-APPLICATION-1 @id:TEST-APPLICATION-LIST-YAML
  Scenario: System supports YAML output format for application listing
    When User runs the CLI application list command with output format set to YAML
    Then User should see "applications:" in the output
    And Output should be valid YAML structure