"""Minimal Vikunja MCP server.

Filtering and sorting are passed straight to the Vikunja API (server-side),
so there is no client-side filtering engine to get wrong.

Credentials are resolved without storing secrets in a shared mcp.json:
  1. Environment variables VIKUNJA_URL / VIKUNJA_API_TOKEN (preferred).
  2. A per-device file of KEY=VALUE lines (default ~/.config/altiplano/env,
     override with ALTIPLANO_CONFIG). Keep it chmod 600.
"""

import base64
import os
from pathlib import Path
from typing import Any, Literal

RelationKind = Literal[
    "subtask",
    "parenttask",
    "related",
    "duplicateof",
    "duplicates",
    "blocking",
    "blockedby",
    "precedes",
    "follows",
    "copiedfrom",
    "copiedto",
]

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("altiplano")

_CONFIG_FILE = Path(
    os.environ.get("ALTIPLANO_CONFIG", Path.home() / ".config" / "altiplano" / "env")
)


def _from_file(key: str) -> str | None:
    try:
        for line in _CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    except FileNotFoundError:
        return None
    return None


def _conf(key: str) -> str | None:
    return os.environ.get(key) or _from_file(key)


def _base() -> str:
    url = _conf("VIKUNJA_URL")
    if not url:
        raise RuntimeError("VIKUNJA_URL is not set (env or ~/.config/altiplano/env)")
    return url.rstrip("/")


def _headers() -> dict[str, str]:
    token = _conf("VIKUNJA_API_TOKEN")
    if not token:
        raise RuntimeError("VIKUNJA_API_TOKEN is not set (env or ~/.config/altiplano/env)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    cf_id = _conf("CF_CLIENT_ID")
    cf_secret = _conf("CF_CLIENT_SECRET")
    if cf_id:
        headers["CF-Access-Client-Id"] = cf_id
    if cf_secret:
        headers["CF-Access-Client-Secret"] = cf_secret
        
    return headers


async def _request(method: str, path: str, **kwargs: Any) -> Any:
    headers = _headers()
    if "files" in kwargs:
        headers.pop("Content-Type", None)
    async with httpx.AsyncClient(base_url=_base(), headers=headers, timeout=30) as client:
        r = await client.request(method, path, **kwargs)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Vikunja returns structured errors: {"code": 3009, "message": "..."}
            # Include the full body so the LLM client can see the exact error.
            try:
                body = exc.response.json()
            except Exception:
                body = exc.response.text
            raise RuntimeError(
                f"Vikunja API error {exc.response.status_code} "
                f"on {method} {path}: {body}"
            ) from exc
        if r.status_code == 204 or not r.content:
            return {"ok": True}
        return r.json()


def _task_summary(t: dict) -> dict:
    return {
        "id": t.get("id"),
        "identifier": t.get("identifier"),
        "title": t.get("title"),
        "done": t.get("done"),
        "priority": t.get("priority"),
    }


async def _resolve_kanban_view_id(project_id: int) -> int:
    views = await _request("GET", f"/projects/{project_id}/views")
    for v in views or []:
        if v.get("view_kind") == "kanban":
            return v["id"]
    raise RuntimeError(
        f"Project {project_id} has no Kanban view; create one in the Vikunja UI first."
    )



# --- projects ---------------------------------------------------------------
##
@mcp.tool()
async def list_projects() -> list[dict]:
    """List all projects (boards). `parent_project_id` shows sub-project nesting."""
    data = await _request("GET", "/projects")
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "parent_project_id": p.get("parent_project_id", 0),
            "is_archived": p.get("is_archived", False),
            "hex_color": p.get("hex_color", ""),
            "identifier": p.get("identifier", ""),
            "description": p.get("description", ""),
        }
        for p in (data or [])
    ]


