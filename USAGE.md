# Usage Guide

## Setup

```bash
# Install from PyPI (when published)
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000 \
  --env WAHA_API_KEY=your-key

# Or from GitHub
claude mcp add whatsapp-waha-mcp -- uvx --from git+https://github.com/FarisHijazi/whatsapp-waha-mcp.git whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000
```

## Available Tools

All 42 tools are available in Claude Code automatically.

## Session Management

```
"Start a WhatsApp session"
"Get the QR code for authentication"
"List my sessions"
"Stop the session"
```

## Messaging

```
"Send 'Hello' to +1234567890"
"Send this image to +1234567890: https://example.com/img.jpg"
"Send a poll asking 'Favorite color?' with options Red, Blue, Green"
"Send my location (40.7128, -74.0060) to +1234567890"
```

## Chat Management

```
"List my recent chats"
"Get the last 50 messages from +1234567890"
"Archive the chat with +1234567890"
```

## Group Management

```
"Create a group 'Team' with +111 and +222"
"Add +333 to group 123456@g.us"
"Promote +111 to admin in group 123456@g.us"
"Update group name to 'New Team'"
"Get the invite link for group 123456@g.us"
```

## Contacts

```
"Check if +1234567890 is on WhatsApp"
"Get all my contacts"
"Get profile picture for +1234567890"
```

## Chat ID Formats

- Individual: `1234567890@c.us`
- Group: `123456789@g.us`
- Channel: `123456789@newsletter`

## Management

```bash
# List servers
claude mcp list

# Remove
claude mcp remove whatsapp-waha-mcp

# Update (remove and re-add with new config)
claude mcp remove whatsapp-waha-mcp
claude mcp add whatsapp-waha-mcp -- uvx whatsapp-waha-mcp \
  --env WAHA_BASE_URL=http://localhost:3000
```
