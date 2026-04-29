Feature: Application Version Release Documents

  The system exposes release documents (output schemas, model manuals, etc.)
  attached to an application version, allowing users to list document metadata,
  describe a single document, and download document files. Only documents with
  public visibility and uploaded status are exposed.

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-1-3
  @id:TC-APPLICATION-CLI-05-01
  Scenario: System lists release documents for an application version
    Given the user has access to an application version with release documents attached
    When the user requests the list of release documents for the application version
    Then the system shall return metadata for documents with public visibility and uploaded status
    And the system shall exclude documents with internal visibility or pending status

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-1-3
  @id:TC-APPLICATION-CLI-05-02
  Scenario: System describes a single release document
    Given the user has access to an application version with a public release document
    When the user requests metadata for that document by name
    Then the system shall return the document metadata including id, mime type, and timestamps

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-1-3
  @id:TC-APPLICATION-CLI-05-03
  Scenario: System rejects requests for non-existent or non-public release documents
    Given the user has access to an application version
    When the user requests metadata for a document that does not exist or is not public
    Then the system shall raise a not-found error indicating the document is unavailable

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-1-3
  @id:TC-APPLICATION-CLI-05-04
  Scenario: System downloads a release document file to a local path
    Given the user has access to an application version with a public release document
    When the user requests download of that document to a local destination
    Then the system shall follow the platform redirect to the signed storage URL
    And the system shall write the document file using the server-provided filename
