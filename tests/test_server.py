import pytest
from unittest.mock import patch, AsyncMock
from altiplano.server import mcp, list_projects

@pytest.mark.anyio
async def test_mcp_initialization():
    """Verify that FastMCP is initialized correctly and tools are registered."""
    assert mcp.name == "altiplano"
    
    # Check that tools are registered on the FastMCP instance
    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    
    expected_tools = [
        "list_projects",
        "create_project",
        "list_tasks",
        "get_task",
        "create_task",
        "update_task",
        "set_reminders",
        "list_labels",
        "add_label",
        "remove_label",
        "list_comments",
        "add_comment",
        "search_users",
        "list_assignees",
        "add_assignee",
        "remove_assignee"
    ]
    
    for tool in expected_tools:
        assert tool in tool_names


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_projects(mock_request):
    """Test the list_projects tool using API mocks."""
    # Set mock response for the _request call
    mock_request.return_value = [
        {"id": 1, "title": "Test Project", "parent_project_id": 0, "is_archived": False}
    ]
    
    result = await list_projects()
    
    # Assert return value format matching list_projects tool output
    assert result == [
        {
            "id": 1,
            "title": "Test Project",
            "parent_project_id": 0,
            "is_archived": False,
        }
    ]
    
    # Assert _request was called correctly
    mock_request.assert_called_once_with("GET", "/projects")


def test_cloudflare_headers():
    """Verify that Cloudflare Access Service Token headers are appended when configured."""
    from altiplano.server import _headers

    # Case 1: No Cloudflare config
    with patch("altiplano.server._conf", side_effect=lambda key: "fake-token" if key == "VIKUNJA_API_TOKEN" else None):
        headers = _headers()
        assert "Authorization" in headers
        assert "CF-Access-Client-Id" not in headers
        assert "CF-Access-Client-Secret" not in headers

    # Case 2: Cloudflare config is present
    def mock_conf(key):
        values = {
            "VIKUNJA_API_TOKEN": "fake-token",
            "CF_CLIENT_ID": "fake-cf-id",
            "CF_CLIENT_SECRET": "fake-cf-secret"
        }
        return values.get(key)

    with patch("altiplano.server._conf", side_effect=mock_conf):
        headers = _headers()
        assert headers["Authorization"] == "Bearer fake-token"
        assert headers["CF-Access-Client-Id"] == "fake-cf-id"
        assert headers["CF-Access-Client-Secret"] == "fake-cf-secret"
