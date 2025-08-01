Feature: TEST-SWR-APPLICATION-12-PROVIDE-RUN-MANAGEMENT-INTERFACE

  Background:
    Given user started Launchpad

  @tests:SWR-APPLICATION-12 @id:TEST-SWR-APPLICATION-12-RUN-INTERFACE
  Scenario: System provides comprehensive web interface for run management
    When User opens the run management web interface
    Then User should see run status displayed
    And User should be able to interact with run controls
    And User should be able to cancel runs through the interface