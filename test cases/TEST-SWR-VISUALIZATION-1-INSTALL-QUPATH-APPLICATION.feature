Feature: TEST-SWR-VISUALIZATION-1-INSTALL-QUPATH-APPLICATION

  Background:
    Given user installed the Python SDK

  @tests:SWR-VISUALIZATION-1 @id:TEST-SWR-VISUALIZATION-1-QUPATH-INSTALL
  Scenario: System installs QuPath application with multi-platform support
    When User runs QuPath install command with platform specification
    Then System should download and install QuPath to user data directory
    And System should support Windows, Linux, Darwin (amd64 and arm64)
    And User should see "QuPath v[version] installed successfully" confirmation