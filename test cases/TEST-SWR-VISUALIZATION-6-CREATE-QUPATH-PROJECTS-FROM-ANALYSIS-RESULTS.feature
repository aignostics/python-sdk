Feature: TEST-SWR-VISUALIZATION-6-CREATE-QUPATH-PROJECTS-FROM-ANALYSIS-RESULTS

  Background:
    Given user has QuPath installed and analysis results available

  @tests:SWR-VISUALIZATION-6 @id:TEST-SWR-VISUALIZATION-6-PROJECT-CREATION
  Scenario: System creates QuPath projects from analysis results with annotation validation
    When User requests to open results in QuPath
    Then System should download analysis results
    And System should create QuPath project structure
    And User should see "Download and QuPath project creation completed." message
    And Created project should contain at least 1000 annotations for successful import