@mcp.tool()
async def create_project(
    title: str,
    parent_project_id: int | None = None,
    description: str | None = None,
    hex_color: str | None = None,
) -> dict:
    """Create a project. Pass `parent_project_id` to create it as a sub-project.

    Use `hex_color` to set a custom color (e.g. "ff0000").
    """
    payload: dict[str, Any] = {"title": title}
    if parent_project_id is not None:
        payload["parent_project_id"] = parent_project_id
    if description is not None:
        payload["description"] = description
    if hex_color is not None:
        payload["hex_color"] = hex_color
    return await _request("PUT", "/projects", json=payload)


@mcp.tool()
async def update_project(
    project_id: int,
    title: str | None = None,
    description: str | None = None,
    hex_color: str | None = None,
    parent_project_id: int | None = None,
) -> dict:
    """Update a project. Only the fields you pass are changed.

    Use `hex_color` to set a custom color (e.g. "ff0000").
    Use `parent_project_id` to nest the project or set to 0 to make it a root project.
    """
    # Build a dict of only the caller-supplied changes (non-None values).
    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title
    if description is not None:
        changes["description"] = description
    if hex_color is not None:
        changes["hex_color"] = hex_color
    if parent_project_id is not None:
        changes["parent_project_id"] = parent_project_id
    if not changes:
        raise ValueError("No fields to update")

    # Vikunja's POST /projects/{id} requires all fields (title is mandatory).
    # Fetch current state and overlay our changes on top.
    project = await _request("GET", f"/projects/{project_id}")
    payload: dict[str, Any] = {
        "title": project["title"],
        "description": project.get("description", ""),
        "hex_color": project.get("hex_color", ""),
        "parent_project_id": project.get("parent_project_id", 0),
    }
    if "updated" in project:
        payload["updated"] = project["updated"]
    payload.update(changes)

    return await _request("POST", f"/projects/{project_id}", json=payload)


