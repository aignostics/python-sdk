Feature: TEST-SWR-APPLICATION-16-VALIDATE-DOWNLOADED-RESULT-INTEGRITY

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-16 @id:TEST-SWR-APPLICATION-16-CHECKSUM-VALIDATION
  Scenario: System ensures downloaded file integrity through checksum validation
    When User downloads analysis results with artifact metadata
    Then System should calculate file checksums for downloaded artifacts
    And System should compare checksums against artifact metadata
    And When checksums don't match, system should raise error with specific values