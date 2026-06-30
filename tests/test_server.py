import pytest
from unittest.mock import patch, AsyncMock, MagicMock
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
        "search_tasks",
        "get_bucket_tasks",
        "get_task",
        "create_task",
        "update_task",
        "set_reminders",
        "list_labels",
        "create_label",
        "update_label",
        "delete_label",
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
        "list_task_attachments",
        "delete_task_attachment",
        "get_task_frontend_url",
        "upload_task_attachment_base64",
        "upload_task_attachment_from_url",
        "delete_task",
        "delete_comment",
        "delete_bucket",
        "list_task_relations",
        "add_task_relation",
        "remove_task_relation",
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
            "identifier": "",               # carried over as default empty string
            "updated": "2023-01-01T00:00:00Z",
        },
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_project_identifier(mock_request):
    """Test updating the project identifier and verifying that it is preserved when other fields are updated."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1":
            return {
                "id": 1,
                "title": "Project Title",
                "description": "desc",
                "hex_color": "aabbcc",
                "parent_project_id": 0,
                "identifier": "SHOP",
                "updated": "2023-01-01T00:00:00Z",
            }
        if method == "POST" and path == "/projects/1":
            return {"id": 1, "title": "Project Title", "updated": "2023-01-01T00:00:00Z"}
        return {}

    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import update_project

    # Case 1: Update the identifier to a new value
    await update_project(project_id=1, identifier="NEWSHOP")
    mock_request.assert_any_call(
        "POST",
        "/projects/1",
        json={
            "title": "Project Title",
            "description": "desc",
            "hex_color": "aabbcc",
            "parent_project_id": 0,
            "identifier": "NEWSHOP",
            "updated": "2023-01-01T00:00:00Z",
        },
    )

    # Case 2: Update another field (e.g. hex_color) and verify that the existing identifier "SHOP" is preserved
    mock_request.reset_mock()
    await update_project(project_id=1, hex_color="112233")
    mock_request.assert_any_call(
        "POST",
        "/projects/1",
        json={
            "title": "Project Title",
            "description": "desc",
            "hex_color": "112233",
            "parent_project_id": 0,
            "identifier": "SHOP",
            "updated": "2023-01-01T00:00:00Z",
        },
    )

    # Case 3: Clear the identifier by passing ""
    mock_request.reset_mock()
    await update_project(project_id=1, identifier="")
    mock_request.assert_any_call(
        "POST",
        "/projects/1",
        json={
            "title": "Project Title",
            "description": "desc",
            "hex_color": "aabbcc",
            "parent_project_id": 0,
            "identifier": "",
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
async def test_tool_set_reminders(mock_request):
    """Test the set_reminders tool merges caller changes onto the full current task to prevent data loss."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/tasks/1":
            return {
                "id": 1,
                "title": "Task with Reminders",
                "description": "Don't lose this description",
                "done": False,
                "priority": 3,
                "due_date": "2026-06-30T23:59:00+02:00",
                "start_date": None,
                "end_date": None,
                "updated": "2023-01-01T00:00:00Z"
            }
        if method == "POST" and path == "/tasks/1":
            return {"id": 1, "title": "Task with Reminders", "updated": "2023-01-01T00:00:00Z"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import set_reminders
    result = await set_reminders(task_id=1, reminders=["2026-06-30T09:00:00+02:00"])
    
    assert mock_request.call_count == 2
    mock_request.assert_any_call("GET", "/tasks/1")
    # POST payload must include all existing fields plus the new reminders
    mock_request.assert_any_call(
        "POST",
        "/tasks/1",
        json={
            "title": "Task with Reminders",
            "description": "Don't lose this description",
            "done": False,
            "priority": 3,
            "due_date": "2026-06-30T23:59:00+02:00",
            "start_date": None,
            "end_date": None,
            "reminders": [{"reminder": "2026-06-30T09:00:00+02:00"}],
            "updated": "2023-01-01T00:00:00Z",
        },
    )


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
async def test_tool_create_project_with_identifier(mock_request):
    """Test the create_project tool with identifier parameter."""
    mock_request.return_value = {
        "id": 1,
        "title": "New Project",
        "description": "A new project",
        "hex_color": "00ff00",
        "parent_project_id": 0,
        "identifier": "SHOP"
    }

    from altiplano.server import create_project
    result = await create_project(
        title="New Project",
        description="A new project",
        hex_color="00ff00",
        identifier="SHOP"
    )

    assert result["id"] == 1
    assert result["title"] == "New Project"
    # Verify that create_project sent the identifier in the payload
    mock_request.assert_called_once_with(
        "PUT",
        "/projects",
        json={
            "title": "New Project",
            "description": "A new project",
            "hex_color": "00ff00",
            "identifier": "SHOP"
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


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_task_attachments(mock_request):
    """Test list_task_attachments tool."""
    mock_request.return_value = [
        {
            "id": 42,
            "file": {"name": "test_file.png", "size": 12345},
            "created": "2023-01-01T00:00:00Z"
        },
        {
            "id": 43,
            "name": "other_file.txt",
            "size": 54321,
            "created": "2023-01-02T00:00:00Z"
        }
    ]
    from altiplano.server import list_task_attachments
    result = await list_task_attachments(task_id=1)
    assert result == [
        {"id": 42, "name": "test_file.png", "size": 12345, "created": "2023-01-01T00:00:00Z"},
        {"id": 43, "name": "other_file.txt", "size": 54321, "created": "2023-01-02T00:00:00Z"}
    ]
    mock_request.assert_called_once_with("GET", "/tasks/1/attachments")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_delete_task_attachment(mock_request):
    """Test delete_task_attachment tool."""
    mock_request.return_value = {"ok": True}
    from altiplano.server import delete_task_attachment
    result = await delete_task_attachment(task_id=1, attachment_id=42)
    assert result == {"ok": True}
    mock_request.assert_called_once_with("DELETE", "/tasks/1/attachments/42")


@pytest.mark.anyio
async def test_tool_get_task_frontend_url():
    """Test get_task_frontend_url tool."""
    from altiplano.server import get_task_frontend_url
    with patch("altiplano.server._conf", return_value="https://tasks.melbjo.win/api/v1"):
        url = await get_task_frontend_url(task_id=5)
        assert url == "https://tasks.melbjo.win/tasks/5"


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_upload_task_attachment_base64(mock_request):
    """Test upload_task_attachment_base64 tool."""
    mock_request.return_value = {"id": 100}
    from altiplano.server import upload_task_attachment_base64
    
    # 1. Successful upload
    content = "SGVsbG8gV29ybGQh"  # "Hello World!" in base64
    result = await upload_task_attachment_base64(task_id=1, filename="hello.txt", content_base64=content)
    assert result == {"id": 100}
    
    # Verify the mocked request payload
    called_args, called_kwargs = mock_request.call_args
    assert called_args == ("PUT", "/tasks/1/attachments")
    assert "files" in called_kwargs
    assert called_kwargs["files"]["files"][0] == "hello.txt"
    assert called_kwargs["files"]["files"][1] == b"Hello World!"

    # 2. Exceed limit (2MB limit). Construct a string that exceeds 2.66 million characters
    too_large_content = "A" * (3 * 1024 * 1024)
    with pytest.raises(ValueError, match="File exceeds 2MB limit"):
        await upload_task_attachment_base64(task_id=1, filename="large.txt", content_base64=too_large_content)


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
@patch("httpx.AsyncClient")
async def test_tool_upload_task_attachment_from_url(mock_client_class, mock_request):
    """Test upload_task_attachment_from_url tool."""
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = b"Downloaded content"
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response

    mock_request.return_value = {"id": 101}
    from altiplano.server import upload_task_attachment_from_url
    
    result = await upload_task_attachment_from_url(task_id=2, url="https://example.com/some/file.pdf?query=1")
    assert result == {"id": 101}

    mock_client.get.assert_called_once_with("https://example.com/some/file.pdf?query=1")
    called_args, called_kwargs = mock_request.call_args
    assert called_args == ("PUT", "/tasks/2/attachments")
    assert "files" in called_kwargs
    assert called_kwargs["files"]["files"][0] == "file.pdf"
    assert called_kwargs["files"]["files"][1] == b"Downloaded content"


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_delete_task(mock_request):
    """Test delete_task tool."""
    from altiplano.server import delete_task

    # 1. Without confirmation (should raise ValueError)
    with pytest.raises(ValueError, match="DANGER: This is a destructive operation"):
        await delete_task(task_id=123, confirm=False)
    
    # 2. With confirmation
    mock_request.return_value = {"ok": True}
    res = await delete_task(task_id=123, confirm=True)
    assert res == {"ok": True}
    mock_request.assert_called_once_with("DELETE", "/tasks/123")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_delete_comment(mock_request):
    """Test delete_comment tool."""
    from altiplano.server import delete_comment

    # 1. Without confirmation (should raise ValueError)
    with pytest.raises(ValueError, match="DANGER: This is a destructive operation"):
        await delete_comment(task_id=123, comment_id=456, confirm=False)
    
    # 2. With confirmation
    mock_request.return_value = {"ok": True}
    res = await delete_comment(task_id=123, comment_id=456, confirm=True)
    assert res == {"ok": True}
    mock_request.assert_called_once_with("DELETE", "/tasks/123/comments/456")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_delete_bucket(mock_request):
    """Test delete_bucket tool."""
    from altiplano.server import delete_bucket

    # 1. Without confirmation (should raise ValueError)
    with pytest.raises(ValueError, match="DANGER: This is a destructive operation"):
        await delete_bucket(project_id=1, bucket_id=2, confirm=False)
    
    # 2. With confirmation (should mock resolve view id as well)
    async def mock_req_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "DELETE" and path == "/projects/1/views/10/buckets/2":
            return {"ok": True}
        return None

    mock_request.side_effect = mock_req_side_effect
    res = await delete_bucket(project_id=1, bucket_id=2, confirm=True)
    assert res == {"ok": True}
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call("DELETE", "/projects/1/views/10/buckets/2")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_task_relations(mock_request):
    """Test list_task_relations tool."""
    mock_request.return_value = {
        "id": 1,
        "title": "Base Task",
        "related_tasks": [
            {
                "id": 2,
                "title": "Subtask Task",
                "relation_kind": "subtask",
                "done": False,
                "priority": 3,
            },
            {
                "id": 3,
                "title": "Blocking Task",
                "relation_kind": "blocking",
                "done": True,
                "priority": 0,
            }
        ]
    }
    from altiplano.server import list_task_relations
    result = await list_task_relations(task_id=1)
    assert result == [
        {"id": 2, "title": "Subtask Task", "relation_kind": "subtask", "done": False, "priority": 3},
        {"id": 3, "title": "Blocking Task", "relation_kind": "blocking", "done": True, "priority": 0}
    ]
    mock_request.assert_called_once_with("GET", "/tasks/1")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_task_relations_empty(mock_request):
    """Test list_task_relations tool when there are no related tasks."""
    mock_request.return_value = {"id": 1, "title": "Base Task"}
    from altiplano.server import list_task_relations
    result = await list_task_relations(task_id=1)
    assert result == []
    mock_request.assert_called_once_with("GET", "/tasks/1")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_task_relations_dict(mock_request):
    """Test list_task_relations tool with a dictionary of related tasks (grouped by kind)."""
    mock_request.return_value = {
        "id": 1,
        "title": "Base Task",
        "related_tasks": {
            "subtask": [
                {
                    "id": 2,
                    "title": "Subtask Task",
                    "done": False,
                    "priority": 3,
                }
            ],
            "blocking": [
                {
                    "id": 3,
                    "title": "Blocking Task",
                    "done": True,
                    "priority": 0,
                }
            ]
        }
    }
    from altiplano.server import list_task_relations
    result = await list_task_relations(task_id=1)
    assert len(result) == 2
    
    subtask = next(r for r in result if r["id"] == 2)
    assert subtask["relation_kind"] == "subtask"
    assert subtask["title"] == "Subtask Task"
    
    blocking = next(r for r in result if r["id"] == 3)
    assert blocking["relation_kind"] == "blocking"
    assert blocking["title"] == "Blocking Task"
    
    mock_request.assert_called_once_with("GET", "/tasks/1")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_add_task_relation(mock_request):
    """Test add_task_relation tool."""
    mock_request.return_value = {"id": 1, "other_task_id": 2, "relation_kind": "subtask"}
    from altiplano.server import add_task_relation
    result = await add_task_relation(task_id=1, other_task_id=2, relation_kind="subtask")
    assert result == {"id": 1, "other_task_id": 2, "relation_kind": "subtask"}
    mock_request.assert_called_once_with(
        "PUT",
        "/tasks/1/relations",
        json={"other_task_id": 2, "relation_kind": "subtask"}
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_remove_task_relation(mock_request):
    """Test remove_task_relation tool."""
    mock_request.return_value = {"ok": True}
    from altiplano.server import remove_task_relation
    result = await remove_task_relation(task_id=1, other_task_id=2, relation_kind="subtask")
    assert result == {"ok": True}
    mock_request.assert_called_once_with("DELETE", "/tasks/1/relations/subtask/2")


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_label(mock_request):
    """Test create_label tool."""
    mock_request.return_value = {
        "id": 10,
        "title": "Priority Label",
        "description": "High priority tasks",
        "hex_color": "ff0000"
    }
    from altiplano.server import create_label
    result = await create_label(title="Priority Label", description="High priority tasks", hex_color="ff0000")
    assert result["id"] == 10
    assert result["title"] == "Priority Label"
    mock_request.assert_called_once_with(
        "PUT",
        "/labels",
        json={"title": "Priority Label", "description": "High priority tasks", "hex_color": "ff0000"}
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_update_label(mock_request):
    """Test update_label tool."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/labels/10":
            return {
                "id": 10,
                "title": "Old Label",
                "description": "Old desc",
                "hex_color": "aabbcc",
                "updated": "2023-01-01T00:00:00Z"
            }
        if method == "POST" and path == "/labels/10":
            return {"id": 10, "title": "New Label", "description": "Old desc", "hex_color": "ff0000"}
        return {}
    mock_request.side_effect = mock_request_side_effect
    from altiplano.server import update_label
    result = await update_label(label_id=10, title="New Label", hex_color="ff0000")
    assert result["title"] == "New Label"
    mock_request.assert_any_call("GET", "/labels/10")
    mock_request.assert_any_call(
        "POST",
        "/labels/10",
        json={
            "title": "New Label",
            "description": "Old desc",
            "hex_color": "ff0000",
            "updated": "2023-01-01T00:00:00Z"
        }
    )


@pytest.mark.anyio
async def test_tool_update_label_no_fields():
    """Test update_label raises ValueError if no fields are provided."""
    from altiplano.server import update_label
    with pytest.raises(ValueError, match="No fields to update"):
        await update_label(label_id=10)


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_delete_label(mock_request):
    """Test delete_label tool with and without confirm."""
    from altiplano.server import delete_label
    
    # Case 1: without confirm, raises ValueError
    with pytest.raises(ValueError, match="DANGER"):
        await delete_label(label_id=10, confirm=False)
        
    # Case 2: with confirm
    mock_request.return_value = {"ok": True}
    result = await delete_label(label_id=10, confirm=True)
    assert result == {"ok": True}
    mock_request.assert_called_once_with("DELETE", "/labels/10")



def test_main_transport_selection(monkeypatch):
    """Test that main() correctly selects transport and configures FastMCP settings."""
    from altiplano.server import main, mcp

    # Save original settings to restore them after the test
    orig_host = mcp.settings.host
    orig_port = mcp.settings.port
    orig_allowed_hosts = list(mcp.settings.transport_security.allowed_hosts)
    orig_dns_rebinding = mcp.settings.transport_security.enable_dns_rebinding_protection

    try:
        # Case 1: Default stdio
        monkeypatch.delenv("MCP_TRANSPORT", raising=False)
        monkeypatch.delenv("FASTMCP_HOST", raising=False)
        monkeypatch.delenv("FASTMCP_PORT", raising=False)
        monkeypatch.delenv("FASTMCP_ALLOWED_HOSTS", raising=False)
        monkeypatch.delenv("FASTMCP_DISABLE_DNS_REBINDING", raising=False)

        with patch.object(mcp, "run") as mock_run:
            main()
            mock_run.assert_called_once_with()

        # Case 2: SSE transport with custom host and port
        monkeypatch.setenv("MCP_TRANSPORT", "sse")
        monkeypatch.setenv("FASTMCP_HOST", "0.0.0.0")
        monkeypatch.setenv("FASTMCP_PORT", "9000")
        monkeypatch.setenv("FASTMCP_ALLOWED_HOSTS", "test.local, api.test.local")
        monkeypatch.setenv("FASTMCP_DISABLE_DNS_REBINDING", "true")

        with patch.object(mcp, "run") as mock_run:
            main()
            mock_run.assert_called_once_with(transport="sse")
            assert mcp.settings.host == "0.0.0.0"
            assert mcp.settings.port == 9000
            assert "test.local" in mcp.settings.transport_security.allowed_hosts
            assert "api.test.local" in mcp.settings.transport_security.allowed_hosts
            assert mcp.settings.transport_security.enable_dns_rebinding_protection is False

        # Case 3: Streamable HTTP transport
        monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
        monkeypatch.setenv("FASTMCP_HOST", "127.0.0.1")
        monkeypatch.setenv("FASTMCP_PORT", "8888")
        monkeypatch.setenv("FASTMCP_DISABLE_DNS_REBINDING", "false")

        # Let's reset the rebinding protection first to test changing it back
        mcp.settings.transport_security.enable_dns_rebinding_protection = True

        with patch.object(mcp, "run") as mock_run:
            main()
            mock_run.assert_called_once_with(transport="streamable-http")
            assert mcp.settings.host == "127.0.0.1"
            assert mcp.settings.port == 8888
            # (Note: "false" does not disable it, so it should stay True)
            assert mcp.settings.transport_security.enable_dns_rebinding_protection is True

    finally:
        # Restore original settings
        mcp.settings.host = orig_host
        mcp.settings.port = orig_port
        mcp.settings.transport_security.allowed_hosts = orig_allowed_hosts
        mcp.settings.transport_security.enable_dns_rebinding_protection = orig_dns_rebinding


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_task_no_labels(mock_request):
    """Test create_task without label_ids."""
    mock_request.return_value = {
        "id": 100,
        "title": "Task without labels",
        "description": "Desc",
        "priority": 1,
    }
    
    from altiplano.server import create_task
    result = await create_task(project_id=1, title="Task without labels", description="Desc", priority=1)
    
    assert result["id"] == 100
    assert "label_errors" not in result
    mock_request.assert_called_once_with(
        "PUT",
        "/projects/1/tasks",
        json={"title": "Task without labels", "description": "Desc", "priority": 1}
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_task_with_labels_success(mock_request):
    """Test create_task with labels successfully added."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "PUT" and path == "/projects/1/tasks":
            return {"id": 100, "title": "Task with labels"}
        if method == "PUT" and path.startswith("/tasks/100/labels"):
            return {"ok": True}
        return {}
        
    mock_request.side_effect = mock_request_side_effect
    
    from altiplano.server import create_task
    result = await create_task(project_id=1, title="Task with labels", label_ids=[5, 6])
    
    assert result["id"] == 100
    assert "label_errors" not in result
    
    # Assert calls
    mock_request.assert_any_call("PUT", "/projects/1/tasks", json={"title": "Task with labels"})
    mock_request.assert_any_call("PUT", "/tasks/100/labels", json={"label_id": 5})
    mock_request.assert_any_call("PUT", "/tasks/100/labels", json={"label_id": 6})
    assert mock_request.call_count == 3


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_create_task_with_labels_partial_error(mock_request):
    """Test create_task where some label additions fail but task is still created."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "PUT" and path == "/projects/1/tasks":
            return {"id": 100, "title": "Task with label error"}
        if method == "PUT" and path == "/tasks/100/labels":
            label_id = kwargs.get("json", {}).get("label_id")
            if label_id == 6:
                raise RuntimeError("Vikunja API error 404: Label not found")
            return {"ok": True}
        return {}
        
    mock_request.side_effect = mock_request_side_effect
    
    from altiplano.server import create_task
    result = await create_task(project_id=1, title="Task with label error", label_ids=[5, 6])
    
    assert result["id"] == 100
    assert "label_errors" in result
    assert len(result["label_errors"]) == 1
    assert "Label not found" in result["label_errors"][0]
    
    mock_request.assert_any_call("PUT", "/projects/1/tasks", json={"title": "Task with label error"})
    mock_request.assert_any_call("PUT", "/tasks/100/labels", json={"label_id": 5})
    mock_request.assert_any_call("PUT", "/tasks/100/labels", json={"label_id": 6})
    assert mock_request.call_count == 3


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_search_tasks_isolated_text(mock_request):
    """Test search_tasks with only text query, using the s query parameter."""
    mock_request.return_value = [{"id": 1, "title": "Tandoor Recipe", "done": False}]
    
    from altiplano.server import search_tasks
    result = await search_tasks(text="Tandoor")
    
    assert len(result) == 1
    assert result[0]["title"] == "Tandoor Recipe"
    mock_request.assert_called_once_with(
        "GET",
        "/tasks",
        params={
            "page": 1,
            "per_page": 50,
            "s": "Tandoor",
            "filter_timezone": "Europe/Zurich"
        }
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_search_tasks_combined(mock_request):
    """Test search_tasks with text search combined with structured filters."""
    mock_request.return_value = []
    
    from altiplano.server import search_tasks
    await search_tasks(
        text="Tandoor",
        done=False,
        project_id=12,
        priority_min=4,
        label_ids=[1, 2]
    )
    
    mock_request.assert_called_once_with(
        "GET",
        "/tasks",
        params={
            "page": 1,
            "per_page": 50,
            "filter": "project = 12 && done = false && labels in 1, 2 && priority >= 4 && (title ~ 'Tandoor' || description ~ 'Tandoor')",
            "filter_timezone": "Europe/Zurich"
        }
    )


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_search_tasks_sorting_validation(mock_request):
    """Test search_tasks validation of sort_by and order_by parameters."""
    from altiplano.server import search_tasks
    
    # Validation error if order_by specified without sort_by
    with pytest.raises(ValueError, match="sort_by is required when order_by is specified"):
        await search_tasks(order_by=["asc"])
        
    # Validation error if mismatch in lengths
    with pytest.raises(ValueError, match="order_by and sort_by must have the same length"):
        await search_tasks(sort_by=["due_date", "priority"], order_by=["asc"])

    # Validation error if invalid order_by value
    with pytest.raises(ValueError, match="order_by values must be 'asc' or 'desc'"):
        await search_tasks(sort_by=["due_date"], order_by=["invalid"])


@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_get_bucket_tasks(mock_request):
    """Test get_bucket_tasks resolves view_id and fetches tasks with bucket filter."""
    async def mock_request_side_effect(method, path, **kwargs):
        if method == "GET" and path == "/projects/1/views":
            return [{"id": 10, "view_kind": "kanban"}]
        if method == "GET" and path == "/projects/1/views/10/tasks":
            return [{"id": 42, "title": "Bucket Task", "bucket_id": 20}]
        return {}
    mock_request.side_effect = mock_request_side_effect
    
    from altiplano.server import get_bucket_tasks
    result = await get_bucket_tasks(project_id=1, bucket_id=20)
    
    assert len(result) == 1
    assert result[0]["title"] == "Bucket Task"
    
    mock_request.assert_any_call("GET", "/projects/1/views")
    mock_request.assert_any_call(
        "GET",
        "/projects/1/views/10/tasks",
        params={
            "filter": "bucket_id = 20",
            "sort_by": "position",
            "order_by": "asc",
            "page": 1,
            "per_page": 50
        }
    )





