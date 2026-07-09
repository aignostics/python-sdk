Feature: Update Run and Item Custom Metadata After Creation

  The system allows updating the custom metadata of an existing run or of an
  individual item within a run after creation. Updates support optimistic
  concurrency control via a metadata checksum, and allow the caller to choose
  whether the SDK enriches the managed `sdk` metadata field with auto-generated
  tracking context or forwards the supplied metadata unchanged.

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-01
  Scenario: System updates custom metadata of an existing run
    Given the user has access to an existing application run
    When the user updates the run's custom metadata with a valid metadata document
    Then the system shall replace the run's custom metadata and confirm success

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-02
  Scenario: System rejects a run metadata update when the checksum is stale
    Given the user has read a run's custom metadata together with its checksum
    And the run's custom metadata was modified by another process afterwards
    When the user updates the run's custom metadata supplying the previously read checksum
    Then the system shall reject the update as a concurrency conflict and instruct the user to re-read and retry

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-03
  Scenario: System forwards the supplied sdk metadata unchanged when enrichment is disabled
    Given the user has a custom metadata document containing a previously read sdk field
    When the user updates the run's custom metadata with SDK metadata enrichment disabled
    Then the system shall forward the custom metadata verbatim without merging or validating the sdk field

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-04
  Scenario: System enriches the sdk metadata field by default on update
    Given the user has access to an existing application run
    When the user updates the run's custom metadata without disabling enrichment
    Then the system shall merge auto-generated SDK tracking context into the sdk field and validate it against the SDK metadata schema

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-05
  Scenario: System dumps a run's custom metadata together with its checksum
    Given the user has access to an existing application run
    When the user dumps the run's custom metadata requesting the checksum
    Then the system shall emit the custom metadata together with its current checksum for use in a subsequent guarded update

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-2-17
  @id:TC-APPLICATION-CLI-07-06
  Scenario: System updates custom metadata of an item within a run
    Given the user has access to an existing item within an application run
    When the user updates the item's custom metadata with a valid metadata document
    Then the system shall replace the item's custom metadata and confirm success
