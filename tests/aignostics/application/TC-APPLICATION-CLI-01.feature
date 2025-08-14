Feature: Application Run Input Validation

  The system validates slide image resolution parameters during application 
  run submission to reject inputs that exceed application limits.

  @tests:SWR-APPLICATION-2-1,SWR-APPLICATION-2-2,SWR-APPLICATION-2-3,SWR-APPLICATION-2-4 @id:TC-APPLICATION-CLI-01
  Scenario: System rejects application run submission when slide resolution exceeds limits
    Given the user provides slide metadata with resolution exceeding application limits
    When the user uploads slides and submits application run
    Then the system shall reject the submission with validation error
    And the system shall indicate the resolution parameter exceeds allowed limits