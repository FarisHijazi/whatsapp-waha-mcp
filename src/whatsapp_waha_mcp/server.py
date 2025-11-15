#!/usr/bin/env python3
"""WAHA MCP Server - WhatsApp HTTP API MCP Integration

This MCP server provides comprehensive access to WAHA (WhatsApp HTTP API) features.
"""

import os
import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
import httpx

# Configure logging to stderr (critical for STDIO-based MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Logs to stderr by default
)
logger = logging.getLogger("whatsapp-waha-mcp")

# Initialize FastMCP server
mcp = FastMCP("WhatsApp WAHA")

# Global configuration
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "https://waha.devlike.pro")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")

# HTTP client with timeout
client = httpx.AsyncClient(timeout=30.0)


async def make_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    session: Optional[str] = None
) -> dict[str, Any]:
    """Make HTTP request to WAHA API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        endpoint: API endpoint path
        data: JSON data for request body
        params: Query parameters
        session: Session name for session-specific endpoints

    Returns:
        Response data as dictionary

    Raises:
        Exception: On API errors
    """
    url = f"{WAHA_BASE_URL}/api{endpoint}"
    headers = {}

    if WAHA_API_KEY:
        headers["X-API-Key"] = WAHA_API_KEY

    # Add session to path if needed
    if session and "{session}" in endpoint:
        endpoint = endpoint.replace("{session}", session)
        url = f"{WAHA_BASE_URL}/api{endpoint}"

    logger.info(f"Making {method} request to {url}")

    try:
        response = await client.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {"success": True, "message": "Operation completed successfully"}

        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise Exception(f"Request failed: {str(e)}")


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@mcp.tool()
async def list_sessions() -> str:
    """List all WhatsApp sessions.

    Returns:
        JSON string with list of all sessions and their status
    """
    result = await make_request("GET", "/sessions")
    return str(result)


@mcp.tool()
async def start_session(
    name: str,
    config: Optional[str] = None
) -> str:
    """Start a new WhatsApp session.

    Args:
        name: Unique session name/identifier
        config: Optional JSON configuration string for the session

    Returns:
        Session status and QR code information
    """
    data = {"name": name}
    if config:
        import json
        data["config"] = json.loads(config)

    result = await make_request("POST", "/sessions", data=data)
    return str(result)


@mcp.tool()
async def stop_session(name: str) -> str:
    """Stop a WhatsApp session.

    Args:
        name: Session name to stop

    Returns:
        Confirmation message
    """
    result = await make_request("DELETE", f"/sessions/{name}")
    return str(result)


@mcp.tool()
async def get_session_status(name: str) -> str:
    """Get status of a WhatsApp session.

    Args:
        name: Session name

    Returns:
        Session status information
    """
    result = await make_request("GET", f"/sessions/{name}")
    return str(result)


@mcp.tool()
async def restart_session(name: str) -> str:
    """Restart a WhatsApp session.

    Args:
        name: Session name to restart

    Returns:
        Restart confirmation
    """
    result = await make_request("POST", f"/sessions/{name}/restart")
    return str(result)


@mcp.tool()
async def logout_session(name: str) -> str:
    """Logout from a WhatsApp session.

    Args:
        name: Session name to logout

    Returns:
        Logout confirmation
    """
    result = await make_request("POST", f"/sessions/{name}/logout")
    return str(result)


# ============================================================================
# MESSAGING
# ============================================================================

@mcp.tool()
async def send_text_message(
    session: str,
    chat_id: str,
    text: str,
    reply_to: Optional[str] = None
) -> str:
    """Send a text message.

    Args:
        session: Session name
        chat_id: Chat ID (phone number with @c.us or group ID with @g.us)
        text: Message text
        reply_to: Optional message ID to reply to

    Returns:
        Message send confirmation with message ID
    """
    data = {
        "chatId": chat_id,
        "text": text
    }
    if reply_to:
        data["reply_to"] = reply_to

    result = await make_request("POST", f"/sessions/{session}/messages/text", data=data)
    return str(result)


