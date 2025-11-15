#!/usr/bin/env python3
"""WAHA MCP Server - Minimal WhatsApp HTTP API Integration"""

import os
import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
import httpx

# Configure logging to stderr (required for STDIO MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("waha-mcp")

# Initialize
mcp = FastMCP("WhatsApp WAHA")
BASE_URL = os.getenv("WAHA_BASE_URL", "https://waha.devlike.pro")
API_KEY = os.getenv("WAHA_API_KEY", "")
client = httpx.AsyncClient(timeout=30.0)


async def api_call(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Make WAHA API request."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    url = f"{BASE_URL}/api{path}"

    try:
        response = await client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.status_code != 204 else {"success": True}
    except httpx.HTTPStatusError as e:
        raise Exception(f"API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


# ============================================================================
# SESSIONS
# ============================================================================

@mcp.tool()
async def list_sessions() -> str:
    """List all WhatsApp sessions."""
    return str(await api_call("GET", "/sessions"))


@mcp.tool()
async def start_session(name: str, config: Optional[str] = None) -> str:
    """Start a new WhatsApp session.

    Args:
        name: Session identifier
        config: Optional JSON config
    """
    data = {"name": name}
    if config:
        import json
        data["config"] = json.loads(config)
    return str(await api_call("POST", "/sessions", json=data))


@mcp.tool()
async def stop_session(name: str) -> str:
    """Stop a WhatsApp session."""
    return str(await api_call("DELETE", f"/sessions/{name}"))


@mcp.tool()
async def get_session(name: str) -> str:
    """Get session status and info."""
    return str(await api_call("GET", f"/sessions/{name}"))


# ============================================================================
# MESSAGING
# ============================================================================

@mcp.tool()
async def send_text(
    session: str,
    chat_id: str,
    text: str,
    reply_to: Optional[str] = None
) -> str:
    """Send a text message.

    Args:
        session: Session name
        chat_id: Chat ID (e.g., '1234567890@c.us' for contact, '1234567890@g.us' for group)
        text: Message text
        reply_to: Optional message ID to reply to
    """
    data = {"chatId": chat_id, "text": text}
    if reply_to:
        data["reply_to"] = reply_to
    return str(await api_call("POST", f"/sessions/{session}/messages/text", json=data))


@mcp.tool()
async def send_image(
    session: str,
    chat_id: str,
    url: str,
    caption: Optional[str] = None
) -> str:
    """Send an image."""
    data = {"chatId": chat_id, "file": {"url": url}}
    if caption:
        data["caption"] = caption
    return str(await api_call("POST", f"/sessions/{session}/messages/image", json=data))


@mcp.tool()
async def send_file(
    session: str,
    chat_id: str,
    url: str,
    filename: Optional[str] = None,
    caption: Optional[str] = None
) -> str:
    """Send a file/document."""
    data = {"chatId": chat_id, "file": {"url": url}}
    if filename:
        data["filename"] = filename
    if caption:
        data["caption"] = caption
    return str(await api_call("POST", f"/sessions/{session}/messages/document", json=data))


@mcp.tool()
async def send_location(
    session: str,
    chat_id: str,
    latitude: float,
    longitude: float,
    title: Optional[str] = None
) -> str:
    """Send a location."""
    data = {"chatId": chat_id, "latitude": latitude, "longitude": longitude}
    if title:
        data["title"] = title
    return str(await api_call("POST", f"/sessions/{session}/messages/location", json=data))


@mcp.tool()
async def react_to_message(
    session: str,
    chat_id: str,
    message_id: str,
    emoji: str
) -> str:
    """React to a message with an emoji."""
    data = {"chatId": chat_id, "messageId": message_id, "reaction": emoji}
    return str(await api_call("POST", f"/sessions/{session}/messages/reaction", json=data))


# ============================================================================
# CHATS
# ============================================================================

@mcp.tool()
async def list_chats(session: str, limit: int = 100) -> str:
    """List all chats."""
    return str(await api_call("GET", f"/sessions/{session}/chats", params={"limit": limit}))


@mcp.tool()
async def get_messages(
    session: str,
    chat_id: str,
    limit: int = 100
) -> str:
    """Get messages from a chat."""
    return str(await api_call("GET", f"/sessions/{session}/chats/{chat_id}/messages", params={"limit": limit}))


@mcp.tool()
async def delete_chat(session: str, chat_id: str) -> str:
    """Delete a chat."""
    return str(await api_call("DELETE", f"/sessions/{session}/chats/{chat_id}"))


@mcp.tool()
async def archive_chat(session: str, chat_id: str) -> str:
    """Archive a chat."""
    data = {"chatId": chat_id, "archive": True}
    return str(await api_call("PUT", f"/sessions/{session}/chats/{chat_id}/archive", json=data))


# ============================================================================
# GROUPS
# ============================================================================

@mcp.tool()
async def create_group(session: str, name: str, participants: str) -> str:
    """Create a WhatsApp group.

    Args:
        session: Session name
        name: Group name
        participants: Comma-separated phone numbers (e.g., "1234567890,0987654321")
    """
    participant_list = [f"{p.strip()}@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"name": name, "participants": participant_list}
    return str(await api_call("POST", f"/sessions/{session}/groups", json=data))


@mcp.tool()
async def list_groups(session: str) -> str:
    """List all groups."""
    return str(await api_call("GET", f"/sessions/{session}/groups"))


@mcp.tool()
async def get_group(session: str, group_id: str) -> str:
    """Get group information."""
    return str(await api_call("GET", f"/sessions/{session}/groups/{group_id}"))


@mcp.tool()
async def add_participants(session: str, group_id: str, participants: str) -> str:
    """Add participants to a group.

    Args:
        participants: Comma-separated phone numbers
    """
    participant_list = [f"{p.strip()}@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}
    return str(await api_call("POST", f"/sessions/{session}/groups/{group_id}/participants", json=data))


@mcp.tool()
async def remove_participants(session: str, group_id: str, participants: str) -> str:
    """Remove participants from a group.

    Args:
        participants: Comma-separated phone numbers
    """
    participant_list = [f"{p.strip()}@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}
    return str(await api_call("DELETE", f"/sessions/{session}/groups/{group_id}/participants", json=data))


# ============================================================================
# CONTACTS
# ============================================================================

@mcp.tool()
async def list_contacts(session: str) -> str:
    """List all contacts."""
    return str(await api_call("GET", f"/sessions/{session}/contacts"))


@mcp.tool()
async def get_contact(session: str, contact_id: str) -> str:
    """Get contact information."""
    return str(await api_call("GET", f"/sessions/{session}/contacts/{contact_id}"))


@mcp.tool()
async def check_number(session: str, phone: str) -> str:
    """Check if a phone number exists on WhatsApp."""
    data = {"phone": phone}
    return str(await api_call("POST", f"/sessions/{session}/contacts/check", json=data))


# ============================================================================
# PRESENCE
# ============================================================================

@mcp.tool()
async def set_presence(session: str, online: bool) -> str:
    """Set presence status (online/offline)."""
    data = {"presence": "online" if online else "offline"}
    return str(await api_call("POST", f"/sessions/{session}/presence", json=data))


@mcp.tool()
async def set_typing(session: str, chat_id: str, typing: bool) -> str:
    """Set typing indicator in a chat."""
    data = {"chatId": chat_id, "typing": typing}
    return str(await api_call("POST", f"/sessions/{session}/typing", json=data))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the MCP server."""
    logger.info(f"Starting WAHA MCP Server (URL: {BASE_URL})")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
