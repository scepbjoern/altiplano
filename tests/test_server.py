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
        "remove_assignee",
        "update_project",
        "complete_task",
        "move_task_to_project",
        "list_buckets",
        "create_bucket",
        "update_bucket",
        "move_task_to_bucket",
    ]
    
    for tool in expected_tools:
        assert tool in tool_names


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_projects(mock_request):
    """Test the list_projects tool using API mocks."""
    # Set mock response for the _request call
    mock_request.return_value = [
        {
            "id": 1,
            "title": "Test Project",
            "parent_project_id": 0,
            "is_archived": False,
            "hex_color": "00ff00",
            "identifier": "TP",
            "description": "Test project description"
        }
    ]

    result = await list_projects()

    # Assert return value format matching list_projects tool output
    assert result == [
        {
            "id": 1,
            "title": "Test Project",
            "parent_project_id": 0,
            "is_archived": False,
            "hex_color": "00ff00",
            "identifier": "TP",
            "description": "Test project description",
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


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_project(mock_request):
    """Test that update_project merges caller changes onto the full current project."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1":
            return {
                "id": 1,
                "title": "Old Title",
                "description": "Old desc",
                "hex_color": "aabbcc",
                "parent_project_id": 0,
                "updated": "2023-01-01T00:00:00Z",
            }
        if method == "POST" and path == "/projects/1":
            return {"id": 1, "title": "Updated Title", "hex_color": "00ff00", "updated": "2023-01-01T00:00:00Z"}
        return {}

    mock_request.side_effect = mock_request_side_effect

    from altiplano.server import update_project

    result = await update_project(project_id=1, title="Updated Title", hex_color="00ff00")

    assert result["id"] == 1
    assert result["title"] == "Updated Title"
    mock_request.assert_any_call("GET", "/projects/1")
    # POST payload must include all fields (title mandatory) with changes overlaid
    mock_request.assert_any_call(
        "POST",
        "/projects/1",
        json={
            "title": "Updated Title",       # changed
            "description": "Old desc",      # carried over from GET
            "hex_color": "00ff00",          # changed
            "parent_project_id": 0,         # carried over from GET
            "updated": "2023-01-01T00:00:00Z",
        },
    )


@pytest.mark.anyio
async def test_tool_update_project_no_fields():
    """Test that update_project raises ValueError if no fields are provided."""
    from altiplano.server import update_project

    with pytest.raises(ValueError, match="No fields to update"):
        await update_project(project_id=1)


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_complete_task(mock_request):
    """Test the complete_task tool without comment."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {"id": 1, "title": "Test Task", "done": False, "updated": "2023-01-01T00:00:00Z"}
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "done": True, "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import complete_task
    result = await complete_task(task_id=1)
    assert result == {"id": 1, "done": True, "updated": "2023-01-01T00:00:00Z"}
    mock_request.assert_any_call("GET", "/tasks/1")
    mock_request.assert_any_call("POST", "/tasks/1", json={"title": "Test Task", "done": True, "updated": "2023-01-01T00:00:00Z"})


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_complete_task_with_comment(mock_request):
    """Test the complete_task tool with a comment."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {"id": 1, "title": "Test Task", "done": False, "updated": "2023-01-01T00:00:00Z"}
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "done": True, "updated": "2023-01-01T00:00:00Z"}
        if method == "PUT" and path == "/tasks/1/comments":
            return {"comment": "Finished this!"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import complete_task
    result = await complete_task(task_id=1, comment="Finished this!")
    assert result == {"id": 1, "done": True, "updated": "2023-01-01T00:00:00Z", "comment_added": True}

    assert mock_request.call_count == 3
    mock_request.assert_any_call("GET", "/tasks/1")
    mock_request.assert_any_call("POST", "/tasks/1", json={"title": "Test Task", "done": True, "updated": "2023-01-01T00:00:00Z"})
    mock_request.assert_any_call("PUT", "/tasks/1/comments", json={"comment": "Finished this!"})


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_move_task_to_project(mock_request):
    """Test the move_task_to_project tool preserving done status and including title."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {"id": 1, "title": "Task to Move", "done": True, "updated": "2023-01-01T00:00:00Z"}
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "project_id": 2, "done": True, "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import move_task_to_project
    result = await move_task_to_project(task_id=1, project_id=2)
    assert result == {"id": 1, "project_id": 2, "done": True, "updated": "2023-01-01T00:00:00Z"}

    assert mock_request.call_count == 2
    mock_request.assert_any_call("GET", "/tasks/1")
    mock_request.assert_any_call("POST", "/tasks/1", json={"title": "Task to Move", "project_id": 2, "done": True, "updated": "2023-01-01T00:00:00Z"})


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_task(mock_request):
    """Test the update_task tool merges caller changes onto the full current task."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {
                "id": 1,
                "title": "Old Title",
                "description": "Old description",
                "done": False,
                "priority": 2,
                "due_date": None,
                "start_date": None,
                "end_date": None,
                "updated": "2023-01-01T00:00:00Z"
            }
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "title": "New Title", "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import update_task
    result = await update_task(task_id=1, title="New Title")
    assert result == {"id": 1, "title": "New Title", "updated": "2023-01-01T00:00:00Z"}
    mock_request.assert_any_call("GET", "/tasks/1")
    mock_request.assert_any_call(
        "POST",
        "/tasks/1",
        json={
            "title": "New Title",
            "description": "Old description",
            "done": False,
            "priority": 2,
            "due_date": None,
            "start_date": None,
            "end_date": None,
            "updated": "2023-01-01T00:00:00Z",
        }
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_task_partial(mock_request):
    """Test that update_task sends title even when only changing other fields."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {
                "id": 1,
                "title": "Task Title",
                "description": "Old description",
                "done": False,
                "priority": 0,
                "due_date": None,
                "start_date": None,
                "end_date": None,
                "updated": "2023-01-01T00:00:00Z"
            }
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "description": "New description", "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import update_task
    result = await update_task(task_id=1, description="New description")
    mock_request.assert_any_call(
        "POST",
        "/tasks/1",
        json={
            "title": "Task Title",
            "description": "New description",
            "done": False,
            "priority": 0,
            "due_date": None,
            "start_date": None,
            "end_date": None,
            "updated": "2023-01-01T00:00:00Z",
        }
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_set_reminders(mock_request):
    """Test the set_reminders tool including updated timestamp and title."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {"id": 1, "title": "Test Task", "updated": "2023-01-01T00:00:00Z"}
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "reminders": [{"reminder": "2023-02-02T12:00:00Z"}], "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import set_reminders
    result = await set_reminders(task_id=1, reminders=["2023-02-02T12:00:00Z"])
    assert result["id"] == 1
    mock_request.assert_any_call("GET", "/tasks/1")
    mock_request.assert_any_call("POST", "/tasks/1", json={"title": "Test Task", "reminders": [{"reminder": "2023-02-02T12:00:00Z"}], "updated": "2023-01-01T00:00:00Z"})


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_project(mock_request):
    """Test the create_project tool with hex_color parameter."""
    mock_request.return_value = {
        "id": 1,
        "title": "New Project",
        "description": "A new project",
        "hex_color": "00ff00",
        "parent_project_id": 0,
        "identifier": "NP"
    }

    from altiplano.server import create_project
    result = await create_project(
        title="New Project",
        description="A new project",
        hex_color="00ff00"
    )

    assert result["id"] == 1
    assert result["title"] == "New Project"
    # Verify that create_project sent the hex_color in the payload
    mock_request.assert_called_once_with(
        "PUT",
        "/projects",
        json={
            "title": "New Project",
            "description": "A new project",
            "hex_color": "00ff00"
        }
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_buckets(mock_request):
    """Test the list_buckets tool."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "GET" and path == "/projects/1/views/10/buckets":
            return [
                {
                    "id": 20,
                    "title": "Backlog",
                    "limit": 5,
                    "position": 1,
                    "count": 2,
                    "created_by": {},
                }
            ]
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import list_buckets
    result = await list_buckets(project_id=1)
    assert result == [
        {
            "id": 20,
            "title": "Backlog",
            "limit": 5,
            "position": 1,
            "count": 2,
        }
    ]
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call("GET", "/projects/1/views/10/buckets")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_bucket(mock_request):
    """Test the create_bucket tool."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "PUT" and path == "/projects/1/views/10/buckets":
            return {"id": 20, "title": "In Progress", "limit": 3}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import create_bucket
    result = await create_bucket(project_id=1, title="In Progress", limit=3)
    assert result["id"] == 20
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call("PUT", "/projects/1/views/10/buckets", json={"title": "In Progress", "limit": 3})


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_bucket(mock_request):
    """Test the update_bucket tool."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "GET" and path == "/projects/1/views/10/buckets":
            return [{"id": 20, "title": "Old Title", "limit": 5, "updated": "2023-01-01"}]
        if method == "POST" and path == "/projects/1/views/10/buckets/20":
            return {"id": 20, "title": "New Title", "limit": 5}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import update_bucket
    result = await update_bucket(project_id=1, bucket_id=20, title="New Title")
    assert result["id"] == 20
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call("GET", "/projects/1/views/10/buckets")
    mock_request.assert_any_call(
        "POST",
        "/projects/1/views/10/buckets/20",
        json={"title": "New Title", "limit": 5, "updated": "2023-01-01"},
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_bucket_edge_cases(mock_request):
    """Test error handling in update_bucket."""
    from altiplano.server import update_bucket
    
    # 1. ValueError if no fields updated
    with pytest.raises(ValueError, match="No fields to update"):
        await update_bucket(project_id=1, bucket_id=20)
        
    # 2. RuntimeError if bucket not found
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "GET" and path == "/projects/1/views/10/buckets":
            return [{"id": 99, "title": "Some Other Bucket"}]
        return {}
    mock_request.side_effect = mock_request_side_effect
    with pytest.raises(RuntimeError, match="Bucket 20 not found in project 1"):
        await update_bucket(project_id=1, bucket_id=20, title="New Title")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_move_task_to_bucket(mock_request):
    """Test the move_task_to_bucket tool."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/50":
            return {"id": 50, "project_id": 1}
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "POST" and path == "/projects/1/views/10/buckets/20/tasks":
            return {"ok": True}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import move_task_to_bucket
    result = await move_task_to_bucket(task_id=50, bucket_id=20)
    assert result == {"ok": True}
    mock_request.assert_any_call("GET", "/tasks/50")
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call(
        "POST",
        "/projects/1/views/10/buckets/20/tasks",
        json={"task_id": 50},
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_resolve_kanban_view_id_missing(mock_request):
    """Test helper resolve_kanban_view_id when Kanban view is missing."""
    mock_request.return_value = [{"id": 10, "view_kind": "list"}]
    from altiplano.server import list_buckets
    with pytest.raises(RuntimeError, match="Project 1 has no Kanban view"):
        await list_buckets(project_id=1)

