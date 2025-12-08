# WhatsApp WAHA MCP Server

Minimal Model Context Protocol (MCP) server for [WAHA (WhatsApp HTTP API)](https://waha.devlike.pro).

**24 tools | 410 lines | 35 tests | No SDK dependencies**

## Features

**24 tools** organized in 6 categories:

### Sessions (4 tools)
- `list_sessions` - List all sessions
- `start_session` - Start new session
- `stop_session` - Stop session
- `get_session` - Get session status

### Messaging (6 tools)
- `send_text` - Send text messages
- `send_image` - Send images
- `send_file` - Send files/documents
- `send_location` - Send location
- `react_to_message` - React with emoji
- `send_seen` - Mark messages as read

### Chats (4 tools)
- `list_chats` - List all chats
- `get_messages` - Get chat messages
- `delete_chat` - Delete chat
- `archive_chat` - Archive chat

### Groups (5 tools)
- `create_group` - Create group
- `list_groups` - List groups
- `get_group` - Get group info
- `add_participants` - Add members
- `remove_participants` - Remove members

### Contacts (3 tools)
- `list_contacts` - List contacts
- `get_contact` - Get contact info
- `check_number` - Check if number exists

### Presence (2 tools)
- `set_presence` - Set online/offline
- `set_typing` - Set typing indicator

## Installation

**Prerequisites:**
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Running WAHA instance

**Install:**

```bash
git clone https://github.com/FarisHijazi/whatsapp-waha-mcp.git
cd whatsapp-waha-mcp
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Configuration

Create `.env` file:

```bash
# Required: Your WAHA server URL
WAHA_BASE_URL=https://your-waha-server.com

# Optional: API key for authentication
WAHA_API_KEY=your-api-key-here

# Optional: Disable SSL verification for self-signed certs
WAHA_VERIFY_SSL=false

# Optional: Chat ID for testing (used by test script)
WAHA_CHAT_ID=1234567890@g.us
```

## Testing Your WAHA Connection

Before using the MCP server, verify your WAHA server is accessible:

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run the connection test
python scripts/test_waha.py
```

The test script will:
1. Check connectivity to your WAHA server
2. List available sessions
3. Show session status
4. Optionally send a test message

## Usage with Claude Desktop

Add to `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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
        "WAHA_BASE_URL": "https://your-waha-server.com",
        "WAHA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Example Usage

Ask Claude:

```
"List all my WhatsApp sessions"
"Start a new session called 'my-phone'"
"Send 'Hello!' to +1234567890"
"Create a group 'Team' with +1111111111, +2222222222"
"List all my chats"
"Get messages from this chat: 120363405900672843@g.us"
```

## Development

**Install dev dependencies:**
```bash
uv pip install -e ".[dev]"
```

**Run tests:**
```bash
pytest                    # Run all tests
pytest -v                 # Verbose mode
pytest --cov              # With coverage report
```

All 35 tests use mocking - no external API calls needed!

## Project Structure

```
whatsapp-waha-mcp/
├── src/whatsapp_waha_mcp/
│   ├── __init__.py          # Package init
│   └── server.py            # MCP server (410 lines)
├── scripts/
│   └── test_waha.py         # Connection test script
├── tests/
│   ├── __init__.py
│   └── test_server.py       # Unit tests (35 tests)
├── pyproject.toml           # Project config
├── pytest.ini               # Test config
├── .env.example             # Environment template
└── README.md                # This file
```

## Technical Details

- **Framework:** FastMCP (lightweight MCP framework)
- **HTTP Client:** httpx (async HTTP library)
- **Transport:** STDIO (standard MCP communication)
- **Protocol:** JSON-RPC 2.0
- **Dependencies:** `mcp`, `httpx`, `python-dotenv`
- **Dev Dependencies:** `pytest`, `pytest-asyncio`, `pytest-mock`, `pytest-cov`
- **Test Coverage:** 35 passing tests

## Why No SDK?

WAHA is a simple REST API. Using httpx directly is:
- **Simpler** - No extra dependencies
- **More transparent** - You see exactly what's called
- **Easier to maintain** - One less layer to debug
- **Smaller codebase** - 410 vs 700+ lines

The entire HTTP layer is just one clean function:

```python
async def api_call(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Make WAHA API request."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    response = await client.request(method, f"{BASE_URL}/api{path}", headers=headers, **kwargs)
    response.raise_for_status()
    return response.json() if response.status_code != 204 else {"success": True}
```

## Troubleshooting

**Server returns 404?**
- Verify `WAHA_BASE_URL` points to your WAHA instance (not the docs site)
- The demo site (waha.devlike.pro) is documentation only
- You need your own running WAHA instance

**SSL errors?**
- Set `WAHA_VERIFY_SSL=false` for self-signed certificates

**Authentication errors?**
- Check your `WAHA_API_KEY` is correct
- Run `python scripts/test_waha.py` to diagnose

## License

MIT License - see [LICENSE](LICENSE)

## Links

- [WAHA Documentation](https://waha.devlike.pro/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
