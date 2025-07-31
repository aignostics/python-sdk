Feature: Application Describe Command for Specific Applications

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-3 @id:TEST-APPLICATION-DESCRIBE-SPECIFIC-ID
  Scenario: Running the CLI application describe command with valid application ID should return specific details
    When User runs the CLI application describe command with a valid application identifier
    Then User should see application-specific information

  @tests:SWR-APPLICATION-3 @id:TEST-APPLICATION-DESCRIBE-ARTIFACTS-ID
  Scenario: Running the CLI application describe command with valid application ID should show artifact identifiers
    When User runs the CLI application describe command with a valid application identifier
    Then User should see artifact identifiers in the output