@mcp.tool()
async def send_image(
    session: str,
    chat_id: str,
    url: str,
    caption: Optional[str] = None
) -> str:
    """Send an image message.

    Args:
        session: Session name
        chat_id: Chat ID
        url: Image URL
        caption: Optional image caption

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "file": {"url": url}
    }
    if caption:
        data["caption"] = caption

    result = await make_request("POST", f"/sessions/{session}/messages/image", data=data)
    return str(result)


@mcp.tool()
async def send_video(
    session: str,
    chat_id: str,
    url: str,
    caption: Optional[str] = None
) -> str:
    """Send a video message.

    Args:
        session: Session name
        chat_id: Chat ID
        url: Video URL
        caption: Optional video caption

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "file": {"url": url}
    }
    if caption:
        data["caption"] = caption

    result = await make_request("POST", f"/sessions/{session}/messages/video", data=data)
    return str(result)


@mcp.tool()
async def send_document(
    session: str,
    chat_id: str,
    url: str,
    filename: Optional[str] = None,
    caption: Optional[str] = None
) -> str:
    """Send a document/file message.

    Args:
        session: Session name
        chat_id: Chat ID
        url: Document URL
        filename: Optional filename
        caption: Optional caption

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "file": {"url": url}
    }
    if filename:
        data["filename"] = filename
    if caption:
        data["caption"] = caption

    result = await make_request("POST", f"/sessions/{session}/messages/document", data=data)
    return str(result)


@mcp.tool()
async def send_audio(
    session: str,
    chat_id: str,
    url: str
) -> str:
    """Send an audio message.

    Args:
        session: Session name
        chat_id: Chat ID
        url: Audio file URL

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "file": {"url": url}
    }

    result = await make_request("POST", f"/sessions/{session}/messages/audio", data=data)
    return str(result)


@mcp.tool()
async def send_location(
    session: str,
    chat_id: str,
    latitude: float,
    longitude: float,
    title: Optional[str] = None
) -> str:
    """Send a location message.

    Args:
        session: Session name
        chat_id: Chat ID
        latitude: Location latitude
        longitude: Location longitude
        title: Optional location title

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "latitude": latitude,
        "longitude": longitude
    }
    if title:
        data["title"] = title

    result = await make_request("POST", f"/sessions/{session}/messages/location", data=data)
    return str(result)


@mcp.tool()
async def send_contact(
    session: str,
    chat_id: str,
    contact_id: str
) -> str:
    """Send a contact card.

    Args:
        session: Session name
        chat_id: Chat ID
        contact_id: Contact ID to share

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "contactId": contact_id
    }

    result = await make_request("POST", f"/sessions/{session}/messages/contact", data=data)
    return str(result)


@mcp.tool()
async def send_poll(
    session: str,
    chat_id: str,
    title: str,
    options: str,
    multiple_answers: bool = False
) -> str:
    """Send a poll.

    Args:
        session: Session name
        chat_id: Chat ID
        title: Poll question/title
        options: Comma-separated poll options (e.g., "Option 1,Option 2,Option 3")
        multiple_answers: Allow multiple answers selection

    Returns:
        Message send confirmation
    """
    data = {
        "chatId": chat_id,
        "poll": {
            "name": title,
            "options": [opt.strip() for opt in options.split(",")],
            "multipleAnswers": multiple_answers
        }
    }

    result = await make_request("POST", f"/sessions/{session}/messages/poll", data=data)
    return str(result)


@mcp.tool()
async def react_to_message(
    session: str,
    chat_id: str,
    message_id: str,
    reaction: str
) -> str:
    """React to a message with an emoji.

    Args:
        session: Session name
        chat_id: Chat ID
        message_id: Message ID to react to
        reaction: Emoji reaction

    Returns:
        Reaction confirmation
    """
    data = {
        "chatId": chat_id,
        "messageId": message_id,
        "reaction": reaction
    }

    result = await make_request("POST", f"/sessions/{session}/messages/reaction", data=data)
    return str(result)


