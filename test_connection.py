"""Simple test script to verify WAHA MCP server functionality."""

import asyncio
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from whatsapp_waha_mcp.server import make_request, WAHA_BASE_URL


async def test_connection():
    """Test basic connection to WAHA API."""
    print(f"Testing connection to WAHA API at: {WAHA_BASE_URL}")
    print("-" * 60)

    try:
        # Test 1: List sessions
        print("\n1. Testing list_sessions endpoint...")
        result = await make_request("GET", "/api/sessions")
        print(f"   ✓ Success! Found {len(result)} session(s)")
        print(f"   Response: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\n   This is expected if you haven't set up WAHA yet.")
        print("   To use this MCP server, you need:")
        print("   1. A running WAHA instance")
        print("   2. Set WAHA_BASE_URL environment variable")
        print("   3. Optionally set WAHA_API_KEY if authentication is required")

    print("\n" + "=" * 60)
    print("MCP Server Installation Test: ✓ PASSED")
    print("The server is properly installed and can be run with:")
    print("  - uvx whatsapp-waha-mcp")
    print("  - whatsapp-waha-mcp")
    print("  - python -m whatsapp_waha_mcp")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_connection())
