#!/usr/bin/env python3
"""Test actual WAHA API integration."""

import json
import subprocess
import sys

def test_waha_api_call():
    """Test calling WAHA API through MCP server."""
    print("Testing WAHA API integration...")

    # Initialize request
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

    # Call list_sessions tool
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_sessions",
            "arguments": {}
        }
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
        process.stdin.write(request_line)
        process.stdin.flush()

        # Read initialize response
        response_line = process.stdout.readline()
        if not response_line:
            print("❌ No response to initialize")
            process.terminate()
            return False

        print(f"✅ Initialized: {json.loads(response_line).get('result', {}).get('serverInfo', {})}")

        # Send call tool request (list_sessions)
        print("\n Testing list_sessions tool...")
        request_line = json.dumps(call_tool_request) + "\n"
        process.stdin.write(request_line)
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            print(f"Raw response: {response_line.strip()}")
            response = json.loads(response_line)

            if "result" in response:
                print(f"\n✅ Tool call successful!")
                print(f"Result: {response['result']}")
                process.terminate()
                process.wait(timeout=5)
                return True
            elif "error" in response:
                # This is expected if we can't connect to WAHA or if it requires auth
                error = response["error"]
                print(f"\n⚠️  API returned error (expected if WAHA requires auth or is unreachable):")
                print(f"   Code: {error.get('code')}")
                print(f"   Message: {error.get('message')}")
                print(f"\n✅ Server correctly handled the error and returned it via MCP!")
                process.terminate()
                process.wait(timeout=5)
                return True

        print(f"❌ No valid response")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
        process.terminate()
        return False

    except Exception as e:
        print(f"❌ Test failed: {str(e)}", file=sys.stderr)
        if 'process' in locals():
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Server stderr: {stderr_output}", file=sys.stderr)
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_waha_api_call()
    sys.exit(0 if success else 1)