# --- tasks ------------------------------------------------------------------
##
@mcp.tool()
async def list_tasks(
    project_id: int,
    filter: str | None = None,
    sort_by: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> list[dict]:
    """List tasks in a project.

    `filter` and `sort_by` are passed to Vikunja and applied server-side, e.g.
    filter="done = false && priority >= 4", sort_by="priority". Vikunja filters
    then paginates, so results are complete regardless of page size.
    """
    params: dict[str, Any] = {"page": page, "per_page": per_page}
    if filter:
        params["filter"] = filter
    if sort_by:
        params["sort_by"] = sort_by
    data = await _request("GET", f"/projects/{project_id}/tasks", params=params)
    return [_task_summary(t) for t in (data or [])]


@mcp.tool()
async def get_task(task_id: int) -> dict:
    """Get a single task with full detail."""
    return await _request("GET", f"/tasks/{task_id}")


@mcp.tool()
async def create_task(
    project_id: int,
    title: str,
    description: str | None = None,
    priority: int | None = None,
    due_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Create a task in a project.

    `start_date` and `end_date` are ISO 8601 datetimes marking the window you
    plan to work on the task (start work / finish work), distinct from
    `due_date` (the deadline).
    """
    payload: dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description
    if priority is not None:
        payload["priority"] = priority
    if due_date is not None:
        payload["due_date"] = due_date
    if start_date is not None:
        payload["start_date"] = start_date
    if end_date is not None:
        payload["end_date"] = end_date
    return await _request("PUT", f"/projects/{project_id}/tasks", json=payload)


@mcp.tool()
async def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    done: bool | None = None,
    priority: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Update a task. Only the fields you pass are changed. Use `done` to open/close it.

    `start_date` and `end_date` are ISO 8601 datetimes marking the window you
    plan to work on the task (start work / finish work).
    """
    # Build dict of only caller-supplied changes (non-None values).
    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title
    if description is not None:
        changes["description"] = description
    if done is not None:
        changes["done"] = done
    if priority is not None:
        changes["priority"] = priority
    if start_date is not None:
        changes["start_date"] = start_date
    if end_date is not None:
        changes["end_date"] = end_date
    if not changes:
        raise ValueError("No fields to update")

    # Vikunja's POST /tasks/{id} requires all fields (title is mandatory).
    # Fetch current state and overlay our changes on top.
    task = await _request("GET", f"/tasks/{task_id}")
    payload: dict[str, Any] = {
        "title": task["title"],
        "description": task.get("description", ""),
        "done": task.get("done", False),
        "priority": task.get("priority", 0),
        "due_date": task.get("due_date"),
        "start_date": task.get("start_date"),
        "end_date": task.get("end_date"),
    }
    if "updated" in task:
        payload["updated"] = task["updated"]
    payload.update(changes)

    return await _request("POST", f"/tasks/{task_id}", json=payload)


@mcp.tool()
async def set_reminders(task_id: int, reminders: list[str]) -> dict:
    """Replace a task's reminders with the given ISO 8601 datetimes. Empty list clears them."""
    task = await _request("GET", f"/tasks/{task_id}")
    payload: dict[str, Any] = {"title": task["title"], "reminders": [{"reminder": r} for r in reminders]}
    if "updated" in task:
        payload["updated"] = task["updated"]
    return await _request("POST", f"/tasks/{task_id}", json=payload)


@mcp.tool()
async def complete_task(task_id: int, comment: str | None = None) -> dict:
    """Mark a task as done. This is a safe convenience wrapper for update_task.

    If a `comment` is provided, it is added to the task comments.
    """
    task = await _request("GET", f"/tasks/{task_id}")
    payload: dict[str, Any] = {"title": task["title"], "done": True}
    if "updated" in task:
        payload["updated"] = task["updated"]
    res = await _request("POST", f"/tasks/{task_id}", json=payload)
    if comment:
        await _request("PUT", f"/tasks/{task_id}/comments", json={"comment": comment})
        res["comment_added"] = True
    return res


@mcp.tool()
async def move_task_to_project(task_id: int, project_id: int) -> dict:
    """Move a task to another project. This is a safe convenience wrapper for update_task."""
    # Fetch current task state to preserve done status
    task = await _request("GET", f"/tasks/{task_id}")
    is_done = task.get("done", False)
    payload: dict[str, Any] = {"title": task["title"], "project_id": project_id, "done": is_done}
    if "updated" in task:
        payload["updated"] = task["updated"]
    return await _request("POST", f"/tasks/{task_id}", json=payload)


@mcp.tool()
async def delete_task(task_id: int, confirm: bool = False) -> dict:
    """Delete a task.

    This is a destructive operation and requires explicit confirmation.
    """
    # Zuerst Bestätigung prüfen, um unbeabsichtigten Datenverlust durch die KI zu verhindern
    if not confirm:
        raise ValueError("DANGER: This is a destructive operation. You MUST ask the human user for explicit confirmation before proceeding. If the user explicitly approves, call this tool again with confirm=true.")
    return await _request("DELETE", f"/tasks/{task_id}")


# --- buckets (kanban) ---
##
@mcp.tool()
async def list_buckets(project_id: int) -> list[dict]:
    """List Kanban buckets (columns) of a project's Kanban view."""
    view_id = await _resolve_kanban_view_id(project_id)
    data = await _request("GET", f"/projects/{project_id}/views/{view_id}/buckets")
    return [
        {
            "id": b.get("id"),
            "title": b.get("title"),
            "limit": b.get("limit", 0),
            "position": b.get("position"),
            "count": b.get("count", 0),
        }
        for b in (data or [])
    ]


@mcp.tool()
async def create_bucket(project_id: int, title: str, limit: int | None = None) -> dict:
    """Create a new Kanban bucket (column) in a project's Kanban view.

    Use `limit` to cap how many tasks may be placed in this bucket (omit for unlimited).
    """
    view_id = await _resolve_kanban_view_id(project_id)
    payload: dict[str, Any] = {"title": title}
    if limit is not None:
        payload["limit"] = limit
    return await _request("PUT", f"/projects/{project_id}/views/{view_id}/buckets", json=payload)


@mcp.tool()
async def update_bucket(
    project_id: int,
    bucket_id: int,
    title: str | None = None,
    limit: int | None = None,
) -> dict:
    """Update a Kanban bucket. Only the fields you pass are changed."""
    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title
    if limit is not None:
        changes["limit"] = limit
    if not changes:
        raise ValueError("No fields to update")

    view_id = await _resolve_kanban_view_id(project_id)
    buckets = await _request("GET", f"/projects/{project_id}/views/{view_id}/buckets")
    bucket = next((b for b in (buckets or []) if b.get("id") == bucket_id), None)
    if bucket is None:
        raise RuntimeError(f"Bucket {bucket_id} not found in project {project_id}")

    payload: dict[str, Any] = {
        "title": bucket["title"],
        "limit": bucket.get("limit", 0),
    }
    if "updated" in bucket:
        payload["updated"] = bucket["updated"]
    payload.update(changes)

    return await _request(
        "POST", f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}", json=payload
    )


@mcp.tool()
async def move_task_to_bucket(task_id: int, bucket_id: int) -> dict:
    """Move a task into a specific Kanban bucket within its current project."""
    task = await _request("GET", f"/tasks/{task_id}")
    project_id = task["project_id"]
    view_id = await _resolve_kanban_view_id(project_id)
    return await _request(
        "POST",
        f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}/tasks",
        json={"task_id": task_id},
    )


