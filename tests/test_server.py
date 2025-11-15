"""Tests for the WAHA MCP server."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from whatsapp_waha_mcp import server


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_headers_without_api_key(self, monkeypatch):
        """Test headers without API key."""
        monkeypatch.setenv("WAHA_API_KEY", "")
        headers = server.get_headers()
        assert headers == {"Content-Type": "application/json"}

    def test_get_headers_with_api_key(self, monkeypatch):
        """Test headers with API key."""
        monkeypatch.setenv("WAHA_API_KEY", "test-key")
        # Reload to pick up new env var
        import importlib
        importlib.reload(server)
        headers = server.get_headers()
        assert "X-Api-Key" in headers
        assert headers["X-Api-Key"] == "test-key"

    def test_parse_json_param_valid(self):
        """Test parsing valid JSON."""
        result = server.parse_json_param('{"key": "value"}', "test")
        assert result == {"key": "value"}

    def test_parse_json_param_invalid(self):
        """Test parsing invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            server.parse_json_param("{invalid}", "test")

    def test_parse_json_param_none(self):
        """Test parsing None."""
        result = server.parse_json_param(None, "test")
        assert result is None


class TestAPICall:
    """Test API call function."""

    @pytest.mark.asyncio
    async def test_api_call_success(self, mock_env, mock_http_client):
        """Test successful API call."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            result = await server.api_call("GET", "/api/test")
            assert "success" in result
            mock_http_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_call_with_data(self, mock_env, mock_http_client):
        """Test API call with data."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.api_call("POST", "/api/test", data={"key": "value"})
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_api_call_with_params(self, mock_env, mock_http_client):
        """Test API call with params."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.api_call("GET", "/api/test", params={"limit": 10})
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"] == {"limit": 10}

    @pytest.mark.asyncio
    async def test_api_call_http_error(self, mock_env, mock_httpx_response):
        """Test API call with HTTP error."""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_httpx_response(404, {"error": "Not found"}))

        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_client):
            with pytest.raises(Exception, match="WAHA API error"):
                await server.api_call("GET", "/api/notfound")


class TestSessionManagement:
    """Test session management tools."""

    @pytest.mark.asyncio
    async def test_list_sessions(self, mock_env, mock_http_client):
        """Test list_sessions."""
        mock_http_client.request.return_value.json.return_value = [{"name": "default"}]
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            result = await server.list_sessions()
            assert "default" in result

    @pytest.mark.asyncio
    async def test_list_sessions_all(self, mock_env, mock_http_client):
        """Test list_sessions with all parameter."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.list_sessions(all=True)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"] == {"all": "true"}

    @pytest.mark.asyncio
    async def test_get_session(self, mock_env, mock_http_client):
        """Test get_session."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.get_session("test-session")
            call_args = mock_http_client.request.call_args
            assert "/api/sessions/test-session" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_start_session(self, mock_env, mock_http_client):
        """Test start_session."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.start_session("test-session")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["name"] == "test-session"

    @pytest.mark.asyncio
    async def test_start_session_with_config(self, mock_env, mock_http_client):
        """Test start_session with config."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            config = '{"webhook": "http://example.com"}'
            await server.start_session("test-session", config=config)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["webhook"] == "http://example.com"

    @pytest.mark.asyncio
    async def test_stop_session(self, mock_env, mock_http_client):
        """Test stop_session."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.stop_session("test-session")
            assert mock_http_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_stop_session_with_logout(self, mock_env, mock_http_client):
        """Test stop_session with logout."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.stop_session("test-session", logout=True)
            assert mock_http_client.request.call_count == 2  # logout + stop

    @pytest.mark.asyncio
    async def test_get_qr_code(self, mock_env, mock_http_client):
        """Test get_qr_code."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.get_qr_code("test-session", format="raw")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"]["format"] == "raw"


