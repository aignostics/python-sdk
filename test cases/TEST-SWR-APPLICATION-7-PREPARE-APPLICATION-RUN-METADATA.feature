Feature: TEST-SWR-APPLICATION-7-PREPARE-APPLICATION-RUN-METADATA

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-7 @id:TEST-SWR-APPLICATION-7-METADATA-GENERATION
  Scenario: System generates comprehensive metadata CSV from whole slide images
    When User runs the CLI run prepare command on directory containing "small-pyramidal.dcm"
    Then System should generate metadata CSV with file properties
    And Metadata should include checksum "EfIIhA=="
    And Metadata should include resolution "8.065226874391001"
    And Metadata should include dimensions "2054x1529"