@mcp.tool()
async def delete_bucket(project_id: int, bucket_id: int, confirm: bool = False) -> dict:
    """Delete a Kanban bucket.

    This is a destructive operation and requires explicit confirmation.
    """
    # Zuerst Bestätigung prüfen, um unbeabsichtigten Datenverlust durch die KI zu verhindern
    if not confirm:
        raise ValueError("DANGER: This is a destructive operation. You MUST ask the human user for explicit confirmation before proceeding. If the user explicitly approves, call this tool again with confirm=true.")
    view_id = await _resolve_kanban_view_id(project_id)
    return await _request("DELETE", f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}")


# --- labels -----------------------------------------------------------------
##
@mcp.tool()
async def list_labels() -> list[dict]:
    """List all labels."""
    data = await _request("GET", "/labels")
    return [{"id": x["id"], "title": x["title"]} for x in (data or [])]


@mcp.tool()
async def add_label(task_id: int, label_id: int) -> dict:
    """Attach a label to a task."""
    return await _request("PUT", f"/tasks/{task_id}/labels", json={"label_id": label_id})


@mcp.tool()
async def remove_label(task_id: int, label_id: int) -> dict:
    """Remove a label from a task."""
    return await _request("DELETE", f"/tasks/{task_id}/labels/{label_id}")


@mcp.tool()
async def create_label(
    title: str,
    description: str | None = None,
    hex_color: str | None = None,
) -> dict:
    """Create a new global label.

    Use `hex_color` to set a custom color (e.g. "ff0000").
    """
    # Payload für die Vikunja-API zusammenbauen
    payload: dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description
    if hex_color is not None:
        payload["hex_color"] = hex_color
    return await _request("PUT", "/labels", json=payload)


@mcp.tool()
async def update_label(
    label_id: int,
    title: str | None = None,
    description: str | None = None,
    hex_color: str | None = None,
) -> dict:
    """Update a global label. Only the fields you pass are changed.

    Use `hex_color` to set a custom color (e.g. "ff0000").
    """
    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title
    if description is not None:
        changes["description"] = description
    if hex_color is not None:
        changes["hex_color"] = hex_color
    if not changes:
        raise ValueError("No fields to update")

    # Das aktuelle Label abrufen, da Vikunja beim POST alle Felder (Pflichtfelder) erwartet
    label = await _request("GET", f"/labels/{label_id}")
    payload: dict[str, Any] = {
        "title": label["title"],
        "description": label.get("description", ""),
        "hex_color": label.get("hex_color", ""),
    }
    if "updated" in label:
        payload["updated"] = label["updated"]
    payload.update(changes)

    return await _request("POST", f"/labels/{label_id}", json=payload)


