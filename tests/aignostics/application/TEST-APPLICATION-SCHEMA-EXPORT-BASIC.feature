Feature: Application Schema Export Command

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-6 @id:TEST-APPLICATION-SCHEMA-EXPORT-BASIC
  Scenario: Running the CLI application dump schemata command should export schema files
    When User runs the CLI application dump schemata command with a destination directory
    Then User should see a confirmation message indicating the number of files processed

  @tests:SWR-APPLICATION-6 @id:TEST-APPLICATION-SCHEMA-EXPORT-FILES
  Scenario: Running the CLI application dump schemata command should create files in destination
    When User runs the CLI application dump schemata command with a destination directory
    Then Schema files should be created in the destination directory