# Claude Code MCP Configuration

## Quick Setup

```bash
# From PyPI (when published)
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key

# From GitHub
claude mcp add whatsapp-waha-mcp -- uvx --from git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000
```

## Manual Configuration

Edit `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "whatsapp-waha-mcp": {
      "command": "uvx",
      "args": ["whatsapp-waha-mcp"],
      "env": {
        "WAHA_BASE_URL": "http://localhost:3000",
        "WAHA_API_KEY": ""
      }
    }
  }
}
```

## Management

```bash
# List servers
claude mcp list

# Remove
claude mcp remove whatsapp-waha-mcp
```
