Feature: TEST-SWR-BUCKET-2-FIND-AND-LIST-CLOUD-STORAGE-OBJECTS

  Background:
    Given user installed the Python SDK

  @tests:SWR-BUCKET-2 @id:TEST-SWR-BUCKET-2-OBJECT-SEARCH
  Scenario: System finds and lists cloud storage objects with detailed information
    When User runs bucket find command with detailed output requested
    Then System should search for objects and display results
    And Results should include filenames and full object paths with prefix structures