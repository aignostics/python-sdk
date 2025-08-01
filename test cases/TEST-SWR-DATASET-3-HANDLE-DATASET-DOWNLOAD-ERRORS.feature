Feature: TEST-SWR-DATASET-3-HANDLE-DATASET-DOWNLOAD-ERRORS

  Background:
    Given user installed the Python SDK

  @tests:SWR-DATASET-3 @id:TEST-SWR-DATASET-3-NO-IDS-PROVIDED
  Scenario: System handles missing dataset identifiers appropriately
    When No dataset identifiers are provided for download
    Then User should see "Download failed: No IDs provided." error message
    And System should validate input parameters before attempting download

  @tests:SWR-DATASET-3 @id:TEST-SWR-DATASET-3-INVALID-IDENTIFIERS
  Scenario: System handles invalid dataset identifiers with descriptive errors
    When Invalid identifiers are provided that don't match datasets
    Then User should see error about values not matching identifiers
    And Error should mention collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID