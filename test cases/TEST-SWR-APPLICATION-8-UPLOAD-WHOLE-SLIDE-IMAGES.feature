Feature: TEST-SWR-APPLICATION-8-UPLOAD-WHOLE-SLIDE-IMAGES

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-8 @id:TEST-SWR-APPLICATION-8-SUCCESSFUL-UPLOAD
  Scenario: System uploads whole slide images using valid metadata CSV
    When User runs the CLI run upload command with valid metadata CSV
    Then User should see "Upload completed." message
    And System should validate referenced file existence

  @tests:SWR-APPLICATION-8 @id:TEST-SWR-APPLICATION-8-MISSING-FILES-ERROR
  Scenario: System handles missing source files during upload
    When User runs the CLI run upload command with metadata referencing missing files
    Then User should see warning "Source file 'missing.file' (row 0) does not exist"
    And System should prevent upload of incomplete datasets