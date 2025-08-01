Feature: TEST-SWR-VISUALIZATION-4-LIST-RUNNING-QUPATH-PROCESSES

  Background:
    Given user has QuPath installed

  @tests:SWR-VISUALIZATION-4 @id:TEST-SWR-VISUALIZATION-4-PROCESS-LIST
  Scenario: System lists running QuPath processes in structured JSON format
    When User runs QuPath processes command
    Then System should display running QuPath process information
    And Output should include process IDs in JSON format
    And System should format output as valid JSON