"""WhatsApp WAHA MCP Server - Minimal implementation with full features."""

import json
import logging
import os
import sys
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (CRITICAL for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("whatsapp-waha-mcp")

# Initialize FastMCP server
mcp = FastMCP("whatsapp-waha")

# Configuration
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "https://waha.devlike.pro")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
http_client: Optional[httpx.AsyncClient] = None


def get_headers() -> dict[str, str]:
    """Get headers for WAHA API requests."""
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY
    return headers


async def get_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)
    return http_client


async def api_call(method: str, path: str, data: Optional[dict] = None, params: Optional[dict] = None) -> str:
    """Make API request and return JSON string."""
    client = await get_client()
    url = f"{WAHA_BASE_URL}{path}"

    try:
        response = await client.request(method, url, headers=get_headers(), json=data, params=params)
        response.raise_for_status()
        return str(response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
        raise Exception(f"WAHA API error ({e.response.status_code}): {e.response.text[:100]}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise


def parse_json_param(param: Optional[str], param_name: str) -> Any:
    """Parse JSON parameter safely."""
    if not param:
        return None
    try:
        return json.loads(param)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in {param_name}")


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@mcp.tool()
async def list_sessions(all: bool = False) -> str:
    """List all WhatsApp sessions."""
    return await api_call("GET", "/api/sessions", params={"all": "true"} if all else None)


@mcp.tool()
async def get_session(session: str = "default") -> str:
    """Get session details and status."""
    return await api_call("GET", f"/api/sessions/{session}")


@mcp.tool()
async def start_session(session: str = "default", config: Optional[str] = None) -> str:
    """Start WhatsApp session. config: Optional JSON string with session configuration."""
    data = {"name": session}
    if config:
        data.update(parse_json_param(config, "config"))
    return await api_call("POST", "/api/sessions/start", data=data)


@mcp.tool()
async def stop_session(session: str = "default", logout: bool = False) -> str:
    """Stop WhatsApp session. logout: Logout before stopping."""
    if logout:
        await api_call("POST", f"/api/sessions/{session}/logout")
    return await api_call("POST", f"/api/sessions/{session}/stop")


@mcp.tool()
async def restart_session(session: str = "default") -> str:
    """Restart WhatsApp session."""
    return await api_call("POST", f"/api/sessions/{session}/restart")


@mcp.tool()
async def get_qr_code(session: str = "default", format: str = "image") -> str:
    """Get QR code for authentication. format: 'image' or 'raw'."""
    return await api_call("GET", f"/api/{session}/auth/qr", params={"format": format})


@mcp.tool()
async def request_pairing_code(session: str = "default", phone: str = "") -> str:
    """Request pairing code for authentication (alternative to QR)."""
    return await api_call("POST", f"/api/{session}/auth/request-code", data={"phoneNumber": phone})


@mcp.tool()
async def get_me(session: str = "default") -> str:
    """Get authenticated WhatsApp account information."""
    return await api_call("GET", f"/api/{session}/me")


# ============================================================================
# MESSAGING
# ============================================================================

async def send_message(endpoint: str, chat_id: str, session: str, **kwargs) -> str:
    """Generic send message helper."""
    data = {"chatId": chat_id, "session": session, **kwargs}
    return await api_call("POST", f"/api/{endpoint}", data=data)


@mcp.tool()
async def send_text(chat_id: str, text: str, session: str = "default",
                   reply_to: Optional[str] = None, mentions: Optional[str] = None) -> str:
    """Send text message. mentions: JSON array of phone numbers to mention."""
    data = {"text": text}
    if reply_to:
        data["reply_to"] = reply_to
    if mentions:
        data["mentions"] = parse_json_param(mentions, "mentions")
    return await send_message("sendText", chat_id, session, **data)


@mcp.tool()
async def send_image(chat_id: str, url: str, session: str = "default",
                    caption: Optional[str] = None, reply_to: Optional[str] = None) -> str:
    """Send image message."""
    data = {"file": {"url": url}}
    if caption:
        data["caption"] = caption
    if reply_to:
        data["reply_to"] = reply_to
    return await send_message("sendImage", chat_id, session, **data)


@mcp.tool()
async def send_file(chat_id: str, url: str, session: str = "default",
                   caption: Optional[str] = None, filename: Optional[str] = None) -> str:
    """Send file/document message."""
    data = {"file": {"url": url}}
    if caption:
        data["caption"] = caption
    if filename:
        data["filename"] = filename
    return await send_message("sendFile", chat_id, session, **data)


@mcp.tool()
async def send_video(chat_id: str, url: str, session: str = "default", caption: Optional[str] = None) -> str:
    """Send video message (MP4 format)."""
    data = {"file": {"url": url}}
    if caption:
        data["caption"] = caption
    return await send_message("sendVideo", chat_id, session, **data)


@mcp.tool()
async def send_voice(chat_id: str, url: str, session: str = "default") -> str:
    """Send voice message (OGG/OPUS format required)."""
    return await send_message("sendVoice", chat_id, session, file={"url": url})


@mcp.tool()
async def send_location(chat_id: str, latitude: float, longitude: float,
                       session: str = "default", title: Optional[str] = None) -> str:
    """Send location message."""
    data = {"latitude": latitude, "longitude": longitude}
    if title:
        data["title"] = title
    return await send_message("sendLocation", chat_id, session, **data)


@mcp.tool()
async def send_poll(chat_id: str, question: str, options: str,
                   session: str = "default", multiple_answers: bool = False) -> str:
    """Send poll. options: JSON array of poll options e.g. '["Option 1", "Option 2"]'."""
    options_list = parse_json_param(options, "options")
    poll_data = {"name": question, "options": options_list, "multipleAnswers": multiple_answers}
    return await send_message("sendPoll", chat_id, session, poll=poll_data)


@mcp.tool()
async def send_contact(chat_id: str, contact_id: str, session: str = "default") -> str:
    """Send contact card. contact_id format: 1234567890@c.us."""
    return await send_message("sendContactVcard", chat_id, session, contactId=contact_id)


@mcp.tool()
async def send_seen(chat_id: str, message_id: str, session: str = "default") -> str:
    """Mark message as read (send read receipt)."""
    return await send_message("sendSeen", chat_id, session, messageId=message_id)


@mcp.tool()
async def edit_message(chat_id: str, message_id: str, text: str, session: str = "default") -> str:
    """Edit text message."""
    data = {"chatId": chat_id, "messageId": message_id, "text": text, "session": session}
    return await api_call("PUT", "/api/messages", data=data)


@mcp.tool()
async def delete_message(chat_id: str, message_id: str, session: str = "default") -> str:
    """Delete message."""
    data = {"chatId": chat_id, "messageId": message_id, "session": session}
    return await api_call("POST", "/api/messages/delete", data=data)


# ============================================================================
# CHAT MANAGEMENT
# ============================================================================

@mcp.tool()
async def list_chats(session: str = "default", limit: int = 100, offset: int = 0) -> str:
    """List all chats with pagination."""
    return await api_call("GET", f"/api/{session}/chats", params={"limit": limit, "offset": offset})


@mcp.tool()
async def get_messages(chat_id: str, session: str = "default",
                      limit: int = 100, download_media: bool = False) -> str:
    """Get messages from a chat."""
    params = {"limit": limit, "downloadMedia": "true" if download_media else "false"}
    return await api_call("GET", f"/api/{session}/chats/{chat_id}/messages", params=params)


@mcp.tool()
async def archive_chat(chat_id: str, archive: bool = True, session: str = "default") -> str:
    """Archive or unarchive a chat."""
    data = {"chatId": chat_id, "archive": archive, "session": session}
    return await api_call("POST", "/api/chats/archive", data=data)


@mcp.tool()
async def delete_chat(chat_id: str, session: str = "default") -> str:
    """Delete chat and all messages."""
    return await api_call("DELETE", f"/api/{session}/chats/{chat_id}")


# ============================================================================
# GROUP MANAGEMENT
# ============================================================================

async def group_action(action: str, group_id: str, session: str, data: Optional[dict] = None) -> str:
    """Generic group action helper."""
    path = f"/api/{session}/groups/{group_id}/{action}"
    return await api_call("POST" if data or action not in ["", "invite-code"] else "GET", path, data=data)


@mcp.tool()
async def create_group(name: str, participants: str, session: str = "default") -> str:
    """Create WhatsApp group. participants: JSON array e.g. '["1234@c.us", "5678@c.us"]'."""
    data = {"name": name, "participants": parse_json_param(participants, "participants"), "session": session}
    return await api_call("POST", "/api/groups", data=data)


@mcp.tool()
async def list_groups(session: str = "default") -> str:
    """List all groups."""
    return await api_call("GET", f"/api/{session}/groups")


@mcp.tool()
async def get_group(group_id: str, session: str = "default") -> str:
    """Get group details, participants, and settings."""
    return await api_call("GET", f"/api/{session}/groups/{group_id}")


@mcp.tool()
async def add_participant(group_id: str, participant: str, session: str = "default") -> str:
    """Add participant to group. participant format: 1234567890@c.us."""
    return await group_action("participants/add", group_id, session,
                            {"groupId": group_id, "participants": [participant], "session": session})


@mcp.tool()
async def remove_participant(group_id: str, participant: str, session: str = "default") -> str:
    """Remove participant from group."""
    return await group_action("participants/remove", group_id, session,
                            {"groupId": group_id, "participants": [participant], "session": session})


@mcp.tool()
async def promote_to_admin(group_id: str, participant: str, session: str = "default") -> str:
    """Promote participant to group admin."""
    return await group_action("admin/promote", group_id, session,
                            {"groupId": group_id, "participants": [participant], "session": session})


@mcp.tool()
async def demote_from_admin(group_id: str, participant: str, session: str = "default") -> str:
    """Demote admin to regular participant."""
    return await group_action("admin/demote", group_id, session,
                            {"groupId": group_id, "participants": [participant], "session": session})


@mcp.tool()
async def update_group_subject(group_id: str, subject: str, session: str = "default") -> str:
    """Update group name/subject."""
    data = {"subject": subject, "session": session}
    return await api_call("PUT", f"/api/{session}/groups/{group_id}/subject", data=data)


@mcp.tool()
async def update_group_description(group_id: str, description: str, session: str = "default") -> str:
    """Update group description."""
    data = {"description": description, "session": session}
    return await api_call("PUT", f"/api/{session}/groups/{group_id}/description", data=data)


@mcp.tool()
async def get_group_invite_code(group_id: str, session: str = "default") -> str:
    """Get group invite link/code."""
    return await api_call("GET", f"/api/{session}/groups/{group_id}/invite-code")


@mcp.tool()
async def revoke_group_invite_code(group_id: str, session: str = "default") -> str:
    """Revoke group invite code and generate new one."""
    return await api_call("POST", f"/api/{session}/groups/{group_id}/invite-code/revoke")


@mcp.tool()
async def leave_group(group_id: str, session: str = "default") -> str:
    """Leave a group."""
    return await api_call("POST", f"/api/{session}/groups/{group_id}/leave")


@mcp.tool()
async def update_group_settings(group_id: str, session: str = "default",
                               only_admins_can_send: Optional[bool] = None,
                               only_admins_can_edit: Optional[bool] = None) -> str:
    """Update group settings (admin permissions)."""
    data = {"session": session}
    if only_admins_can_send is not None:
        data["onlyAdmins"] = only_admins_can_send
    if only_admins_can_edit is not None:
        data["onlyAdminsCanEditInfo"] = only_admins_can_edit
    return await api_call("PUT", f"/api/{session}/groups/{group_id}/settings", data=data)


# ============================================================================
# CONTACTS & PRESENCE
# ============================================================================

@mcp.tool()
async def get_contacts(session: str = "default") -> str:
    """Get all contacts."""
    return await api_call("GET", f"/api/{session}/contacts")


@mcp.tool()
async def check_number_exists(phone: str, session: str = "default") -> str:
    """Check if phone number exists on WhatsApp."""
    return await api_call("GET", f"/api/{session}/contacts/check-exists", params={"phone": phone})


@mcp.tool()
async def get_contact_about(contact_id: str, session: str = "default") -> str:
    """Get contact's about/status text."""
    return await api_call("GET", f"/api/{session}/contacts/about",
                         params={"contactId": contact_id, "session": session})


@mcp.tool()
async def get_contact_profile_picture(contact_id: str, session: str = "default") -> str:
    """Get contact's profile picture URL."""
    return await api_call("GET", f"/api/{session}/contacts/profile-picture",
                         params={"contactId": contact_id, "session": session})


@mcp.tool()
async def set_presence(presence: str, session: str = "default") -> str:
    """Set presence status. presence: 'available' or 'unavailable'."""
    return await api_call("POST", f"/api/{session}/presence", data={"presence": presence, "session": session})


@mcp.tool()
async def subscribe_presence(contact_id: str, session: str = "default") -> str:
    """Subscribe to contact's presence updates."""
    return await api_call("POST", f"/api/{session}/presence/subscribe",
                         data={"contactId": contact_id, "session": session})


def main():
    """Run the MCP server."""
    logger.info(f"Starting WhatsApp WAHA MCP Server")
    logger.info(f"WAHA Base URL: {WAHA_BASE_URL}")
    logger.info(f"API Key configured: {bool(WAHA_API_KEY)}")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
