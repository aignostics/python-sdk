Feature: Read a Shared Application Run via Share Token

  The system allows an authenticated user who holds a share token secret to read
  an application run shared with them via the CLI — retrieving run status and
  details, dumping run and item custom metadata, and downloading results — by
  supplying the token as a command option. OAuth authentication remains required;
  the share token elevates the authenticated user's access to the shared run.

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-01
  Scenario: System describes a shared run when a valid share token is supplied
    Given a run has been shared with the authenticated user via a share token
    When the user runs the describe command with the run identifier and the share token
    Then the system shall return the run details identically to the authenticated path

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-02
  Scenario: System dumps run custom metadata when a valid share token is supplied
    Given a run has been shared with the authenticated user via a share token
    When the user runs the dump-metadata command with the run identifier and the share token
    Then the system shall emit the run's custom metadata identically to the authenticated path

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-03
  Scenario: System dumps item custom metadata when a valid share token is supplied
    Given a run has been shared with the authenticated user via a share token
    When the user runs the dump-item-metadata command with the run identifier, an item external identifier, and the share token
    Then the system shall emit the item's custom metadata identically to the authenticated path

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-04
  Scenario: System downloads shared run results when a valid share token is supplied
    Given a run has been shared with the authenticated user via a share token
    When the user runs the result download command with the run identifier, a destination directory, and the share token
    Then the system shall download the run results identically to the authenticated path

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-05
  Scenario: System denies access when the share token is invalid, expired, or revoked
    Given the user supplies a share token that is invalid, expired, or revoked
    When the user runs a share-token read command for the run
    Then the system shall report an access-denied message hinting the token may be invalid, expired, or revoked
    And the system shall exit with code 1

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-06
  Scenario: System reports run-not-found distinctly from access denied
    Given the user supplies a share token for a run identifier that does not exist
    When the user runs a share-token read command for that run
    Then the system shall report the run as not found and exit with code 2

  @tests:SPEC-APPLICATION-SERVICE
  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-07
  Scenario: System preserves authenticated behaviour when no share token is supplied
    Given the user has direct access to an application run
    When the user runs a read command without a share token
    Then the system shall behave exactly as before, passing no share token to the platform

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-3
  @id:TC-APPLICATION-CLI-08-08
  Scenario: System propagates a forbidden error from the download path without wrapping it
    Given a share-token download is denied by the platform with a forbidden response
    When the download path handles the forbidden response
    Then the system shall propagate the forbidden error unchanged rather than wrapping it into a generic runtime error
