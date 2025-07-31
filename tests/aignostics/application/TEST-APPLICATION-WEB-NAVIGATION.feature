Feature: Application Web Interface Access

  Background:
    Given user started Launchpad

  @tests:SWR-APPLICATION-5 @id:TEST-APPLICATION-WEB-NAVIGATION
  Scenario: User can navigate to applications through web interface
    When User opens the home page
    And User navigates to the applications section
    Then User should see available AI applications displayed

  @tests:SWR-APPLICATION-5 @id:TEST-APPLICATION-WEB-INDEX
  Scenario: Application index page displays available applications
    When User opens the applications index page
    Then User should see a list of available AI applications
    And Applications should be organized in a discoverable format