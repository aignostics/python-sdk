Feature: TEST-SWR-APPLICATION-14-DISPLAY-RUN-STATUS-DURING-DOWNLOAD

  Background:
    Given user installed the Python SDK

  @tests:SWR-APPLICATION-14 @id:TEST-SWR-APPLICATION-14-STATUS-INFORMATION
  Scenario: System displays comprehensive run status during download operations
    When User downloads results for runs in various states
    Then User should see "status: running on plat" for active runs
    And User should see "status: canceled by user." for canceled runs
    And User should see completion status for finished runs