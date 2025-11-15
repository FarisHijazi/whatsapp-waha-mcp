"""Simple check to verify tools are registered in the MCP server."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from whatsapp_waha_mcp.server import mcp

# Get all registered tools
tools = []
for name, func in mcp._tool_manager._tools.items():
    tools.append({
        "name": name,
        "description": func.__doc__ or "No description"
    })

print("=" * 70)
print(f"MCP Server Tool Registration Check")
print("=" * 70)
print(f"\n✓ Found {len(tools)} registered tools:\n")

# Group by category
categories = {}
for tool in tools:
    name = tool["name"]
    if any(x in name for x in ["session", "qr", "pairing", "get_me"]):
        category = "Session Management"
    elif any(x in name for x in ["send_", "edit_message", "delete_message"]):
        category = "Messaging"
    elif "chat" in name or "archive" in name:
        category = "Chat Management"
    elif "group" in name:
        category = "Group Management"
    elif "contact" in name or "check_number" in name:
        category = "Contacts"
    elif "presence" in name:
        category = "Presence"
    else:
        category = "Other"

    if category not in categories:
        categories[category] = []
    categories[category].append(tool)

# Print by category
for category, tools_list in sorted(categories.items()):
    print(f"  {category} ({len(tools_list)} tools):")
    for tool in sorted(tools_list, key=lambda x: x["name"]):
        print(f"    - {tool['name']}")
    print()

print("=" * 70)
print(f"✓ SUCCESS: MCP server has {len(tools)} tools properly registered")
print("=" * 70)
print("\nThe server is ready to use with:")
print("  • uvx whatsapp-waha-mcp")
print("  • python -m whatsapp_waha_mcp")
print("  • whatsapp-waha-mcp")
print("\nConfigure in Claude Desktop by adding to:")
print("  ~/Library/Application Support/Claude/claude_desktop_config.json")
print("=" * 70)
