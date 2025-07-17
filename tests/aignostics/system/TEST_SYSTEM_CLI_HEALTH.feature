Feature: System Health CLI Command

  Background:
    Given user installed the Python SDK

  @tests:RQ-SYSTEM-CLI-HEALTH-1 @id:TEST_SYSTEM_CLI_HEALTH_YAML
  Scenario: Running the CLI health command should return "UP"
    When User runs the CLI health command
    Then User should see "UP" in the output

  @tests:RQ-SYSTEM-CLI-HEALTH-1 @id:TEST_SYSTEM_CLI_HEALTH_JSON
  Scenario: Running the CLI health command with YAML enabled should return "status: UP"
    When User runs the CLI health command with output format set to YAML
    Then User should see "status: UP" in the output
