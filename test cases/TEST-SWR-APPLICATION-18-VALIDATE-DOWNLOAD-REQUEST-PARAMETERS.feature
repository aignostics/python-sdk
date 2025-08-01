Feature: TEST-SWR-APPLICATION-18-VALIDATE-DOWNLOAD-REQUEST-PARAMETERS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-18 @id:TEST-SWR-APPLICATION-18-NON-EXISTENT-RUNS
  Scenario: System handles requests for non-existent runs appropriately
    When User requests download for non-existent run "00000000000000000000000000000000"
    Then User should see "Run with ID '00000000000000000000000000000000' not found." message
    And System should provide guidance on finding valid run identifiers