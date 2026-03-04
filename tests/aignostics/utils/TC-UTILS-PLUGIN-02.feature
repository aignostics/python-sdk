Feature: Plugin CLI Command Integration

  The SDK automatically registers CLI commands contributed by plugin modules
  into the SDK command-line interface when the plugin is installed.

  @tests:SWR-UTILS-2-2
  @id:TC-UTILS-PLUGIN-02
  Scenario: Plugin CLI commands are registered in the SDK CLI after installation
    Given a plugin package registers an entry point under "aignostics.plugins"
    And the plugin exposes a Typer CLI instance
    When the SDK CLI is prepared via prepare_cli()
    Then the plugin's CLI is registered in the SDK command-line interface
