Feature: TEST-SWR-DATASET-4-VALIDATE-DATASET-FILE-INTEGRITY

  Background:
    Given user installed the Python SDK

  @tests:SWR-DATASET-4 @id:TEST-SWR-DATASET-4-FILE-SIZE-VALIDATION
  Scenario: System ensures downloaded file integrity through size validation
    When System downloads files from external datasets
    Then System should check actual file size matches expected size from metadata
    And System should compare against dataset metadata specifications
    And When sizes match expected values, system should consider download successful