Feature: Bucket Complete Data Lifecycle Management

  The system provides complete bucket operations for file storage including
  upload, discovery, download, and deletion with content validation and
  cleanup verification.

  @tests:SWR-BUCKET-1-1
  @tests:SWR-BUCKET-1-2
  @tests:SWR-BUCKET-1-3
  @tests:SWR-BUCKET-1-4
  @id:TC-BUCKET-CLI-01
  Scenario: System processes complete bucket data lifecycle operations
    Given the user creates test files in multiple subdirectories
    When the user uploads the directory structure to bucket storage
    Then the system shall store all files with proper organization
    When the user searches for uploaded files
    Then the system shall return all uploaded files with correct paths
    When the user downloads files to a new location
    Then the system shall retrieve files with identical content validation
    When the user deletes files individually from bucket storage
    Then the system shall remove each file and confirm deletion
    And the system shall report file not found for subsequent deletion attempts