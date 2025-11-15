# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-15

### Added
- Initial release of WAHA MCP Server
- Complete MCP integration with FastMCP framework
- 43 tools covering all major WAHA API features:
  - Session management (6 tools)
  - Messaging (9 tools)
  - Chat management (6 tools)
  - Group management (8 tools)
  - Contact management (5 tools)
  - Presence management (4 tools)
  - Status/Stories (2 tools)
  - Labels for WhatsApp Business (3 tools)
- Environment-based configuration for WAHA_BASE_URL and WAHA_API_KEY
- Comprehensive error handling and logging
- Test suite for MCP protocol, WAHA API integration, and uvx installation
- Complete documentation (README, TESTING, LICENSE)
- Compatible with Claude Desktop and other MCP clients
- Built with Python 3.10+ using modern async/await patterns
- Installable via uv/uvx for easy deployment

### Features
- **Session Management**: Start, stop, restart, and manage WhatsApp sessions
- **Rich Messaging**: Send text, images, videos, documents, audio, locations, contacts, and polls
- **Group Operations**: Create and manage WhatsApp groups and participants
- **Chat Management**: List, archive, delete, and retrieve chat messages
- **Contact Operations**: Check existence, block/unblock contacts
- **Presence Control**: Set online/offline status and typing indicators
- **Stories/Status**: Post text and image status updates
- **Business Features**: Manage labels for WhatsApp Business accounts
- **Reaction Support**: React to messages with emojis

### Technical Details
- Uses STDIO transport for MCP communication
- Async HTTP client with 30-second timeout
- Proper logging to stderr (required for STDIO-based MCP)
- Type hints and docstrings for all tools
- Auto-generated tool schemas from Python function signatures
- JSON-RPC 2.0 protocol compliance
