Feature: TEST-SWR-VISUALIZATION-8-LAUNCH-QUPATH-WITH-PROJECT

  Background:
    Given user has QuPath installed and project files prepared

  @tests:SWR-VISUALIZATION-8 @id:TEST-SWR-VISUALIZATION-8-PROJECT-LAUNCH
  Scenario: System launches QuPath application with prepared project files
    When Project creation is completed
    Then System should launch QuPath with prepared project
    And User should see "QuPath opened successfully with process id '[pid]'" notification
    And Pid should be actual process identifier of launched QuPath instance