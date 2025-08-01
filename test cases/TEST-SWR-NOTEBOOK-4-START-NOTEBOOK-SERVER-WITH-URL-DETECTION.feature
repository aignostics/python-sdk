Feature: TEST-SWR-NOTEBOOK-4-START-NOTEBOOK-SERVER-WITH-URL-DETECTION

  Background:
    Given user installed the Python SDK

  @tests:SWR-NOTEBOOK-4 @id:TEST-SWR-NOTEBOOK-4-URL-DETECTION
  Scenario: System starts servers with URL detection and success logging
    When System starts notebook servers
    Then System should monitor server startup and confirm URL detection
    And System should consider server ready when URL is available
    And System should log "Marimo server started successfully with URL [url]"