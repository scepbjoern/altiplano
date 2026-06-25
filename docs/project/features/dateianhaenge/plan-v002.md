# Plan: Dateianhänge

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v002
**Quelle:** User Request  
**Confidence Score:** 9/10 - Die Anbindung ist konzeptionell klar. Der Fokus auf Base64 und URLs passt perfekt zum Remote-Homelab-Szenario. Das Content-Type-Gotcha für Multipart-Uploads ist gelöst.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v002 |
| Komplexität | Medium |
| Primär betroffene Systeme | fastmcp, httpx, server.py, tests |
| Abhängigkeiten | Vikunja API (Multipart-Form-Uploads) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v002 | 2026-06-25 | Review / User Feedback | Lokale Dateipfade verworfen, da der Server remote auf dem Homelab laufen wird. Stattdessen: Base64-Upload (Limit 2MB), URL-Upload und direkte Task-Links für manuelle Uploads grosser Dateien. Delete-Tool ergänzt. |
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt (mit lokalem Dateipfad). |

## Feature Description

Dieses Feature ermöglicht es LLM-Clients (z.B. ChatGPT Web, Claude Web), Dateien als Anhänge an Vikunja-Tasks anzufügen, ohne dass sich der MCP-Server und der LLM-Client ein lokales Dateisystem teilen müssen.
Kleine Dateien (<= 2MB) können direkt via Base64-Codierung angehängt werden. Dateien aus dem Web können via direkter Download-URL übergeben werden (der MCP-Server lädt sie herunter und pusht sie zu Vikunja). Für zu grosse Dateien liefert der Server dem LLM einen anklickbaren Web-Link zum Task, sodass der Nutzer die Datei manuell über sein Smartphone oder den Browser hochladen kann.
Bestehende Anhänge können zudem aufgelistet und gelöscht werden.

## User Story

```text
Als KI-Client (im Auftrag des Personal Users)
möchte ich kleine Dateien via Base64 oder URLs an einen Vikunja-Task anhängen, sowie Anhänge listen und löschen können,
damit Remote-Homelab-Setups ohne gemeinsames Dateisystem funktionieren.
Bei zu grossen lokalen Dateien möchte ich dem Nutzer einen direkten Link zum Task geben,
damit er diese manuell hochladen kann.
```

## Problem Statement

Beim Remote-Hosting des MCP-Servers (Homelab) haben LLM-Clients keinen Zugriff auf das Dateisystem des Servers. Die Übergabe von lokalen Dateipfaden (z.B. `C:\Users\...`) funktioniert nicht. Grosse Dateien via Base64 zu übertragen, sprengt Token-Limits.

## Solution Statement

1. **`upload_task_attachment_base64`**: Erlaubt Uploads bis 2 MB, indem das LLM den Inhalt als Base64 übergibt.
2. **`upload_task_attachment_from_url`**: Der MCP-Server lädt eine Datei von einer URL in den Speicher und leitet sie als Multipart-Upload an Vikunja weiter.
3. **`get_task_frontend_url`**: Generiert den direkten Web-Link zu einem Task, den das LLM dem Nutzer anbietet, wenn die Datei lokal liegt und > 2 MB ist.
4. **`list_task_attachments` & `delete_task_attachment`**: Grundlegendes Management.

## Scope

### Im Scope

- Auflisten von Anhängen (`list_task_attachments`).
- Löschen von Dateianhängen (`delete_task_attachment`).
- Base64-Upload-Tool bis 2MB (`upload_task_attachment_base64`).
- URL-Download-Tool (`upload_task_attachment_from_url`).
- Generierung von Task-Frontend-Links (`get_task_frontend_url`).
- Anpassung des HTTP-Clients (`_request`), um Multipart-Uploads zu erlauben (Verwerfen des hardcodierten `application/json` Headers bei Multipart).

### Nicht im Scope

- Herunterladen von Anhängen via MCP an den LLM-Client (derzeit kein sinnvolles LLM-Szenario).
- Übergabe von absoluten lokalen Dateipfaden (`file_path`).

## Rollen und Berechtigungen

Personal User. Der MCP-Server benötigt HTTP-Ausgangsrechte (für den URL-Download-Fallback).

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Erweiterung von `_request` und Tool-Registrierung.
- `tests/test_server.py` - Warum: Mocking von `_request` und `httpx.AsyncClient` für Downloads.

## Codebase Intelligence

### Patterns to Follow

- **Naming:** `upload_task_attachment_base64`, `upload_task_attachment_from_url`.
- **FastMCP Docstrings:** Dem LLM explizit erklären, wann welches Tool zu nutzen ist und ab wann der manuelle Link (`get_task_frontend_url`) erzeugt werden soll.
- **API-Anbindung:** Wir nutzen weiterhin `_request(method, path, **kwargs)`.

