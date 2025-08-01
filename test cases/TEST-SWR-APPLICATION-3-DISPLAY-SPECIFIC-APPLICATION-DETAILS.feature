Feature: TEST-SWR-APPLICATION-3-DISPLAY-SPECIFIC-APPLICATION-DETAILS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-3 @id:TEST-APPLICATION-DESCRIBE-SPECIFIC-ID
  Scenario: System displays details for specific application identifier
    When User runs the CLI application describe command with valid application identifier "he-tme"
    Then User should see application-specific information
    And User should see artifact identifiers in the output
    And User should see "tissue_qc:geojson_polygons" in the output

  @tests:SWR-APPLICATION-3 @id:TEST-APPLICATION-DESCRIBE-ARTIFACTS-ID
  Scenario: System includes comprehensive artifact information in application details
    When User runs the CLI application describe command with a valid application identifier
    Then User should see all input and output artifact identifiers
    And System should display artifact types and descriptions