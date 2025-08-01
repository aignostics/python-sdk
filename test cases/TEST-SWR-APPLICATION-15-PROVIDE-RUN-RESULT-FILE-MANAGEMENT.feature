Feature: TEST-SWR-APPLICATION-15-PROVIDE-RUN-RESULT-FILE-MANAGEMENT

  Background:
    Given user started Launchpad

  @tests:SWR-APPLICATION-15 @id:TEST-SWR-APPLICATION-15-DOWNLOAD-INTERFACE
  Scenario: System provides comprehensive graphical interface for result file management
    When User opens the run results management interface
    Then User should see download button for application run results
    And User should see "Download completed." notification upon completion
    And Downloaded results should be organized with run ID as directory name