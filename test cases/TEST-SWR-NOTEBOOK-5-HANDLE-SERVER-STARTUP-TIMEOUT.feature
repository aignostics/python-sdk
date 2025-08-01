Feature: TEST-SWR-NOTEBOOK-5-HANDLE-SERVER-STARTUP-TIMEOUT

  Background:
    Given user installed the Python SDK

  @tests:SWR-NOTEBOOK-5 @id:TEST-SWR-NOTEBOOK-5-TIMEOUT-HANDLING
  Scenario: System handles timeout conditions and enforces startup time limits
    When Servers fail to start within timeout limit
    Then System should raise RuntimeError with timeout message
    And Error should include "Marimo server didn't start within '[timeout]' seconds (URL not detected)."
    And System should prevent indefinite waiting during initialization