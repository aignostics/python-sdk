Feature: TEST-SWR-VISUALIZATION-2-UNINSTALL-QUPATH-APPLICATION

  Background:
    Given user has QuPath installed

  @tests:SWR-VISUALIZATION-2 @id:TEST-SWR-VISUALIZATION-2-QUPATH-UNINSTALL
  Scenario: System uninstalls QuPath application with platform support
    When User runs QuPath uninstall command with platform parameters
    Then System should remove QuPath from user data directory
    And System should support platform-specific uninstallation
    And User should see "QuPath uninstalled successfully." confirmation