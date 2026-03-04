Feature: Plugin GUI Page Integration

  The SDK automatically registers GUI navigation entries contributed by plugin
  modules into the SDK graphical user interface when the plugin is installed.

  @tests:SWR-UTILS-2-3
  @id:TC-UTILS-PLUGIN-03
  Scenario: Plugin GUI navigation entries are available in the SDK after installation
    Given a plugin package registers an entry point under "aignostics.plugins"
    And the plugin exposes a BaseNavBuilder subclass
    When the SDK GUI collects navigation groups via gui_get_nav_groups()
    Then the plugin's navigation entries are included in the SDK navigation