@mcp.tool()
async def delete_label(label_id: int, confirm: bool = False) -> dict:
    """Delete a global label.

    This is a destructive operation and requires explicit confirmation.
    """
    # Sicherheitsprüfung: Löschen erfordert explizite Bestätigung durch den Benutzer
    if not confirm:
        raise ValueError(
            "DANGER: This is a destructive operation. You MUST ask the human user for explicit "
            "confirmation before proceeding. If the user explicitly approves, call this tool again "
            "with confirm=true."
        )
    return await _request("DELETE", f"/labels/{label_id}")



# --- comments ---------------------------------------------------------------
##
@mcp.tool()
async def list_comments(task_id: int) -> list[dict]:
    """List comments on a task."""
    data = await _request("GET", f"/tasks/{task_id}/comments")
    return [
        {"id": c.get("id"), "comment": c.get("comment"), "author": (c.get("author") or {}).get("username")}
        for c in (data or [])
    ]


@mcp.tool()
async def add_comment(task_id: int, comment: str) -> dict:
    """Add a comment to a task."""
    return await _request("PUT", f"/tasks/{task_id}/comments", json={"comment": comment})


@mcp.tool()
async def delete_comment(task_id: int, comment_id: int, confirm: bool = False) -> dict:
    """Delete a comment from a task.

    This is a destructive operation and requires explicit confirmation.
    """
    # Zuerst Bestätigung prüfen, um unbeabsichtigten Datenverlust durch die KI zu verhindern
    if not confirm:
        raise ValueError("DANGER: This is a destructive operation. You MUST ask the human user for explicit confirmation before proceeding. If the user explicitly approves, call this tool again with confirm=true.")
    return await _request("DELETE", f"/tasks/{task_id}/comments/{comment_id}")


# --- attachments ------------------------------------------------------------
##
@mcp.tool()
async def list_task_attachments(task_id: int) -> list[dict]:
    """List attachments on a task."""
    data = await _request("GET", f"/tasks/{task_id}/attachments")
    return [
        {
            "id": a.get("id"),
            "name": a.get("file", {}).get("name") if a.get("file") else a.get("name"),
            "size": a.get("file", {}).get("size") if a.get("file") else a.get("size"),
            "created": a.get("created"),
        }
        for a in (data or [])
    ]


@mcp.tool()
async def delete_task_attachment(task_id: int, attachment_id: int) -> dict:
    """Delete an attachment from a task."""
    return await _request("DELETE", f"/tasks/{task_id}/attachments/{attachment_id}")


@mcp.tool()
async def get_task_frontend_url(task_id: int) -> str:
    """Get the clickable web UI link for a task.
    Use this to tell the user where to manually upload files if the file is too large for Base64 (> 2MB).
    """
    base = _base()
    # Remove trailing /api/v1 if present to get the frontend domain
    if base.endswith("/api/v1"):
        base = base[:-7]
    return f"{base}/tasks/{task_id}"


@mcp.tool()
async def upload_task_attachment_base64(task_id: int, filename: str, content_base64: str) -> dict:
    """Upload a file to a task using a Base64 encoded string.
    DO NOT use this for files larger than 2MB. If the file is >2MB, call `get_task_frontend_url` instead
    and instruct the user to click the link and upload the file manually in the Vikunja UI.
    """
    # Check approximate size (Base64 string length * 0.75 gives bytes)
    if len(content_base64) * 0.75 > 2 * 1024 * 1024:
        raise ValueError("File exceeds 2MB limit. Call get_task_frontend_url and ask user to upload manually.")
    
    file_bytes = base64.b64decode(content_base64)
    # files tuple format for httpx: (filename, content)
    files = {"files": (filename, file_bytes)}
    return await _request("PUT", f"/tasks/{task_id}/attachments", files=files)


