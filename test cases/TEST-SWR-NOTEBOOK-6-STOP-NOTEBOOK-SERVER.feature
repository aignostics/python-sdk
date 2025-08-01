Feature: TEST-SWR-NOTEBOOK-6-STOP-NOTEBOOK-SERVER

  Background:
    Given user has running notebook server

  @tests:SWR-NOTEBOOK-6 @id:TEST-SWR-NOTEBOOK-6-SERVER-SHUTDOWN
  Scenario: System provides shutdown capabilities with proper resource cleanup
    When User requests server shutdown
    Then System should terminate notebook server
    And System should log "Marimo server stopped" and "Service stopped" messages
    And System should properly clean up server resources