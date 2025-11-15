#!/usr/bin/env python3
"""Test uvx can run the package."""

import json
import subprocess
import sys

def test_uvx():
    """Test running with uvx."""
    print("Testing uvx installation and execution...")

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

    try:
        # Run with uvx
        print("\nRunning: /root/.local/bin/uvx --from . whatsapp-waha-mcp")
        process = subprocess.Popen(
            ["/root/.local/bin/uvx", "--from", ".", "whatsapp-waha-mcp"],
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

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                print(f"✅ uvx execution successful!")
                print(f"Server info: {response['result'].get('serverInfo', {})}")
                process.terminate()
                process.wait(timeout=5)
                return True

        print(f"❌ No valid response received")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}", file=sys.stderr)
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
    success = test_uvx()
    sys.exit(0 if success else 1)
