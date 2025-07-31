Feature: Application Unknown Request Error Handling

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-4 @id:TEST-APPLICATION-UNKNOWN-ID-ERROR
  Scenario: Running the CLI application describe command with unknown application ID should return error
    When User runs the CLI application describe command with an unknown application identifier "unknown-app-id"
    Then User should see "Application with ID 'unknown-app-id' not found." in the output

  @tests:SWR-APPLICATION-4 @id:TEST-APPLICATION-INVALID-FORMAT-ERROR
  Scenario: Running the CLI application describe command with invalid application ID should return appropriate error
    When User runs the CLI application describe command with an invalid application identifier
    Then User should see an error message about the application not being found