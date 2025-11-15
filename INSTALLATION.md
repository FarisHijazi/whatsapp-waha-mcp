# Installation Guide

## From PyPI (when published)

```bash
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key
```

## From GitHub

```bash
claude mcp add whatsapp-waha-mcp -- uvx --from git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key
```

## Environment Variables

- `WAHA_BASE_URL` - Your WAHA instance URL
- `WAHA_API_KEY` - API key (optional)

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

# Update (remove and re-add)
claude mcp remove whatsapp-waha-mcp
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000
```

## Development

```bash
# Clone and install
git clone https://github.com/FarisHijazi/whatsapp-waha-mcp.git
cd whatsapp-waha-mcp
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov
```
