# WhatsApp WAHA MCP Server - Documentation

## Overview

Minimal MCP server (420 lines) providing 42 tools for WhatsApp WAHA API integration.

## Quick Start

```bash
# Start WAHA
docker run -d -p 3000:3000 devlikeapro/waha

# Install
uv pip install -e .

# Use with Claude Code (automatic via .claude/mcp.json)
"List my WhatsApp sessions"
```

## Architecture

```
Claude Code
    ↓ (loads .claude/mcp.json)
MCP Server (42 tools)
    ↓ (HTTP)
WAHA Instance
    ↓
WhatsApp
```

## Configuration

`.claude/mcp.json`:
```json
{
  "mcpServers": {
    "whatsapp-waha": {
      "command": "python",
      "args": ["-m", "whatsapp_waha_mcp"],
      "env": {
        "WAHA_BASE_URL": "http://localhost:3000",
        "WAHA_API_KEY": ""
      }
    }
  }
}
```

## Tools (42 total)

### Session (9 tools)
- list_sessions, get_session, start_session, stop_session
- restart_session, get_qr_code, request_pairing_code
- get_me, get_messages

### Messaging (11 tools)
- send_text, send_image, send_file, send_video, send_voice
- send_location, send_poll, send_contact, send_seen
- edit_message, delete_message

### Chat (3 tools)
- list_chats, archive_chat, delete_chat

### Group (13 tools)
- create_group, list_groups, get_group
- add_participant, remove_participant
- promote_to_admin, demote_from_admin
- update_group_subject, update_group_description
- get_group_invite_code, revoke_group_invite_code
- leave_group, update_group_settings

### Contacts (4 tools)
- get_contacts, check_number_exists
- get_contact_about, get_contact_profile_picture

### Presence (2 tools)
- set_presence, subscribe_presence

## Code Structure

```
src/whatsapp_waha_mcp/
  server.py     420 lines (61% reduction from 1085)
                - api_call() - generic HTTP handler
                - send_message() - messaging helper
                - group_action() - group operations helper
                - parse_json_param() - JSON parsing

tests/
  test_server.py  349 lines, 38 tests, 79% coverage
```

## Development

```bash
# Install dev deps
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov

# Format & lint
black src/ tests/ && ruff check src/ tests/

# Verify tools
python simple_tool_check.py
```

## Chat ID Formats

- Individual: `1234567890@c.us`
- Group: `123456789@g.us`
- Channel: `123456789@newsletter`

## Example Commands

```
"List my WhatsApp sessions"
"Send 'Meeting at 3pm' to +1234567890"
"Create group 'Team' with +111 and +222"
"Get last 20 messages from +1234567890"
"Add +333 to group 123456@g.us"
"Promote +111 to admin"
```

## Stats

- **Code:** 420 lines (minimal)
- **Tests:** 38 passing, 79% coverage
- **Tools:** 42 working
- **Dependencies:** mcp, httpx

## Security

- No credentials in code
- Environment variable configuration
- Optional API key authentication
- Logging to stderr only (MCP requirement)

## Links

- [WAHA Docs](https://waha.devlike.pro)
- [MCP Docs](https://modelcontextprotocol.io)
