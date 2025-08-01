Feature: TEST-SWR-VISUALIZATION-7-TERMINATE-QUPATH-PROCESSES

  Background:
    Given user has running QuPath processes

  @tests:SWR-VISUALIZATION-7 @id:TEST-SWR-VISUALIZATION-7-PROCESS-TERMINATION
  Scenario: System terminates running QuPath processes with confirmation
    When User runs QuPath terminate command
    Then System should terminate all running QuPath processes
    And User should see "Terminated [count] running QuPath processes." confirmation
    And Count should reflect actual number of terminated processes