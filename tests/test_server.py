"""Unit tests for WAHA MCP Server"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.whatsapp_waha_mcp import server


@pytest.fixture
def mock_client():
    """Mock httpx AsyncClient"""
    with patch.object(server, 'client') as mock:
        yield mock


@pytest.fixture
def mock_response():
    """Mock httpx Response"""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"success": True, "data": "test"}
    response.raise_for_status = MagicMock()
    return response


class TestApiCall:
    """Test the api_call helper function"""

    async def test_successful_get_request(self, mock_client, mock_response):
        """Test successful GET request"""
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.api_call("GET", "/test")

        assert result == {"success": True, "data": "test"}
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == f"{server.BASE_URL}/api/test"

    async def test_successful_post_with_data(self, mock_client, mock_response):
        """Test successful POST request with JSON data"""
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.api_call("POST", "/test", json={"key": "value"})

        assert result == {"success": True, "data": "test"}
        call_args = mock_client.request.call_args
        assert call_args[1]["json"] == {"key": "value"}

    async def test_request_with_api_key(self, mock_client, mock_response):
        """Test request includes API key when set"""
        original_key = server.API_KEY
        server.API_KEY = "test-api-key"
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.api_call("GET", "/test")

        call_args = mock_client.request.call_args
        assert call_args[1]["headers"]["X-API-Key"] == "test-api-key"

        server.API_KEY = original_key

    async def test_204_no_content_response(self, mock_client):
        """Test handling of 204 No Content response"""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 204
        response.raise_for_status = MagicMock()
        mock_client.request = AsyncMock(return_value=response)

        result = await server.api_call("DELETE", "/test")

        assert result == {"success": True}

    async def test_http_error_handling(self, mock_client):
        """Test HTTP error handling"""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 404
        response.text = "Not Found"
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )
        mock_client.request = AsyncMock(return_value=response)

        with pytest.raises(Exception) as exc_info:
            await server.api_call("GET", "/nonexistent")

        assert "API error 404" in str(exc_info.value)

    async def test_network_error_handling(self, mock_client):
        """Test network error handling"""
        mock_client.request = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))

        with pytest.raises(Exception) as exc_info:
            await server.api_call("GET", "/test")

        assert "Request failed" in str(exc_info.value)


class TestSessionTools:
    """Test session management tools"""

    async def test_list_sessions(self, mock_client, mock_response):
        """Test list_sessions tool"""
        mock_response.json.return_value = [{"name": "default", "status": "online"}]
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.list_sessions()

        assert "default" in result
        assert "online" in result

    async def test_start_session(self, mock_client, mock_response):
        """Test start_session tool"""
        mock_response.json.return_value = {"name": "test", "qr": "qr-code"}
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.start_session("test")

        assert "test" in result
        call_args = mock_client.request.call_args
        assert call_args[1]["json"] == {"name": "test"}

    async def test_start_session_with_config(self, mock_client, mock_response):
        """Test start_session with config"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.start_session("test", '{"key": "value"}')

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["config"] == {"key": "value"}

    async def test_stop_session(self, mock_client, mock_response):
        """Test stop_session tool"""
        mock_response.status_code = 204
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.stop_session("test")

        assert "success" in result.lower()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/sessions/test" in call_args[0][1]

    async def test_get_session(self, mock_client, mock_response):
        """Test get_session tool"""
        mock_response.json.return_value = {"name": "test", "status": "online"}
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.get_session("test")

        assert "test" in result
        assert "online" in result


class TestMessagingTools:
    """Test messaging tools"""

    async def test_send_text(self, mock_client, mock_response):
        """Test send_text tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.send_text("default", "1234567890@c.us", "Hello")

        call_args = mock_client.request.call_args
        # Using the new WAHA API format with /api/sendText
        assert "/sendText" in call_args[0][1]
        assert call_args[1]["json"] == {
            "session": "default",
            "chatId": "1234567890@c.us",
            "text": "Hello"
        }

    async def test_send_text_with_reply(self, mock_client, mock_response):
        """Test send_text with reply_to"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.send_text("default", "1234567890@c.us", "Reply", "msg123")

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["reply_to"] == "msg123"

    async def test_send_image(self, mock_client, mock_response):
        """Test send_image tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.send_image(
            "default",
            "1234567890@c.us",
            "https://example.com/image.jpg",
            "Caption"
        )

        call_args = mock_client.request.call_args
        assert "/sendImage" in call_args[0][1]
        json_data = call_args[1]["json"]
        assert json_data["session"] == "default"
        assert json_data["file"]["url"] == "https://example.com/image.jpg"
        assert json_data["caption"] == "Caption"

    async def test_send_file(self, mock_client, mock_response):
        """Test send_file tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.send_file(
            "default",
            "1234567890@c.us",
            "https://example.com/doc.pdf",
            "document.pdf",
            "My document"
        )

        call_args = mock_client.request.call_args
        assert "/sendFile" in call_args[0][1]
        json_data = call_args[1]["json"]
        assert json_data["session"] == "default"
        assert json_data["filename"] == "document.pdf"
        assert json_data["caption"] == "My document"

    async def test_send_location(self, mock_client, mock_response):
        """Test send_location tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.send_location(
            "default",
            "1234567890@c.us",
            37.7749,
            -122.4194,
            "San Francisco"
        )

        call_args = mock_client.request.call_args
        assert "/sendLocation" in call_args[0][1]
        json_data = call_args[1]["json"]
        assert json_data["session"] == "default"
        assert json_data["latitude"] == 37.7749
        assert json_data["longitude"] == -122.4194
        assert json_data["title"] == "San Francisco"

    async def test_react_to_message(self, mock_client, mock_response):
        """Test react_to_message tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.react_to_message(
            "default",
            "1234567890@c.us",
            "msg123",
            "like"
        )

        call_args = mock_client.request.call_args
        json_data = call_args[1]["json"]
        assert json_data["session"] == "default"
        assert json_data["messageId"] == "msg123"
        assert json_data["reaction"] == "like"

    async def test_send_seen(self, mock_client, mock_response):
        """Test send_seen tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.send_seen("default", "1234567890@c.us")

        call_args = mock_client.request.call_args
        assert "/sendSeen" in call_args[0][1]
        json_data = call_args[1]["json"]
        assert json_data["session"] == "default"
        assert json_data["chatId"] == "1234567890@c.us"


class TestChatTools:
    """Test chat management tools"""

    async def test_list_chats(self, mock_client, mock_response):
        """Test list_chats tool"""
        mock_response.json.return_value = [
            {"id": "123@c.us", "name": "John"},
            {"id": "456@c.us", "name": "Jane"}
        ]
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.list_chats("default", 50)

        call_args = mock_client.request.call_args
        assert call_args[1]["params"] == {"limit": 50}
        assert "John" in result

    async def test_get_messages(self, mock_client, mock_response):
        """Test get_messages tool"""
        mock_response.json.return_value = [
            {"id": "1", "text": "Hello"},
            {"id": "2", "text": "Hi"}
        ]
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.get_messages("default", "1234567890@c.us", 20)

        call_args = mock_client.request.call_args
        assert "/chats/1234567890@c.us/messages" in call_args[0][1]
        assert call_args[1]["params"]["limit"] == 20

    async def test_delete_chat(self, mock_client, mock_response):
        """Test delete_chat tool"""
        mock_response.status_code = 204
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.delete_chat("default", "1234567890@c.us")

        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/chats/1234567890@c.us" in call_args[0][1]

    async def test_archive_chat(self, mock_client, mock_response):
        """Test archive_chat tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.archive_chat("default", "1234567890@c.us")

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["archive"] is True


