Feature: MCP Server Plugin Auto-Discovery

  The central MCP server discovers plugin tools registered via Python entry
  points, mounts them with namespace isolation, and serves them to MCP clients.

  @tests:SPEC-UTILS-SERVICE
  @tests:SWR-UTILS-1-1
  @id:TC-UTILS-MCP-01
  Scenario: Server discovers plugin tools via entry points and serves them to a client
    Given a plugin package registers an entry point under "aignostics.plugins"
    And the plugin exposes a FastMCP instance with tools "dummy_echo" and "dummy_add"
    When the MCP server is created via mcp_create_server()
    And a client connects and lists tools via client.list_tools()
    Then the returned tool list includes "dummy_plugin_dummy_echo" and "dummy_plugin_dummy_add"
    And calling "dummy_plugin_dummy_echo" with message "hello" returns "hello"
