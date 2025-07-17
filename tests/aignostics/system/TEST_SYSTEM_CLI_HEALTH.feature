Feature: System Health CLI Command

  Background:
    Given user installed the Python SDK

  @tests:SWR-SYSTEM-CLI-HEALTH-1 @id:TEST-SYSTEM-CLI-HEALTH-YAML
  Scenario: Running the CLI health command should return "UP"
    When User runs the CLI health command
    Then User should see "UP" in the output

  @tests:SWR-SYSTEM-CLI-HEALTH-1 @id:TEST-SYSTEM-CLI-HEALTH-JSON
  Scenario: Running the CLI health command with YAML enabled should return "status: UP"
    When User runs the CLI health command with output format set to YAML
    Then User should see "status: UP" in the output
