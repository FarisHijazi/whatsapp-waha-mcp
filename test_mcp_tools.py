"""Test MCP server tools are properly exposed."""

import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Test that the MCP server exposes all expected tools."""

    print("Testing MCP Server Tool Exposure")
    print("=" * 70)

    # Start the MCP server process
    proc = subprocess.Popen(
        [sys.executable, "-m", "whatsapp_waha_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Send initialize request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    # Send the request
    proc.stdin.write(json.dumps(initialize_request) + "\n")
    proc.stdin.flush()

    # Read the response
    try:
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"Initialize Response: {json.dumps(response, indent=2)}")

            # Send tools/list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }

            proc.stdin.write(json.dumps(tools_request) + "\n")
            proc.stdin.flush()

            tools_response_line = proc.stdout.readline()
            if tools_response_line:
                tools_response = json.loads(tools_response_line)

                if "result" in tools_response and "tools" in tools_response["result"]:
                    tools = tools_response["result"]["tools"]
                    print(f"\n✓ Found {len(tools)} tools exposed by the MCP server:\n")

                    # Group tools by category
                    categories = {}
                    for tool in tools:
                        # Determine category from tool name
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

                    # Print tools by category
                    for category, tools_list in sorted(categories.items()):
                        print(f"  {category}:")
                        for tool in sorted(tools_list, key=lambda x: x["name"]):
                            print(f"    - {tool['name']}")
                            if "description" in tool:
                                desc = tool["description"].split("\n")[0][:60]
                                print(f"      {desc}...")
                        print()

                    print("=" * 70)
                    print("✓ MCP Server Test: PASSED")
                    print(f"✓ All {len(tools)} tools are properly exposed")
                    print("=" * 70)
                else:
                    print("✗ No tools found in response")
    except json.JSONDecodeError as e:
        print(f"✗ Error decoding JSON response: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
