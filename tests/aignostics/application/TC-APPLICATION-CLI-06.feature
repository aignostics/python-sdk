Feature: Run Sharing and Access Management

  The system supports granting, listing, and revoking access to application runs
  via both direct organization grants and revocable share tokens.

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-1
  @id:TC-APPLICATION-CLI-06-01
  Scenario: System grants organization access to an application run
    Given the data scientist has an existing application run
    When the data scientist grants read access to the run for an organization user
    Then the system shall create an access grant on the Aignostics Platform
    And the system shall return the grant with subject type, subject identifier, and relation

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-1
  @id:TC-APPLICATION-CLI-06-02
  Scenario: System lists active access grants for an application run
    Given the data scientist has a run with one or more active grants
    When the data scientist requests the list of grants for that run
    Then the system shall return all active grants including their subject type and subject identifier

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-1
  @id:TC-APPLICATION-CLI-06-03
  Scenario: System revokes an organization access grant for an application run
    Given the data scientist has an active grant on an application run
    When the data scientist revokes that grant
    Then the system shall remove the grant via the Aignostics Platform access control API
    And the system shall invalidate the local operation cache

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-2
  @id:TC-APPLICATION-CLI-06-04
  Scenario: System creates a share token and grants it access to an application run
    Given the data scientist has an existing application run
    When the data scientist creates a share token and grants it access to the run
    Then the system shall return the share token with the one-time secret populated
    And the system shall create an access grant linking the token to the run

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-2
  @id:TC-APPLICATION-CLI-06-05
  Scenario: System lists share tokens for the authenticated user
    Given the data scientist has one or more active share tokens
    When the data scientist requests the list of share tokens
    Then the system shall return all active tokens without exposing the token secret

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-2
  @id:TC-APPLICATION-CLI-06-06
  Scenario: System revokes share token access to a specific application run
    Given the data scientist has a share token granted access to an application run
    When the data scientist revokes the token's grant for that run
    Then the system shall remove only the grant for that run via the platform API
    And the token shall remain valid for any other runs it was granted access to

  @tests:SPEC-PLATFORM-SERVICE
  @tests:SWR-APPLICATION-4-1
  @tests:SWR-APPLICATION-4-2
  @tests:SHR-APPLICATION-4
  @id:TC-APPLICATION-CLI-06-07
  Scenario: System supports end-to-end run sharing workflow using share tokens
    Given the data scientist has a completed application run on the staging platform
    When the data scientist creates a share token with an expiry date
    And the data scientist grants the token read access to the run
    Then the system shall confirm the grant is active and lists the token under share tokens for the run
    When the data scientist revokes the token's grant for the run
    Then the system shall confirm no active grants exist for the token on that run
