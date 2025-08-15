Feature: Notebook Extension Management via GUI

  The system provides graphical interface for managing Marimo notebook
  extension including launch capabilities, iframe integration, and
  navigation controls for interactive data analysis workflows.

  @tests:SWR-NOTEBOOK-1-1
  @id:TC-NOTEBOOK-GUI-01
  Scenario: System manages notebook extension through GUI interface
    Given the user navigates to notebook extension management page
    When the user launches Marimo extension through GUI controls
    Then the system shall transition to notebook interface with iframe integration
    And the system shall provide embedded Marimo notebook functionality
    When the user navigates back to notebook management
    Then the system shall return to extension management interface
    And the system shall maintain proper navigation state and controls