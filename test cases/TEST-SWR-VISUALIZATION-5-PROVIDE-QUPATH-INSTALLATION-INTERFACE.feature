Feature: TEST-SWR-VISUALIZATION-5-PROVIDE-QUPATH-INSTALLATION-INTERFACE

  Background:
    Given user started Launchpad

  @tests:SWR-VISUALIZATION-5 @id:TEST-SWR-VISUALIZATION-5-INSTALLATION-INTERFACE
  Scenario: System provides graphical interface for QuPath installation with health status
    When User opens QuPath installation interface
    Then Interface should display installation status messages
    And Interface should show "Install QuPath to enable visualizing your Whole Slide Image and application results" when not installed
    And Interface should show "Launchpad is unhealthy" when QuPath not installed
    And Interface should show "Launchpad is healthy" with "[version] is installed and ready to execute" when installed