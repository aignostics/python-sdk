Feature: TEST-SWR-APPLICATION-17-HANDLE-DOWNLOAD-DESTINATION-ERRORS

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-17 @id:TEST-SWR-APPLICATION-17-PERMISSION-ERRORS
  Scenario: System handles directory creation failures gracefully across platforms
    When User attempts download to restricted directory "/4711"
    Then User should see "Failed to create destination directory" error message
    And System should accommodate platform-specific file system behaviors