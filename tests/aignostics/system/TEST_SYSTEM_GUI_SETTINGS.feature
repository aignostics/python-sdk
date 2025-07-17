Feature: System Health GUI

  Background:
    Given user started Launchpad

  @tests:SWR-SYSTEM-GUI-SETTINGS-1 @id:TEST-SYSTEM-GUI-SETTINGS-MASKING-DEFAULT
  Scenario: Mask secrets switch is enabled by default
    When User navigates to the settings page
    Then The mask secrets switch is enabled
