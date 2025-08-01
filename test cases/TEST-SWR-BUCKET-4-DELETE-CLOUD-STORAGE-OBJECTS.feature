Feature: TEST-SWR-BUCKET-4-DELETE-CLOUD-STORAGE-OBJECTS

  Background:
    Given user installed the Python SDK

  @tests:SWR-BUCKET-4 @id:TEST-SWR-BUCKET-4-OBJECT-DELETION
  Scenario: System deletes cloud storage objects with appropriate confirmation messages
    When User runs bucket delete command with object keys
    Then System should remove matching objects
    And User should see "Deleted X object(s) matching ['key']" confirmation

  @tests:SWR-BUCKET-4 @id:TEST-SWR-BUCKET-4-NO-OBJECTS-FOUND
  Scenario: System handles deletion attempts when no objects match criteria
    When No objects match deletion criteria
    Then User should see "No objects found matching pattern ['key']" message
    And System should complete operation successfully