# ============================================================================
# CHATS MANAGEMENT
# ============================================================================

@mcp.tool()
async def list_chats(
    session: str,
    limit: int = 100,
    offset: int = 0
) -> str:
    """List all chats.

    Args:
        session: Session name
        limit: Maximum number of chats to return (default: 100)
        offset: Offset for pagination (default: 0)

    Returns:
        List of chats
    """
    params = {"limit": limit, "offset": offset}
    result = await make_request("GET", f"/sessions/{session}/chats", params=params)
    return str(result)


@mcp.tool()
async def get_chat_messages(
    session: str,
    chat_id: str,
    limit: int = 100
) -> str:
    """Get messages from a chat.

    Args:
        session: Session name
        chat_id: Chat ID
        limit: Maximum number of messages to return (default: 100)

    Returns:
        List of messages from the chat
    """
    params = {"limit": limit}
    result = await make_request("GET", f"/sessions/{session}/chats/{chat_id}/messages", params=params)
    return str(result)


@mcp.tool()
async def delete_chat(
    session: str,
    chat_id: str
) -> str:
    """Delete a chat.

    Args:
        session: Session name
        chat_id: Chat ID to delete

    Returns:
        Deletion confirmation
    """
    result = await make_request("DELETE", f"/sessions/{session}/chats/{chat_id}")
    return str(result)


@mcp.tool()
async def clear_chat_messages(
    session: str,
    chat_id: str
) -> str:
    """Clear all messages from a chat.

    Args:
        session: Session name
        chat_id: Chat ID to clear

    Returns:
        Clear confirmation
    """
    result = await make_request("DELETE", f"/sessions/{session}/chats/{chat_id}/messages")
    return str(result)


@mcp.tool()
async def archive_chat(
    session: str,
    chat_id: str
) -> str:
    """Archive a chat.

    Args:
        session: Session name
        chat_id: Chat ID to archive

    Returns:
        Archive confirmation
    """
    data = {"chatId": chat_id, "archive": True}
    result = await make_request("PUT", f"/sessions/{session}/chats/{chat_id}/archive", data=data)
    return str(result)


@mcp.tool()
async def unarchive_chat(
    session: str,
    chat_id: str
) -> str:
    """Unarchive a chat.

    Args:
        session: Session name
        chat_id: Chat ID to unarchive

    Returns:
        Unarchive confirmation
    """
    data = {"chatId": chat_id, "archive": False}
    result = await make_request("PUT", f"/sessions/{session}/chats/{chat_id}/archive", data=data)
    return str(result)


# ============================================================================
# GROUPS MANAGEMENT
# ============================================================================

@mcp.tool()
async def create_group(
    session: str,
    name: str,
    participants: str
) -> str:
    """Create a new WhatsApp group.

    Args:
        session: Session name
        name: Group name
        participants: Comma-separated list of participant phone numbers

    Returns:
        Created group information
    """
    participant_list = [p.strip() + "@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {
        "name": name,
        "participants": participant_list
    }

    result = await make_request("POST", f"/sessions/{session}/groups", data=data)
    return str(result)


@mcp.tool()
async def list_groups(session: str) -> str:
    """List all groups.

    Args:
        session: Session name

    Returns:
        List of all groups
    """
    result = await make_request("GET", f"/sessions/{session}/groups")
    return str(result)


@mcp.tool()
async def get_group_info(
    session: str,
    group_id: str
) -> str:
    """Get information about a group.

    Args:
        session: Session name
        group_id: Group ID

    Returns:
        Group information including participants
    """
    result = await make_request("GET", f"/sessions/{session}/groups/{group_id}")
    return str(result)