class TestGroupTools:
    """Test group management tools"""

    async def test_create_group(self, mock_client, mock_response):
        """Test create_group tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.create_group("default", "Test Group", "1234567890,0987654321")

        call_args = mock_client.request.call_args
        json_data = call_args[1]["json"]
        assert json_data["name"] == "Test Group"
        assert "1234567890@c.us" in json_data["participants"]
        assert "0987654321@c.us" in json_data["participants"]

    async def test_create_group_with_formatted_numbers(self, mock_client, mock_response):
        """Test create_group with already formatted numbers"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.create_group("default", "Test", "1234567890@c.us,9876543210")

        call_args = mock_client.request.call_args
        participants = call_args[1]["json"]["participants"]
        assert "1234567890@c.us" in participants
        assert "9876543210@c.us" in participants

    async def test_list_groups(self, mock_client, mock_response):
        """Test list_groups tool"""
        mock_response.json.return_value = [
            {"id": "123@g.us", "name": "Group 1"}
        ]
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.list_groups("default")

        assert "Group 1" in result

    async def test_get_group(self, mock_client, mock_response):
        """Test get_group tool"""
        mock_response.json.return_value = {
            "id": "123@g.us",
            "name": "Test Group",
            "participants": []
        }
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.get_group("default", "123@g.us")

        assert "Test Group" in result

    async def test_add_participants(self, mock_client, mock_response):
        """Test add_participants tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.add_participants("default", "123@g.us", "1111111111,2222222222")

        call_args = mock_client.request.call_args
        participants = call_args[1]["json"]["participants"]
        assert len(participants) == 2

    async def test_remove_participants(self, mock_client, mock_response):
        """Test remove_participants tool"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.remove_participants("default", "123@g.us", "1111111111")

        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"


class TestContactTools:
    """Test contact management tools"""

    async def test_list_contacts(self, mock_client, mock_response):
        """Test list_contacts tool"""
        mock_response.json.return_value = [
            {"id": "123@c.us", "name": "John"}
        ]
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.list_contacts("default")

        assert "John" in result

    async def test_get_contact(self, mock_client, mock_response):
        """Test get_contact tool"""
        mock_response.json.return_value = {
            "id": "123@c.us",
            "name": "John",
            "number": "1234567890"
        }
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.get_contact("default", "123@c.us")

        assert "John" in result
        assert "1234567890" in result

    async def test_check_number(self, mock_client, mock_response):
        """Test check_number tool"""
        mock_response.json.return_value = {"exists": True}
        mock_client.request = AsyncMock(return_value=mock_response)

        result = await server.check_number("default", "1234567890")

        call_args = mock_client.request.call_args
        assert "/checkNumberStatus" in call_args[0][1]
        assert call_args[1]["json"]["phone"] == "1234567890"
        assert call_args[1]["json"]["session"] == "default"


class TestPresenceTools:
    """Test presence management tools"""

    async def test_set_presence_online(self, mock_client, mock_response):
        """Test set_presence with online=True"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.set_presence("default", True)

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["presence"] == "online"

    async def test_set_presence_offline(self, mock_client, mock_response):
        """Test set_presence with online=False"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.set_presence("default", False)

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["presence"] == "offline"

    async def test_set_typing_true(self, mock_client, mock_response):
        """Test set_typing with typing=True"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.set_typing("default", "123@c.us", True)

        call_args = mock_client.request.call_args
        json_data = call_args[1]["json"]
        assert json_data["chatId"] == "123@c.us"
        assert json_data["typing"] is True

    async def test_set_typing_false(self, mock_client, mock_response):
        """Test set_typing with typing=False"""
        mock_client.request = AsyncMock(return_value=mock_response)

        await server.set_typing("default", "123@c.us", False)

        call_args = mock_client.request.call_args
        assert call_args[1]["json"]["typing"] is False
