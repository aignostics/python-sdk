Feature: TEST-SWR-NOTEBOOK-8-HANDLE-MISSING-SERVER-URL

  Background:
    Given user installed the Python SDK

  @tests:SWR-NOTEBOOK-8 @id:TEST-SWR-NOTEBOOK-8-URL-VALIDATION
  Scenario: System validates URL availability and handles missing URLs appropriately
    When Server ready events are triggered but URLs are not available
    Then System should raise RuntimeError about missing server URL
    And Error should state "Server URL was not set despite server ready event being triggered."
    And System should ensure proper server configuration