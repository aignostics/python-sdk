Feature: TEST-SWR-DATASET-5-DISCOVER-AVAILABLE-DATASET-SOURCES

  Background:
    Given user installed the Python SDK

  @tests:SWR-DATASET-5 @id:TEST-SWR-DATASET-5-DATASET-DISCOVERY
  Scenario: System provides comprehensive dataset discovery capabilities
    When User runs dataset discovery commands
    Then System should list available dataset indices
    And System should display dataset column information
    And System should help users understand data formats before download