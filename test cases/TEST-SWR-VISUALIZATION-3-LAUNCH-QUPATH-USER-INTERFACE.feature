Feature: TEST-SWR-VISUALIZATION-3-LAUNCH-QUPATH-USER-INTERFACE

  Background:
    Given user has QuPath installed

  @tests:SWR-VISUALIZATION-3 @id:TEST-SWR-VISUALIZATION-3-QUPATH-LAUNCH
  Scenario: System launches QuPath user interface and handles not-installed state
    When User runs QuPath launch command
    Then System should start QuPath as new process
    And User should see "QuPath launched successfully with process id '[pid]'." confirmation

  @tests:SWR-VISUALIZATION-3 @id:TEST-SWR-VISUALIZATION-3-NOT-INSTALLED-ERROR
  Scenario: System handles QuPath launch when not installed appropriately
    When QuPath is not installed and user runs launch command
    Then User should see "QuPath is not installed. Use 'uvx aignostics qupath install' to install it." error
    And System should provide guidance for installation