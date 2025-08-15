Feature: GUI Application Workflow Management

  The system provides complete graphical interface for application workflow 
  management including dataset selection, metadata generation, file upload, 
  run submission, status monitoring, and run control operations including 
  user-initiated cancellation.

  @tests:SWR-APPLICATION-1-1
  @tests:SWR-APPLICATION-1-2
  @tests:SWR-APPLICATION-2-10
  @tests:SWR-APPLICATION-2-11
  @id:TC-APPLICATION-GUI-04
  Scenario: System processes user manual cancellation of application runs through complete GUI workflow
    Given the system completes full application workflow through GUI interface
    And the system downloads sample dataset files successfully
    And the system navigates through application selection and file picking
    And the system processes metadata generation and slide detection
    And the system completes upload and submission creating a running application run
    And the system displays run with running status and cancellation controls
    When the user manually cancels the running application run through GUI button
    Then the system shall process the manual cancellation request
    And the system shall provide user feedback during cancellation process
    And the system shall confirm cancellation completion to user
    And the system shall update the run status to canceled state
    And the system shall maintain the updated state in the interface