@mcp.tool()
async def upload_task_attachment_from_url(task_id: int, url: str) -> dict:
    """Download a file from a public URL and attach it to a task.
    Use this if the user provides a web link to a file they want attached.
    """
    # Extract a filename from the URL, or use a default
    filename = url.split("/")[-1].split("?")[0]
    if not filename:
        filename = "downloaded_attachment"
        
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as dl_client:
        r = await dl_client.get(url)
        r.raise_for_status()
        file_bytes = r.content
        
    files = {"files": (filename, file_bytes)}
    return await _request("PUT", f"/tasks/{task_id}/attachments", files=files)


# --- relations --------------------------------------------------------------
##
@mcp.tool()
async def list_task_relations(task_id: int) -> list[dict]:
    """List all relations of a task."""
    task = await _request("GET", f"/tasks/{task_id}")
    related = task.get("related_tasks")
    
    relations = []
    if isinstance(related, list):
        for r in related:
            if isinstance(r, dict):
                relations.append({
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "relation_kind": r.get("relation_kind"),
                    "done": r.get("done", False),
                    "priority": r.get("priority", 0),
                })
    elif isinstance(related, dict):
        for relation_kind, tasks in related.items():
            if isinstance(tasks, list):
                for r in tasks:
                    if isinstance(r, dict):
                        relations.append({
                            "id": r.get("id"),
                            "title": r.get("title"),
                            "relation_kind": r.get("relation_kind") or relation_kind,
                            "done": r.get("done", False),
                            "priority": r.get("priority", 0),
                        })
    return relations


@mcp.tool()
async def add_task_relation(task_id: int, other_task_id: int, relation_kind: RelationKind) -> dict:
    """Create a relation between this task and another task.
    
    Common relation kinds are: subtask, parenttask, related, duplicateof, duplicates,
    blocking, blockedby, precedes, follows, copiedfrom, copiedto.
    """
    payload = {
        "other_task_id": other_task_id,
        "relation_kind": relation_kind,
    }
    return await _request("PUT", f"/tasks/{task_id}/relations", json=payload)


@mcp.tool()
async def remove_task_relation(task_id: int, other_task_id: int, relation_kind: RelationKind) -> dict:
    """Remove an existing relation between tasks."""
    return await _request("DELETE", f"/tasks/{task_id}/relations/{relation_kind}/{other_task_id}")


# --- users / assignees ------------------------------------------------------
##
@mcp.tool()
async def search_users(query: str) -> list[dict]:
    """Search users by name or username. Use this to find a user_id for assignees."""
    data = await _request("GET", "/users", params={"s": query})
    return [{"id": u.get("id"), "username": u.get("username"), "name": u.get("name")} for u in (data or [])]


@mcp.tool()
async def list_assignees(task_id: int) -> list[dict]:
    """List the users assigned to a task."""
    data = await _request("GET", f"/tasks/{task_id}/assignees")
    return [{"id": u.get("id"), "username": u.get("username")} for u in (data or [])]


@mcp.tool()
async def add_assignee(task_id: int, user_id: int) -> dict:
    """Assign a user to a task."""
    return await _request("PUT", f"/tasks/{task_id}/assignees", json={"user_id": user_id})


@mcp.tool()
async def remove_assignee(task_id: int, user_id: int) -> dict:
    """Unassign a user from a task."""
    return await _request("DELETE", f"/tasks/{task_id}/assignees/{user_id}")


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport in ("sse", "streamable-http"):
        host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
        port_str = os.environ.get("FASTMCP_PORT")
        if port_str:
            try:
                mcp.settings.port = int(port_str)
            except ValueError:
                pass
        mcp.settings.host = host

        allowed_hosts_env = os.environ.get("FASTMCP_ALLOWED_HOSTS")
        if allowed_hosts_env:
            hosts = [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]
            mcp.settings.transport_security.allowed_hosts = hosts

        disable_dns = os.environ.get("FASTMCP_DISABLE_DNS_REBINDING", "false").lower() in ("true", "1", "yes")
        if disable_dns:
            mcp.settings.transport_security.enable_dns_rebinding_protection = False

        mcp.run(transport=transport)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

