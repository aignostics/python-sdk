Feature: System Health GUI

  Background:
    Given user started Launchpad

  @tests:RQ-SYSTEM-GUI-HEALTH-1 @id:TEST_SYSTEM_GUI_HEALTH
  Scenario: Health is shown and updated
    When User opens any page
    Then User should see health in the footer