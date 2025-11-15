#!/usr/bin/env python3
"""Test script to verify MCP server functionality."""

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server by sending an initialize request."""
    print("Testing WAHA MCP Server...")

    # Initialize request as per MCP protocol
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

    # List tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    try:
        # Start the MCP server
        process = subprocess.Popen(
            [".venv/bin/whatsapp-waha-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={"WAHA_BASE_URL": "https://waha.devlike.pro"}
        )

        # Send initialize request
        request_line = json.dumps(initialize_request) + "\n"
        print(f"\nSending: {request_line.strip()}")

        process.stdin.write(request_line)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            print(f"Received: {response_line.strip()}")
            response = json.loads(response_line)
            print(f"\n✅ Server initialized successfully!")
            print(f"Server capabilities: {json.dumps(response.get('result', {}), indent=2)}")

        # Send list tools request
        request_line = json.dumps(list_tools_request) + "\n"
        print(f"\nSending: {request_line.strip()}")

        process.stdin.write(request_line)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            print(f"Received: {response_line.strip()}")
            response = json.loads(response_line)
            tools = response.get('result', {}).get('tools', [])
            print(f"\n✅ Server has {len(tools)} tools available!")

            # Print first few tools
            print("\nSample tools:")
            for tool in tools[:5]:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")

            if len(tools) > 5:
                print(f"  ... and {len(tools) - 5} more tools")

        # Terminate the process
        process.terminate()
        process.wait(timeout=5)

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}", file=sys.stderr)
        if 'process' in locals():
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Server stderr: {stderr_output}", file=sys.stderr)
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
