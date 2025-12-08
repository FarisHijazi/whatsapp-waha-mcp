#!/usr/bin/env python3
"""WAHA MCP Server - Minimal WhatsApp HTTP API Integration"""

import os
import logging
import ssl
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
BASE_URL = os.getenv("WAHA_BASE_URL", "https://waha.devlike.pro").rstrip("/")
API_KEY = os.getenv("WAHA_API_KEY", "")
VERIFY_SSL = os.getenv("WAHA_VERIFY_SSL", "true").lower() != "false"

# Create client with optional SSL verification
client = httpx.AsyncClient(timeout=30.0, verify=VERIFY_SSL)


async def api_call(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Make WAHA API request."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    if "json" in kwargs:
        headers["Content-Type"] = "application/json"
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
# MESSAGING (using WAHA's direct endpoint format)
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
        session: Session name (e.g., 'default')
        chat_id: Chat ID (e.g., '1234567890@c.us' for contact, '1234567890@g.us' for group)
        text: Message text
        reply_to: Optional message ID to reply to
    """
    data = {"session": session, "chatId": chat_id, "text": text}
    if reply_to:
        data["reply_to"] = reply_to
    return str(await api_call("POST", "/sendText", json=data))


@mcp.tool()
async def send_image(
    session: str,
    chat_id: str,
    url: str,
    caption: Optional[str] = None
) -> str:
    """Send an image.

    Args:
        session: Session name
        chat_id: Chat ID
        url: Image URL
        caption: Optional caption
    """
    data = {"session": session, "chatId": chat_id, "file": {"url": url}}
    if caption:
        data["caption"] = caption
    return str(await api_call("POST", "/sendImage", json=data))


@mcp.tool()
async def send_file(
    session: str,
    chat_id: str,
    url: str,
    filename: Optional[str] = None,
    caption: Optional[str] = None
) -> str:
    """Send a file/document.

    Args:
        session: Session name
        chat_id: Chat ID
        url: File URL
        filename: Optional filename
        caption: Optional caption
    """
    data = {"session": session, "chatId": chat_id, "file": {"url": url}}
    if filename:
        data["filename"] = filename
    if caption:
        data["caption"] = caption
    return str(await api_call("POST", "/sendFile", json=data))


@mcp.tool()
async def send_location(
    session: str,
    chat_id: str,
    latitude: float,
    longitude: float,
    title: Optional[str] = None
) -> str:
    """Send a location.

    Args:
        session: Session name
        chat_id: Chat ID
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        title: Optional location title
    """
    data = {"session": session, "chatId": chat_id, "latitude": latitude, "longitude": longitude}
    if title:
        data["title"] = title
    return str(await api_call("POST", "/sendLocation", json=data))


@mcp.tool()
async def react_to_message(
    session: str,
    chat_id: str,
    message_id: str,
    emoji: str
) -> str:
    """React to a message with an emoji.

    Args:
        session: Session name
        chat_id: Chat ID
        message_id: Message ID to react to
        emoji: Emoji to react with
    """
    data = {"session": session, "messageId": message_id, "reaction": emoji}
    return str(await api_call("PUT", f"/{session}/chats/{chat_id}/messages/{message_id}/reaction", json=data))


@mcp.tool()
async def send_seen(session: str, chat_id: str) -> str:
    """Mark messages in a chat as seen/read.

    Args:
        session: Session name
        chat_id: Chat ID to mark as seen
    """
    data = {"session": session, "chatId": chat_id}
    return str(await api_call("POST", "/sendSeen", json=data))


# ============================================================================
# CHATS
# ============================================================================

@mcp.tool()
async def list_chats(session: str, limit: int = 100) -> str:
    """List all chats.

    Args:
        session: Session name
        limit: Maximum number of chats to return (default: 100)
    """
    return str(await api_call("GET", f"/{session}/chats", params={"limit": limit}))


@mcp.tool()
async def get_messages(
    session: str,
    chat_id: str,
    limit: int = 100
) -> str:
    """Get messages from a chat.

    Args:
        session: Session name
        chat_id: Chat ID
        limit: Maximum messages to return (default: 100)
    """
    return str(await api_call("GET", f"/{session}/chats/{chat_id}/messages", params={"limit": limit}))


@mcp.tool()
async def delete_chat(session: str, chat_id: str) -> str:
    """Delete a chat.

    Args:
        session: Session name
        chat_id: Chat ID to delete
    """
    return str(await api_call("DELETE", f"/{session}/chats/{chat_id}"))


@mcp.tool()
async def archive_chat(session: str, chat_id: str) -> str:
    """Archive a chat.

    Args:
        session: Session name
        chat_id: Chat ID to archive
    """
    data = {"archive": True}
    return str(await api_call("PUT", f"/{session}/chats/{chat_id}/archive", json=data))


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
    return str(await api_call("POST", f"/{session}/groups", json=data))


@mcp.tool()
async def list_groups(session: str) -> str:
    """List all groups.

    Args:
        session: Session name
    """
    return str(await api_call("GET", f"/{session}/groups"))


@mcp.tool()
async def get_group(session: str, group_id: str) -> str:
    """Get group information.

    Args:
        session: Session name
        group_id: Group ID
    """
    return str(await api_call("GET", f"/{session}/groups/{group_id}"))


@mcp.tool()
async def add_participants(session: str, group_id: str, participants: str) -> str:
    """Add participants to a group.

    Args:
        session: Session name
        group_id: Group ID
        participants: Comma-separated phone numbers
    """
    participant_list = [f"{p.strip()}@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}
    return str(await api_call("POST", f"/{session}/groups/{group_id}/participants", json=data))


@mcp.tool()
async def remove_participants(session: str, group_id: str, participants: str) -> str:
    """Remove participants from a group.

    Args:
        session: Session name
        group_id: Group ID
        participants: Comma-separated phone numbers
    """
    participant_list = [f"{p.strip()}@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}
    return str(await api_call("DELETE", f"/{session}/groups/{group_id}/participants", json=data))


# ============================================================================
# CONTACTS
# ============================================================================

@mcp.tool()
async def list_contacts(session: str) -> str:
    """List all contacts.

    Args:
        session: Session name
    """
    return str(await api_call("GET", f"/{session}/contacts"))


@mcp.tool()
async def get_contact(session: str, contact_id: str) -> str:
    """Get contact information.

    Args:
        session: Session name
        contact_id: Contact ID
    """
    return str(await api_call("GET", f"/{session}/contacts/{contact_id}"))


@mcp.tool()
async def check_number(session: str, phone: str) -> str:
    """Check if a phone number exists on WhatsApp.

    Args:
        session: Session name
        phone: Phone number to check
    """
    data = {"session": session, "phone": phone}
    return str(await api_call("POST", "/checkNumberStatus", json=data))


# ============================================================================
# PRESENCE
# ============================================================================

@mcp.tool()
async def set_presence(session: str, online: bool) -> str:
    """Set presence status (online/offline).

    Args:
        session: Session name
        online: True for online, False for offline
    """
    data = {"presence": "online" if online else "offline"}
    return str(await api_call("POST", f"/{session}/presence", json=data))


@mcp.tool()
async def set_typing(session: str, chat_id: str, typing: bool) -> str:
    """Set typing indicator in a chat.

    Args:
        session: Session name
        chat_id: Chat ID
        typing: True to show typing, False to hide
    """
    data = {"chatId": chat_id, "typing": typing}
    return str(await api_call("POST", f"/{session}/typing", json=data))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the MCP server."""
    logger.info(f"Starting WAHA MCP Server (URL: {BASE_URL})")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
