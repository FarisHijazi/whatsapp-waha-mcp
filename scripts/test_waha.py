#!/usr/bin/env python3
"""
WAHA API Connection Test Script

Test your WAHA server connectivity before using the MCP server.

Usage:
    python scripts/test_waha.py

    # Or with custom settings:
    WAHA_BASE_URL=https://your-server.com WAHA_API_KEY=your-key python scripts/test_waha.py

Environment Variables:
    WAHA_BASE_URL - WAHA server URL (required)
    WAHA_API_KEY - API key for authentication (optional)
    WAHA_CHAT_ID - Chat ID for test message (optional)
    WAHA_VERIFY_SSL - Set to 'false' to disable SSL verification
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

# Load .env file if present
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

BASE_URL = os.getenv("WAHA_BASE_URL", "").rstrip("/")
API_KEY = os.getenv("WAHA_API_KEY", "")
CHAT_ID = os.getenv("WAHA_CHAT_ID", "")
VERIFY_SSL = os.getenv("WAHA_VERIFY_SSL", "true").lower() != "false"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def success(msg: str) -> str:
    return f"{Colors.GREEN}[OK]{Colors.RESET} {msg}"


def error(msg: str) -> str:
    return f"{Colors.RED}[FAIL]{Colors.RESET} {msg}"


def info(msg: str) -> str:
    return f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}"


def warn(msg: str) -> str:
    return f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}"


async def test_waha():
    """Run WAHA API connectivity tests."""

    print(f"\n{Colors.BOLD}WAHA API Connection Test{Colors.RESET}")
    print("=" * 50)

    # Check configuration
    if not BASE_URL:
        print(error("WAHA_BASE_URL not set!"))
        print(info("Set it in .env file or as environment variable"))
        return False

    print(info(f"Server URL: {BASE_URL}"))
    print(info(f"API Key: {'***' + API_KEY[-4:] if len(API_KEY) > 4 else '(not set)'}"))
    print(info(f"SSL Verify: {VERIFY_SSL}"))
    if CHAT_ID:
        print(info(f"Test Chat ID: {CHAT_ID}"))
    print()

    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    headers["Content-Type"] = "application/json"

    async with httpx.AsyncClient(timeout=30.0, verify=VERIFY_SSL) as client:
        tests_passed = 0
        tests_failed = 0
        session_name = None

        # Test 1: Basic connectivity
        print(f"{Colors.BOLD}Test 1: Basic Connectivity{Colors.RESET}")
        try:
            # Try the version endpoint or sessions
            resp = await client.get(f"{BASE_URL}/api/sessions", headers=headers)
            if resp.status_code == 200:
                sessions = resp.json()
                print(success(f"Connected to WAHA server"))
                print(info(f"Found {len(sessions)} session(s)"))
                if sessions:
                    session_name = sessions[0].get("name", sessions[0]) if isinstance(sessions[0], dict) else sessions[0]
                    print(info(f"Available sessions: {[s.get('name', s) if isinstance(s, dict) else s for s in sessions]}"))
                tests_passed += 1
            elif resp.status_code == 401:
                print(error("Authentication failed - check your WAHA_API_KEY"))
                tests_failed += 1
            elif resp.status_code == 404:
                print(error(f"Endpoint not found - is WAHA running at {BASE_URL}?"))
                print(info("Make sure you're pointing to the WAHA API server, not the docs site"))
                tests_failed += 1
            else:
                print(error(f"Unexpected response: {resp.status_code}"))
                print(info(f"Response: {resp.text[:200]}"))
                tests_failed += 1
        except httpx.ConnectError as e:
            print(error(f"Connection failed: {e}"))
            print(info("Check if the WAHA server is running and accessible"))
            tests_failed += 1
        except Exception as e:
            print(error(f"Error: {e}"))
            tests_failed += 1
        print()

        # Test 2: Session status (if we have a session)
        if session_name:
            print(f"{Colors.BOLD}Test 2: Session Status{Colors.RESET}")
            try:
                resp = await client.get(f"{BASE_URL}/api/sessions/{session_name}", headers=headers)
                if resp.status_code == 200:
                    session_info = resp.json()
                    status = session_info.get("status", "unknown")
                    print(success(f"Session '{session_name}' status: {status}"))
                    if status == "WORKING":
                        print(info("Session is connected and ready"))
                    elif status == "SCAN_QR_CODE":
                        print(warn("Session needs QR code scan"))
                    elif status == "STOPPED":
                        print(warn("Session is stopped - try starting it"))
                    tests_passed += 1
                else:
                    print(error(f"Failed to get session status: {resp.status_code}"))
                    tests_failed += 1
            except Exception as e:
                print(error(f"Error: {e}"))
                tests_failed += 1
            print()

        # Test 3: List chats (if session is working)
        if session_name:
            print(f"{Colors.BOLD}Test 3: List Chats{Colors.RESET}")
            try:
                resp = await client.get(f"{BASE_URL}/api/{session_name}/chats", headers=headers, params={"limit": 5})
                if resp.status_code == 200:
                    chats = resp.json()
                    print(success(f"Retrieved {len(chats)} chat(s)"))
                    for chat in chats[:3]:
                        name = chat.get("name", chat.get("id", "unknown"))
                        chat_id = chat.get("id", "")
                        print(info(f"  - {name} ({chat_id})"))
                    tests_passed += 1
                elif resp.status_code == 422:
                    print(warn("Session not ready - waiting for authentication"))
                    tests_failed += 1
                else:
                    print(error(f"Failed to list chats: {resp.status_code}"))
                    tests_failed += 1
            except Exception as e:
                print(error(f"Error: {e}"))
                tests_failed += 1
            print()

        # Test 4: Send test message (optional)
        if session_name and CHAT_ID:
            print(f"{Colors.BOLD}Test 4: Send Test Message{Colors.RESET}")
            try:
                data = {
                    "session": session_name,
                    "chatId": CHAT_ID,
                    "text": "Test message from WAHA MCP Server"
                }
                resp = await client.post(f"{BASE_URL}/api/sendText", headers=headers, json=data)
                if resp.status_code in [200, 201]:
                    result = resp.json()
                    print(success("Message sent successfully!"))
                    msg_id = result.get("id", result.get("key", {}).get("id", "unknown"))
                    print(info(f"Message ID: {msg_id}"))
                    tests_passed += 1
                elif resp.status_code == 422:
                    print(warn("Session not ready - authenticate first"))
                    tests_failed += 1
                else:
                    print(error(f"Failed to send message: {resp.status_code}"))
                    print(info(f"Response: {resp.text[:200]}"))
                    tests_failed += 1
            except Exception as e:
                print(error(f"Error: {e}"))
                tests_failed += 1
            print()
        elif CHAT_ID and not session_name:
            print(warn("Skipping message test - no active session"))

        # Summary
        print("=" * 50)
        print(f"{Colors.BOLD}Summary{Colors.RESET}")
        total = tests_passed + tests_failed
        if tests_failed == 0 and tests_passed > 0:
            print(success(f"All {tests_passed} tests passed!"))
            print(info("Your WAHA MCP server should work correctly."))
            return True
        elif tests_passed > 0:
            print(warn(f"{tests_passed}/{total} tests passed, {tests_failed} failed"))
            return False
        else:
            print(error(f"All {tests_failed} tests failed"))
            print()
            print(f"{Colors.BOLD}Troubleshooting:{Colors.RESET}")
            print("1. Verify WAHA_BASE_URL points to a running WAHA instance")
            print("2. Check if the server is accessible (try curl)")
            print("3. Verify WAHA_API_KEY is correct")
            print("4. Check if a session exists and is authenticated")
            return False


def main():
    """Entry point."""
    print(f"\n{Colors.BLUE}WAHA MCP Server - Connection Tester{Colors.RESET}")

    if not BASE_URL:
        print(f"\n{Colors.RED}Error:{Colors.RESET} WAHA_BASE_URL not configured!")
        print("\nPlease set your WAHA server URL:")
        print("  1. Create a .env file with: WAHA_BASE_URL=https://your-server.com")
        print("  2. Or export: export WAHA_BASE_URL=https://your-server.com")
        sys.exit(1)

    success = asyncio.run(test_waha())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
