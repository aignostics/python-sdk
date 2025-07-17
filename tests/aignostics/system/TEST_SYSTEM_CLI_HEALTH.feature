Feature: System Health CLI Command

  Background:
    Given user installed the Python SDK

  @tests:SPEC-SYSTEM-CLI-1 @id:TEST_SYSTEM_CLI_HEALTH_YAML
  Scenario: Running the CLI health command should return "UP"
    When User runs the CLI health command
    Then User should see "UP" in the output

  @tests:SPEC-SYSTEM-CLI-1 @id:TEST_SYSTEM_CLI_HEALTH_JSON
  Scenario: Running the CLI health command with YAML format should return "status: UP"
    When User runs the CLI health command with YAML format
    Then User should see "status: UP" in the output