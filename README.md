# WhatsApp WAHA MCP Server

Minimal Model Context Protocol (MCP) server for [WAHA (WhatsApp HTTP API)](https://waha.devlike.pro).

**23 tools • 300 lines • 98% test coverage • No SDK dependencies**

## Features

**23 tools** organized in 6 categories:

### Sessions (4 tools)
- `list_sessions` - List all sessions
- `start_session` - Start new session
- `stop_session` - Stop session
- `get_session` - Get session status

### Messaging (5 tools)
- `send_text` - Send text messages
- `send_image` - Send images
- `send_file` - Send files/documents
- `send_location` - Send location
- `react_to_message` - React with emoji

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
- WAHA instance (e.g., waha.devlike.pro)

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
WAHA_BASE_URL=https://waha.devlike.pro
WAHA_API_KEY=your-api-key-here
```

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
        "WAHA_BASE_URL": "https://waha.devlike.pro",
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

All 34 tests use mocking - no external API calls needed!

## Project Structure

```
whatsapp-waha-mcp/
├── src/whatsapp_waha_mcp/
│   ├── __init__.py          # Package init
│   └── server.py            # MCP server (300 lines)
├── tests/
│   ├── __init__.py
│   └── test_server.py       # Unit tests (34 tests, 98% coverage)
├── pyproject.toml           # Project config
├── pytest.ini               # Test config
└── README.md                # This file
```

## Technical Details

- **Framework:** FastMCP (lightweight MCP framework)
- **HTTP Client:** httpx (async HTTP library)
- **Transport:** STDIO (standard MCP communication)
- **Protocol:** JSON-RPC 2.0
- **Dependencies:** `mcp`, `httpx`, `python-dotenv`
- **Dev Dependencies:** `pytest`, `pytest-asyncio`, `pytest-mock`, `pytest-cov`
- **Test Coverage:** 98% (34 passing tests)

## Why No SDK?

WAHA is a simple REST API. Using httpx directly is:
- ✅ **Simpler** - No extra dependencies
- ✅ **More transparent** - You see exactly what's called
- ✅ **Easier to maintain** - One less layer to debug
- ✅ **Smaller codebase** - 300 vs 700+ lines

The entire HTTP layer is just one clean function:

```python
async def api_call(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Make WAHA API request."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    response = await client.request(method, f"{BASE_URL}/api{path}", headers=headers, **kwargs)
    response.raise_for_status()
    return response.json() if response.status_code != 204 else {"success": True}
```

## License

MIT License - see [LICENSE](LICENSE)

## Links

- [WAHA Documentation](https://waha.devlike.pro/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
