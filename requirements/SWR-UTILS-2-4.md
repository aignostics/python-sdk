---
itemId: SWR-UTILS-2-4
itemTitle: MCP Server with Auto-Discovery and CLI Commands
itemHasParent: SHR-UTILS-2
itemType: Requirement
Requirement type: FUNCTIONAL
Layer: System (backend logic)
---

System shall provide a central MCP server that automatically discovers plugin tools via entry-point-based service discovery, mounts them with namespace isolation to prevent tool name collisions, and exposes CLI commands (`mcp run` to start the stdio transport server, `mcp list-tools` to enumerate all registered tools).