@mcp.tool()
async def add_group_participants(
    session: str,
    group_id: str,
    participants: str
) -> str:
    """Add participants to a group.

    Args:
        session: Session name
        group_id: Group ID
        participants: Comma-separated list of participant phone numbers

    Returns:
        Add operation result
    """
    participant_list = [p.strip() + "@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}

    result = await make_request("POST", f"/sessions/{session}/groups/{group_id}/participants", data=data)
    return str(result)


@mcp.tool()
async def remove_group_participants(
    session: str,
    group_id: str,
    participants: str
) -> str:
    """Remove participants from a group.

    Args:
        session: Session name
        group_id: Group ID
        participants: Comma-separated list of participant phone numbers

    Returns:
        Remove operation result
    """
    participant_list = [p.strip() + "@c.us" if "@" not in p else p.strip()
                       for p in participants.split(",")]
    data = {"participants": participant_list}

    result = await make_request("DELETE", f"/sessions/{session}/groups/{group_id}/participants", data=data)
    return str(result)


@mcp.tool()
async def leave_group(
    session: str,
    group_id: str
) -> str:
    """Leave a group.

    Args:
        session: Session name
        group_id: Group ID to leave

    Returns:
        Leave confirmation
    """
    result = await make_request("POST", f"/sessions/{session}/groups/{group_id}/leave")
    return str(result)


@mcp.tool()
async def update_group_subject(
    session: str,
    group_id: str,
    subject: str
) -> str:
    """Update group name/subject.

    Args:
        session: Session name
        group_id: Group ID
        subject: New group name

    Returns:
        Update confirmation
    """
    data = {"subject": subject}
    result = await make_request("PUT", f"/sessions/{session}/groups/{group_id}/subject", data=data)
    return str(result)


@mcp.tool()
async def update_group_description(
    session: str,
    group_id: str,
    description: str
) -> str:
    """Update group description.

    Args:
        session: Session name
        group_id: Group ID
        description: New group description

    Returns:
        Update confirmation
    """
    data = {"description": description}
    result = await make_request("PUT", f"/sessions/{session}/groups/{group_id}/description", data=data)
    return str(result)


# ============================================================================
# CONTACTS MANAGEMENT
# ============================================================================

@mcp.tool()
async def list_contacts(session: str) -> str:
    """List all contacts.

    Args:
        session: Session name

    Returns:
        List of all contacts
    """
    result = await make_request("GET", f"/sessions/{session}/contacts")
    return str(result)


@mcp.tool()
async def get_contact(
    session: str,
    contact_id: str
) -> str:
    """Get contact information.

    Args:
        session: Session name
        contact_id: Contact ID (phone number)

    Returns:
        Contact information
    """
    result = await make_request("GET", f"/sessions/{session}/contacts/{contact_id}")
    return str(result)


@mcp.tool()
async def check_number_exists(
    session: str,
    phone: str
) -> str:
    """Check if a phone number exists on WhatsApp.

    Args:
        session: Session name
        phone: Phone number to check

    Returns:
        Existence check result
    """
    data = {"phone": phone}
    result = await make_request("POST", f"/sessions/{session}/contacts/check", data=data)
    return str(result)


@mcp.tool()
async def block_contact(
    session: str,
    contact_id: str
) -> str:
    """Block a contact.

    Args:
        session: Session name
        contact_id: Contact ID to block

    Returns:
        Block confirmation
    """
    data = {"contactId": contact_id}
    result = await make_request("POST", f"/sessions/{session}/contacts/block", data=data)
    return str(result)


@mcp.tool()
async def unblock_contact(
    session: str,
    contact_id: str
) -> str:
    """Unblock a contact.

    Args:
        session: Session name
        contact_id: Contact ID to unblock

    Returns:
        Unblock confirmation
    """
    data = {"contactId": contact_id}
    result = await make_request("POST", f"/sessions/{session}/contacts/unblock", data=data)
    return str(result)


# ============================================================================
# PRESENCE MANAGEMENT
# ============================================================================

@mcp.tool()
async def set_presence_online(session: str) -> str:
    """Set presence as online.

    Args:
        session: Session name

    Returns:
        Presence update confirmation
    """
    data = {"presence": "online"}
    result = await make_request("POST", f"/sessions/{session}/presence", data=data)
    return str(result)


@mcp.tool()
async def set_presence_offline(session: str) -> str:
    """Set presence as offline.

    Args:
        session: Session name

    Returns:
        Presence update confirmation
    """
    data = {"presence": "offline"}
    result = await make_request("POST", f"/sessions/{session}/presence", data=data)
    return str(result)


@mcp.tool()
async def start_typing(
    session: str,
    chat_id: str
) -> str:
    """Start typing indicator in a chat.

    Args:
        session: Session name
        chat_id: Chat ID

    Returns:
        Typing start confirmation
    """
    data = {"chatId": chat_id, "typing": True}
    result = await make_request("POST", f"/sessions/{session}/typing", data=data)
    return str(result)


@mcp.tool()
async def stop_typing(
    session: str,
    chat_id: str
) -> str:
    """Stop typing indicator in a chat.

    Args:
        session: Session name
        chat_id: Chat ID

    Returns:
        Typing stop confirmation
    """
    data = {"chatId": chat_id, "typing": False}
    result = await make_request("POST", f"/sessions/{session}/typing", data=data)
    return str(result)


# ============================================================================
# STATUS/STORIES
# ============================================================================

@mcp.tool()
async def send_text_status(
    session: str,
    text: str,
    background_color: str = "#000000"
) -> str:
    """Send a text status/story.

    Args:
        session: Session name
        text: Status text
        background_color: Background color in hex format (default: #000000)

    Returns:
        Status send confirmation
    """
    data = {
        "text": text,
        "backgroundColor": background_color
    }
    result = await make_request("POST", f"/sessions/{session}/status/text", data=data)
    return str(result)


@mcp.tool()
async def send_image_status(
    session: str,
    url: str,
    caption: Optional[str] = None
) -> str:
    """Send an image status/story.

    Args:
        session: Session name
        url: Image URL
        caption: Optional caption

    Returns:
        Status send confirmation
    """
    data = {"file": {"url": url}}
    if caption:
        data["caption"] = caption

    result = await make_request("POST", f"/sessions/{session}/status/image", data=data)
    return str(result)


# ============================================================================
# LABELS (WhatsApp Business)
# ============================================================================

@mcp.tool()
async def list_labels(session: str) -> str:
    """List all labels (WhatsApp Business).

    Args:
        session: Session name

    Returns:
        List of all labels
    """
    result = await make_request("GET", f"/sessions/{session}/labels")
    return str(result)


@mcp.tool()
async def create_label(
    session: str,
    name: str,
    color: Optional[str] = None
) -> str:
    """Create a new label (WhatsApp Business).

    Args:
        session: Session name
        name: Label name
        color: Optional label color

    Returns:
        Created label information
    """
    data = {"name": name}
    if color:
        data["color"] = color

    result = await make_request("POST", f"/sessions/{session}/labels", data=data)
    return str(result)


@mcp.tool()
async def assign_label_to_chat(
    session: str,
    chat_id: str,
    label_id: str
) -> str:
    """Assign a label to a chat (WhatsApp Business).

    Args:
        session: Session name
        chat_id: Chat ID
        label_id: Label ID to assign

    Returns:
        Assignment confirmation
    """
    data = {"labelId": label_id}
    result = await make_request("PUT", f"/sessions/{session}/chats/{chat_id}/labels", data=data)
    return str(result)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    logger.info("Starting WhatsApp WAHA MCP Server")
    logger.info(f"WAHA Base URL: {WAHA_BASE_URL}")

    # Run the MCP server using STDIO transport
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
