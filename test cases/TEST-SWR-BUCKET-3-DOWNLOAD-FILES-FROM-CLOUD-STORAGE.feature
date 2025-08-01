Feature: TEST-SWR-BUCKET-3-DOWNLOAD-FILES-FROM-CLOUD-STORAGE

  Background:
    Given user installed the Python SDK

  @tests:SWR-BUCKET-3 @id:TEST-SWR-BUCKET-3-FILE-DOWNLOAD
  Scenario: System downloads files from cloud storage with content verification and summary
    When User runs bucket download command with object prefixes and destination
    Then System should retrieve all matching files
    And System should verify content integrity by comparing original and downloaded files
    And User should see "Summary: X downloaded, Y failed, Z total" message