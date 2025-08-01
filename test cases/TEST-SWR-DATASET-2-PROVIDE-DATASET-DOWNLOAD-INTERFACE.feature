Feature: TEST-SWR-DATASET-2-PROVIDE-DATASET-DOWNLOAD-INTERFACE

  Background:
    Given user started Launchpad

  @tests:SWR-DATASET-2 @id:TEST-SWR-DATASET-2-DOWNLOAD-INTERFACE
  Scenario: System provides comprehensive graphical interface for dataset downloads
    When User opens the dataset download interface
    Then User should see source input field for dataset identifiers
    And User should see download destination selection mechanism
    And User should see example dataset identifiers for guidance
    And User should see "Download completed" notification upon completion