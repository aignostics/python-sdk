Feature: TEST-SWR-DATASET-1-DOWNLOAD-EXTERNAL-DATASET-FILES

  Background:
    Given user installed the Python SDK

  @tests:SWR-DATASET-1 @id:TEST-SWR-DATASET-1-FILE-DOWNLOAD
  Scenario: System downloads files using valid dataset identifiers with size validation
    When User provides valid dataset identifiers for download
    Then System should download corresponding files to destination directories
    And User should see "Successfully downloaded" with filename in output
    And Files should be created with expected sizes "1369290 bytes" and "14681750 bytes"