class TestMessaging:
    """Test messaging tools."""

    @pytest.mark.asyncio
    async def test_send_text(self, mock_env, mock_http_client):
        """Test send_text."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.send_text("1234@c.us", "Hello")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["text"] == "Hello"
            assert call_args[1]["json"]["chatId"] == "1234@c.us"

    @pytest.mark.asyncio
    async def test_send_text_with_mentions(self, mock_env, mock_http_client):
        """Test send_text with mentions."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            mentions = '["1234567890"]'
            await server.send_text("1234@c.us", "Hello @user", mentions=mentions)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["mentions"] == ["1234567890"]

    @pytest.mark.asyncio
    async def test_send_image(self, mock_env, mock_http_client):
        """Test send_image."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.send_image("1234@c.us", "http://example.com/image.jpg", caption="Test")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["file"]["url"] == "http://example.com/image.jpg"
            assert call_args[1]["json"]["caption"] == "Test"

    @pytest.mark.asyncio
    async def test_send_poll(self, mock_env, mock_http_client):
        """Test send_poll."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            options = '["Option 1", "Option 2"]'
            await server.send_poll("1234@c.us", "Question?", options)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["poll"]["name"] == "Question?"
            assert len(call_args[1]["json"]["poll"]["options"]) == 2

    @pytest.mark.asyncio
    async def test_send_location(self, mock_env, mock_http_client):
        """Test send_location."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.send_location("1234@c.us", 40.7128, -74.0060, title="NYC")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["latitude"] == 40.7128
            assert call_args[1]["json"]["longitude"] == -74.0060
            assert call_args[1]["json"]["title"] == "NYC"

    @pytest.mark.asyncio
    async def test_edit_message(self, mock_env, mock_http_client):
        """Test edit_message."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.edit_message("1234@c.us", "msg123", "Updated text")
            call_args = mock_http_client.request.call_args
            assert call_args[0][0] == "PUT"
            assert call_args[1]["json"]["text"] == "Updated text"

    @pytest.mark.asyncio
    async def test_delete_message(self, mock_env, mock_http_client):
        """Test delete_message."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.delete_message("1234@c.us", "msg123")
            call_args = mock_http_client.request.call_args
            assert "delete" in call_args[0][1]


class TestChatManagement:
    """Test chat management tools."""

    @pytest.mark.asyncio
    async def test_list_chats(self, mock_env, mock_http_client):
        """Test list_chats."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.list_chats(limit=50, offset=10)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"]["limit"] == 50
            assert call_args[1]["params"]["offset"] == 10

    @pytest.mark.asyncio
    async def test_get_messages(self, mock_env, mock_http_client):
        """Test get_messages."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.get_messages("1234@c.us", download_media=True)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"]["downloadMedia"] == "true"

    @pytest.mark.asyncio
    async def test_archive_chat(self, mock_env, mock_http_client):
        """Test archive_chat."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.archive_chat("1234@c.us", archive=True)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["archive"] is True


class TestGroupManagement:
    """Test group management tools."""

    @pytest.mark.asyncio
    async def test_create_group(self, mock_env, mock_http_client):
        """Test create_group."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            participants = '["1111@c.us", "2222@c.us"]'
            await server.create_group("Test Group", participants)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["name"] == "Test Group"
            assert len(call_args[1]["json"]["participants"]) == 2

    @pytest.mark.asyncio
    async def test_add_participant(self, mock_env, mock_http_client):
        """Test add_participant."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.add_participant("123@g.us", "1111@c.us")
            call_args = mock_http_client.request.call_args
            assert "participants/add" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_promote_to_admin(self, mock_env, mock_http_client):
        """Test promote_to_admin."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.promote_to_admin("123@g.us", "1111@c.us")
            call_args = mock_http_client.request.call_args
            assert "admin/promote" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_update_group_settings(self, mock_env, mock_http_client):
        """Test update_group_settings."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.update_group_settings("123@g.us", only_admins_can_send=True)
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["onlyAdmins"] is True


class TestContactsAndPresence:
    """Test contacts and presence tools."""

    @pytest.mark.asyncio
    async def test_get_contacts(self, mock_env, mock_http_client):
        """Test get_contacts."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.get_contacts()
            call_args = mock_http_client.request.call_args
            assert "/contacts" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_check_number_exists(self, mock_env, mock_http_client):
        """Test check_number_exists."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.check_number_exists("+1234567890")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["params"]["phone"] == "+1234567890"

    @pytest.mark.asyncio
    async def test_set_presence(self, mock_env, mock_http_client):
        """Test set_presence."""
        with patch("whatsapp_waha_mcp.server.get_client", return_value=mock_http_client):
            await server.set_presence("available")
            call_args = mock_http_client.request.call_args
            assert call_args[1]["json"]["presence"] == "available"


class TestToolRegistration:
    """Test that all tools are properly registered."""

    def test_all_tools_registered(self):
        """Test that all 42 tools are registered."""
        tools = server.mcp._tool_manager._tools
        assert len(tools) == 42

    def test_session_tools_registered(self):
        """Test session management tools are registered."""
        tools = server.mcp._tool_manager._tools
        session_tools = ["list_sessions", "get_session", "start_session", "stop_session",
                        "restart_session", "get_qr_code", "request_pairing_code", "get_me"]
        for tool in session_tools:
            assert tool in tools

    def test_messaging_tools_registered(self):
        """Test messaging tools are registered."""
        tools = server.mcp._tool_manager._tools
        messaging_tools = ["send_text", "send_image", "send_file", "send_video",
                          "send_voice", "send_location", "send_poll", "send_contact",
                          "send_seen", "edit_message", "delete_message"]
        for tool in messaging_tools:
            assert tool in tools

    def test_group_tools_registered(self):
        """Test group management tools are registered."""
        tools = server.mcp._tool_manager._tools
        group_tools = ["create_group", "list_groups", "get_group", "add_participant",
                      "remove_participant", "promote_to_admin", "demote_from_admin",
                      "update_group_subject", "update_group_description",
                      "get_group_invite_code", "revoke_group_invite_code",
                      "leave_group", "update_group_settings"]
        for tool in group_tools:
            assert tool in tools
