Feature: TEST-SWR-BUCKET-1-UPLOAD-FILES-TO-CLOUD-STORAGE

  Background:
    Given user installed the Python SDK

  @tests:SWR-BUCKET-1 @id:TEST-SWR-BUCKET-1-FILE-UPLOAD
  Scenario: System uploads files and directories to cloud storage preserving structure
    When User runs bucket upload command with files and directories
    Then System should transfer all files maintaining relative paths
    And System should apply specified destination prefixes
    And User should see "All files uploaded successfully!" message