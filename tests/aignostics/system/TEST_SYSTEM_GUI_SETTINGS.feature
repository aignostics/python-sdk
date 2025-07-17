Feature: System Health GUI

  Background:
    Given user started Launchpad

  @tests:RQ-SYSTEM-GUI-SETTINGS-1 @id:TEST_SYSTEM_GUI_SETTINGS_MASKING_DEFAULT
  Scenario: Mask secrets switch is enabled by default
    When User navigates to the settings page
    Then The mask secrets switch is enabled
