# WhatsApp WAHA MCP Server

Minimal MCP server for WhatsApp WAHA API integration. 420 lines of code, 42 tools, 79% test coverage.

## Installation

```bash
# From GitHub
claude mcp add whatsapp-waha-mcp -- uvx --from git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key
```

## Usage

```
"List my WhatsApp sessions"
"Send 'Hello' to +1234567890"
```

## Configuration

### Environment Variables

- `WAHA_BASE_URL` - WAHA instance URL (default: `http://localhost:3000`)
- `WAHA_API_KEY` - API key for authentication (optional)

### Manual Setup

Edit `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "whatsapp-waha-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git"],
      "env": {
        "WAHA_BASE_URL": "http://localhost:3000",
        "WAHA_API_KEY": ""
      }
    }
  }
}
```

## Available Tools (42)

- **Session (9):** list_sessions, get_session, start_session, stop_session, restart_session, get_qr_code, request_pairing_code, get_me, get_messages
- **Messaging (11):** send_text, send_image, send_file, send_video, send_voice, send_location, send_poll, send_contact, send_seen, edit_message, delete_message
- **Chat (3):** list_chats, archive_chat, delete_chat
- **Group (13):** create_group, list_groups, get_group, add_participant, remove_participant, promote_to_admin, demote_from_admin, update_group_subject, update_group_description, get_group_invite_code, revoke_group_invite_code, leave_group, update_group_settings
- **Contacts (4):** get_contacts, check_number_exists, get_contact_about, get_contact_profile_picture
- **Presence (2):** set_presence, subscribe_presence

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov

# Format and lint
black src/ tests/ && ruff check src/ tests/
```
