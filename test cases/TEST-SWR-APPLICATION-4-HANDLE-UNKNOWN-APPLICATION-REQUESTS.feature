Feature: TEST-SWR-APPLICATION-4-HANDLE-UNKNOWN-APPLICATION-REQUESTS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-4 @id:TEST-APPLICATION-UNKNOWN-ID-ERROR
  Scenario: System handles requests for non-existent application identifiers
    When User runs the CLI application describe command with unknown application identifier "unknown"
    Then User should see error message "Application with ID 'unknown' not found."
    And System should handle the error gracefully