### Anti-Patterns to Avoid

- **Gotcha:** `_headers()` setzt hardcodiert `Content-Type: application/json`. Wenn wir `httpx` anweisen, einen Multipart-Upload via `files=...` durchzuführen, setzt `httpx` automatisch den korrekten `Content-Type` inklusive `boundary`. Der hardcodierte Header überschreibt dies, was bei Vikunja zu Fehlern führt.

### Dependency Analysis

- `httpx` für das Herunterladen von Dateien von externen URLs im URL-Tool.
- `base64` Standardbibliothek.

## Datenmodell und API-Mapping

- `PUT /tasks/{task_id}/attachments` (Multipart `files`).
- `DELETE /tasks/{task_id}/attachments/{attachment_id}`.
- `GET /tasks/{task_id}/attachments` liefert Metadaten der Anhänge.
- Frontend URL Berechnung: `VIKUNJA_URL` (z.B. `https://tasks.melbjo.win/api/v1`) -> `https://tasks.melbjo.win/tasks/{task_id}`.

## Implementation Plan

### Phase 1: Foundation
Anpassen von `_request` in `server.py`, um Multipart-Uploads zu unterstützen.

### Phase 2: Core Tools
Implementierung von `list_task_attachments`, `delete_task_attachment` und `get_task_frontend_url`.

### Phase 3: Upload Tools
Implementierung von `upload_task_attachment_base64` (mit Grössenlimit) und `upload_task_attachment_from_url`.

### Phase 4: Testing
Hinzufügen von pytest Unit-Tests mit Mocks für Base64 und `httpx`-Downloads.

## Step-by-Step Tasks

### Task 1: UPDATE `_request` in `src/altiplano/server.py`

**Status:** done  
**Ziel:** `_request` soll `Content-Type` verwerfen, wenn `files` vorhanden ist.  
**Validation:** `uv run pytest` ausgeführt. Alle 18 Tests bestanden ohne Regressionen.
**IMPLEMENT:** 
In `_request`:
```python
    headers = _headers()
    if "files" in kwargs:
        headers.pop("Content-Type", None)
    async with httpx.AsyncClient(base_url=_base(), headers=headers, timeout=30) as client:
```

### Task 2: ADD `list` and `delete` attachment tools

**Status:** done  
**Ziel:** Tools zum Listen und Löschen.  
**Validation:** `uv run pytest` ausgeführt. Alle 18 Tests bestanden ohne Regressionen.
**IMPLEMENT:**  
```python
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
```

### Task 3: ADD `get_task_frontend_url`

**Status:** done  
**Ziel:** Helfer-Tool, das einen direkten Task-Link liefert.  
**Validation:** `uv run pytest` ausgeführt. Alle 18 Tests bestanden ohne Regressionen.
**IMPLEMENT:** 
```python
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
```

### Task 4: ADD `upload_task_attachment_base64`

**Status:** done  
**Ziel:** Base64-Upload mit 2MB-Limit.  
**Validation:** `uv run pytest` ausgeführt. Alle 18 Tests bestanden ohne Regressionen.
**IMPLEMENT:**  
```python
import base64

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
```

### Task 5: ADD `upload_task_attachment_from_url`

**Status:** done  
**Ziel:** Download einer externen URL und Upload an Vikunja.  
**Validation:** `uv run pytest` ausgeführt. Alle 18 Tests bestanden ohne Regressionen.
**IMPLEMENT:** 
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
```

### Task 6: UPDATE `tests/test_server.py`

**Status:** done  
**Ziel:** Unit-Tests für alle 5 neuen Tools.  
**Validation:** `uv run pytest` ausgeführt. 23/23 Tests bestanden (5 neue Tests für alle Anhangs-Tools erfolgreich hinzugefügt).
**IMPLEMENT:** 
- Mock `_request` für `list`, `delete`, `upload_base64` und `upload_from_url`.
- Test für Grössenlimit-Exception in `upload_base64`.
- Mock `httpx.AsyncClient.get` für `upload_from_url`.

**VALIDATE:**
- `uv run pytest`

## Acceptance Criteria

- [x] `list_task_attachments` & `delete_task_attachment` existieren.
- [x] `upload_task_attachment_base64` lehnt Strings > ~2.66 MB (entspricht 2MB binär) ab.
- [x] `upload_task_attachment_from_url` lädt die Datei korrekt über HTTP herunter.
- [x] `get_task_frontend_url` berechnet den Link korrekt aus `VIKUNJA_URL`.
- [x] Content-Type Header Workaround im `_request` funktioniert.
- [x] Tests sind grün.

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Bereit für `/document` und `/commit`

## Documentation Results

Folgende Dokumentationsdateien wurden generiert:
- [User Guide](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/dateianhaenge/user-guide.md)
- [Developer Notes](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/dateianhaenge/developer-notes.md)
