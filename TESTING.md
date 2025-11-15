# Testing Guide

This document describes how to test the WAHA MCP server.

## Running the Tests

We've included several test scripts to verify the server works correctly:

### 1. Basic MCP Protocol Test

Tests that the server initializes correctly and exposes all tools:

```bash
python test_mcp.py
```

Expected output:
```
✅ Server initialized successfully!
✅ Server has 43 tools available!
```

### 2. WAHA API Integration Test

Tests that the server can make API calls to WAHA:

```bash
python test_waha_api.py
```

This test will attempt to call the `list_sessions` endpoint on WAHA. If WAHA is accessible and doesn't require authentication, you'll see the actual session list. Otherwise, you'll see an error (which is expected and shows proper error handling).

### 3. uvx Installation Test

Tests that the package can be run with uvx:

```bash
# Note: Requires network access to download Python if not cached
python test_uvx.py
```

## Manual Testing with Claude Desktop

1. Add the server to your Claude Desktop configuration:

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

2. Restart Claude Desktop

3. Try asking Claude:
   - "List all WhatsApp sessions"
   - "Start a new session called 'test'"
   - "Send a message to +1234567890"

## Testing with a Local WAHA Instance

For full integration testing, run WAHA locally:

```bash
# Start WAHA with Docker
docker run -it -p 3000:3000 devlikeapro/waha

# Update .env file
echo "WAHA_BASE_URL=http://localhost:3000" > .env

# Run the integration test
python test_waha_api.py
```

## Available Tools

The server exposes 43 tools across these categories:

### Session Management (6 tools)
- list_sessions
- start_session
- stop_session
- get_session_status
- restart_session
- logout_session

### Messaging (9 tools)
- send_text_message
- send_image
- send_video
- send_document
- send_audio
- send_location
- send_contact
- send_poll
- react_to_message

### Chats (6 tools)
- list_chats
- get_chat_messages
- delete_chat
- clear_chat_messages
- archive_chat
- unarchive_chat

### Groups (8 tools)
- create_group
- list_groups
- get_group_info
- add_group_participants
- remove_group_participants
- leave_group
- update_group_subject
- update_group_description

### Contacts (5 tools)
- list_contacts
- get_contact
- check_number_exists
- block_contact
- unblock_contact

### Presence (4 tools)
- set_presence_online
- set_presence_offline
- start_typing
- stop_typing

### Status/Stories (2 tools)
- send_text_status
- send_image_status

### Labels (3 tools)
- list_labels
- create_label
- assign_label_to_chat

## Troubleshooting

### Server won't start
- Check that Python 3.10+ is installed: `python --version`
- Verify uv is installed: `uv --version`
- Check the logs in stderr

### Connection errors
- Verify WAHA_BASE_URL is correct
- Test WAHA directly: `curl $WAHA_BASE_URL/api/sessions`
- Check network connectivity

### Authentication errors
- Ensure WAHA_API_KEY is set if your WAHA instance requires it
- Verify the API key is correct

### Tool calls failing
- Check that the session name exists
- Verify chat IDs are in the correct format (e.g., `1234567890@c.us` for contacts, `1234567890@g.us` for groups)
- Review the error message returned by the tool
