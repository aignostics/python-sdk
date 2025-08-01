Feature: TEST-SWR-APPLICATION-13-DOWNLOAD-APPLICATION-RUN-RESULTS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-13 @id:TEST-SWR-APPLICATION-13-SUCCESSFUL-DOWNLOAD
  Scenario: System downloads analysis results from completed runs
    When User runs the CLI run result download command with valid run identifier
    Then User should see "Downloaded results of run '[run_id]'" confirmation
    And System should download analysis results to destination directory

  @tests:SWR-APPLICATION-13 @id:TEST-SWR-APPLICATION-13-INVALID-RUN-HANDLING
  Scenario: System handles invalid run identifiers appropriately
    When User runs download command with invalid run ID "4711"
    Then User should see "Run ID '4711' invalid" error message
    And System should provide guidance on valid run ID format