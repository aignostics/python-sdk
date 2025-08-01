Feature: TEST-SWR-APPLICATION-5-PROVIDE-APPLICATION-INTERFACE-ACCESS

  Background:
    Given user started Launchpad

  @tests:SWR-APPLICATION-5 @id:TEST-APPLICATION-WEB-INDEX
  Scenario: System provides web interface for viewing AI applications
    When User opens the application web interface
    Then User should see "Atlas H&E-TME" displayed
    And User should see "Download Datasets" option available

  @tests:SWR-APPLICATION-5 @id:TEST-APPLICATION-WEB-NAVIGATION
  Scenario: System enables navigation to specific application pages
    When User navigates to specific application page for "Atlas H&E-TME"
    Then User should see application description "The Atlas H&E TME is an AI application"
    And User should see "Test Application" with "This is the test application with two algorithms"