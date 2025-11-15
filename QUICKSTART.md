# Quick Start Guide

Get up and running with WAHA MCP Server in 5 minutes!

## Step 1: Install Dependencies

Make sure you have Python 3.10+ and uv installed:

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Step 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/whatsapp-waha-mcp.git
cd whatsapp-waha-mcp

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Step 3: Configure

Create a `.env` file with your WAHA instance details:

```bash
cat > .env << EOF
WAHA_BASE_URL=https://waha.devlike.pro
WAHA_API_KEY=your-api-key-if-needed
EOF
```

## Step 4: Test It

Run the test to verify everything works:

```bash
python test_mcp.py
```

You should see:
```
✅ Server initialized successfully!
✅ Server has 43 tools available!
```

## Step 5: Use with Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

**Important**: Replace `/absolute/path/to/whatsapp-waha-mcp` with the actual absolute path!

## Step 6: Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server should now be available!

## Step 7: Try It Out

Ask Claude:

- "List all my WhatsApp sessions"
- "Start a new WhatsApp session called 'my-phone'"
- "Send a text message to +1234567890 saying 'Hello!'"
- "Create a WhatsApp group called 'Team' with participants +1111111111, +2222222222"

## Troubleshooting

### Server not appearing in Claude Desktop

1. Check the Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

2. Verify the absolute path in your config is correct

3. Ensure the virtual environment exists: `ls .venv/bin/whatsapp-waha-mcp`

### Can't connect to WAHA

1. Test WAHA directly:
   ```bash
   curl https://waha.devlike.pro/api/sessions
   ```

2. Check your WAHA_BASE_URL is correct

3. Verify API key if authentication is required

### Tool calls failing

1. Make sure you have an active WhatsApp session:
   - Use `list_sessions` first
   - Start a session if needed with `start_session`

2. Check chat ID format:
   - Personal chats: `1234567890@c.us`
   - Group chats: `1234567890@g.us`

## Next Steps

- Read [README.md](README.md) for full documentation
- See [TESTING.md](TESTING.md) for testing guide
- Check out all 43 available tools in the code
- Run WAHA locally with Docker for development:
  ```bash
  docker run -it -p 3000:3000 devlikeapro/waha
  ```

## Getting Help

- WAHA Documentation: https://waha.devlike.pro/
- MCP Documentation: https://modelcontextprotocol.io/
- Issues: https://github.com/yourusername/whatsapp-waha-mcp/issues
