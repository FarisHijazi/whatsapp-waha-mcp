# WhatsApp WAHA MCP Server

A comprehensive Model Context Protocol (MCP) server for [WAHA (WhatsApp HTTP API)](https://waha.devlike.pro), enabling AI assistants like Claude to interact with WhatsApp programmatically.

## Features

This MCP server provides complete access to WAHA features:

### Session Management
- ✅ List all sessions
- ✅ Start/stop sessions
- ✅ Get session status
- ✅ Restart sessions
- ✅ Logout from sessions

### Messaging
- ✅ Send text messages
- ✅ Send images, videos, documents, audio
- ✅ Send location
- ✅ Send contact cards
- ✅ Send polls
- ✅ React to messages with emojis

### Chats
- ✅ List all chats
- ✅ Get chat messages
- ✅ Delete chats
- ✅ Clear chat messages
- ✅ Archive/unarchive chats

### Groups
- ✅ Create groups
- ✅ List groups
- ✅ Get group info
- ✅ Add/remove participants
- ✅ Leave groups
- ✅ Update group name and description

### Contacts
- ✅ List contacts
- ✅ Get contact info
- ✅ Check if number exists
- ✅ Block/unblock contacts

### Presence
- ✅ Set online/offline status
- ✅ Start/stop typing indicators

### Status/Stories
- ✅ Send text status
- ✅ Send image status

### Labels (WhatsApp Business)
- ✅ List labels
- ✅ Create labels
- ✅ Assign labels to chats

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Access to a WAHA instance (e.g., waha.devlike.pro)

### Quick Start

Install and run locally:

```bash
# Clone the repository
git clone https://github.com/yourusername/whatsapp-waha-mcp.git
cd whatsapp-waha-mcp

# Install with uv
uv pip install -e .

# Run the server
whatsapp-waha-mcp
```

## Configuration

Set environment variables to configure the server:

```bash
# WAHA API base URL (default: https://waha.devlike.pro)
export WAHA_BASE_URL="https://waha.devlike.pro"

# WAHA API key (if required)
export WAHA_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```env
WAHA_BASE_URL=https://waha.devlike.pro
WAHA_API_KEY=your-api-key-here
```

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

For local development:

```json
{
  "mcpServers": {
    "whatsapp-waha": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/whatsapp-waha-mcp",
        "run",
        "whatsapp-waha-mcp"
      ],
      "env": {
        "WAHA_BASE_URL": "https://waha.devlike.pro",
        "WAHA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Example Usage

Once configured with Claude Desktop, you can ask Claude to:

```
"List all my WhatsApp sessions"
"Start a new WhatsApp session called 'my-phone'"
"Send a text message to +1234567890 saying 'Hello from Claude!'"
"Create a group called 'Team' with participants +1234567890, +0987654321"
"List all my chats"
"Get messages from chat 1234567890@c.us"
```

## Available Tools

The server exposes 50+ tools for comprehensive WhatsApp automation. See the full list in the [source code](src/whatsapp_waha_mcp/server.py).

### Session Tools
- `list_sessions()` - List all sessions
- `start_session(name, config?)` - Start a new session
- `stop_session(name)` - Stop a session
- `get_session_status(name)` - Get session status
- `restart_session(name)` - Restart a session
- `logout_session(name)` - Logout from session

### Messaging Tools
- `send_text_message(session, chat_id, text, reply_to?)` - Send text
- `send_image(session, chat_id, url, caption?)` - Send image
- `send_video(session, chat_id, url, caption?)` - Send video
- `send_document(session, chat_id, url, filename?, caption?)` - Send document
- `send_audio(session, chat_id, url)` - Send audio
- `send_location(session, chat_id, latitude, longitude, title?)` - Send location
- `send_contact(session, chat_id, contact_id)` - Send contact
- `send_poll(session, chat_id, title, options, multiple_answers?)` - Send poll
- `react_to_message(session, chat_id, message_id, reaction)` - React with emoji

### Chat Tools
- `list_chats(session, limit?, offset?)` - List chats
- `get_chat_messages(session, chat_id, limit?)` - Get messages
- `delete_chat(session, chat_id)` - Delete chat
- `clear_chat_messages(session, chat_id)` - Clear messages
- `archive_chat(session, chat_id)` - Archive chat
- `unarchive_chat(session, chat_id)` - Unarchive chat

### Group Tools
- `create_group(session, name, participants)` - Create group
- `list_groups(session)` - List groups
- `get_group_info(session, group_id)` - Get group info
- `add_group_participants(session, group_id, participants)` - Add members
- `remove_group_participants(session, group_id, participants)` - Remove members
- `leave_group(session, group_id)` - Leave group
- `update_group_subject(session, group_id, subject)` - Update name
- `update_group_description(session, group_id, description)` - Update description

And many more!

## Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## Architecture

This server uses:
- **FastMCP**: Simplified MCP server framework for Python
- **httpx**: Async HTTP client for WAHA API calls
- **STDIO Transport**: Communicates with MCP hosts via standard input/output

## Troubleshooting

### Server not starting
- Ensure Python 3.10+ is installed
- Check that `uv` is properly installed
- Verify WAHA_BASE_URL is accessible

### Authentication errors
- Verify your WAHA_API_KEY is correct
- Check if your WAHA instance requires authentication

### Connection issues
- Ensure WAHA instance is running and accessible
- Check network connectivity
- Verify SSL certificates if using HTTPS

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Links

- [WAHA Documentation](https://waha.devlike.pro/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)

## Support

For issues and questions:
- WAHA: https://github.com/devlikeapro/waha
- This MCP Server: https://github.com/yourusername/whatsapp-waha-mcp/issues
