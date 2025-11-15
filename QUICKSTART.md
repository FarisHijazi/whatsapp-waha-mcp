# Quick Start

## Install

```bash
# From PyPI (when published)
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key

# Or from GitHub
claude mcp add whatsapp-waha-mcp -- uvx --from git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key
```

## Use

```
"List my WhatsApp sessions"
"Send 'Hello' to +1234567890"
```

## Manage

```bash
# List servers
claude mcp list

# Remove
claude mcp remove whatsapp-waha-mcp
```
