Feature: TEST-SWR-SYSTEM-1-PROVIDE-SYSTEM-SETTINGS-INTERFACE

  Background:
    Given user started Launchpad

  @tests:SWR-SYSTEM-1 @id:TEST-SYSTEM-GUI-SETTINGS-MASKING-DEFAULT
  Scenario: System provides settings interface with secure defaults
    When User opens the system settings page
    Then User should see "Health" section
    And User should see "Info" section  
    And User should see "Settings" section
    And User should see "Mask secrets" toggle enabled by default
    And System should protect sensitive information by default