Feature: TEST-SWR-APPLICATION-6-EXPORT-APPLICATION-SCHEMA-FILES

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-6 @id:TEST-APPLICATION-SCHEMA-EXPORT-BASIC
  Scenario: System exports application schema files to destination directory
    When User runs the CLI application dump schemata command for "he-tme" with destination
    Then System should create organized schema files
    And User should see "Zipped 11 files" in the output when using zip option