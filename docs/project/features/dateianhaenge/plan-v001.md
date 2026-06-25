# Plan: Dateianhänge

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001
**Quelle:** User Request (`/plan-feature Dateianhänge`) & PRD v006  
**Confidence Score:** 9/10 - Die Anbindung ist simpel, jedoch muss auf die `Content-Type` Behandlung im `_request` Helfer geachtet werden, da httpx Multipart-Uploads übernimmt, aber von einem fixen JSON-Header gestört wird.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Low-Medium |
| Primär betroffene Systeme | fastmcp, httpx, server.py, tests |
| Abhängigkeiten | Vikunja API (Multipart-Form-Uploads), lokales Dateisystem |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Das Feature "Dateianhänge" ermöglicht es dem LLM-Client, lokale Dateien über den MCP-Server als Anhänge zu Vikunja-Tasks hochzuladen und bestehende Anhänge eines Tasks aufzulisten. Da der Server im MVP lokal via `stdio` betrieben wird, kann der LLM-Client absolute Dateipfade übergeben, die der Server dann einliest und per `multipart/form-data` an die Vikunja-API überträgt.

## User Story

```text
Als KI-Client (im Auftrag des Personal Users)
möchte ich lokale Dateien an einen Vikunja-Task anhängen und bestehende Anhänge listen können,
damit ich Dokumente, Bilder oder Logs nahtlos mit Tasks verknüpfen kann.
```

## Problem Statement

Derzeit können keine Dateien an Tasks angehängt werden, obwohl die Vikunja-API dies unterstützt. Die Einschränkung limitiert Workflows, bei denen Fehlerprotokolle, Mockups oder relevante Dokumente mit einem Task assoziiert werden sollen.

## Solution Statement

Wir fügen zwei neue MCP-Tools hinzu: `list_task_attachments` und `upload_task_attachment`. 
Für `upload_task_attachment` wird ein lokaler absoluter Dateipfad akzeptiert, die Datei asynchron oder im Kontextmanager gelesen und via `httpx` als Multipart-Form-Upload (`files={"files": (filename, f)}`) an den Endpunkt `PUT /tasks/{task_id}/attachments` gesendet.

## Scope

### Im Scope

- Auflisten von Anhängen an einem Task (`list_task_attachments`).
- Hochladen von Dateien als Anhang (`upload_task_attachment`).
- Löschen von Dateianhängen (`delete_task_attachment`).
- Anpassung des HTTP-Clients (`_request`), um Multipart-Uploads zu erlauben (Entfernen des hardcodierten `application/json` Headers, wenn `files` übergeben wird).

### Nicht im Scope

- Herunterladen von Anhängen via MCP (derzeit kein sinnvolles LLM-Szenario).
- Remote-Upload grosser Dateien via Base64 (unterliegt Token-Limits der LLMs).

## Rollen und Berechtigungen

Personal User. Zugriff auf das lokale Dateisystem ist erforderlich (wird durch das MCP-Protokoll impliziert, da der Server lokal läuft).

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Erweiterung von `_request` und Registrierung der neuen Tools.
- `tests/test_server.py` - Warum: Mocking von `_request` und Dateizugriff (`builtins.open` / `pathlib.Path.open`).

## Codebase Intelligence

### Projektstruktur und Architektur

Das Projekt nutzt `mcp.server.fastmcp.FastMCP`. Alle Tools rufen `_request()` auf.

### Patterns to Follow

- **Naming:** Tools heissen `<aktion>_<objekt>`, also `list_task_attachments` und `upload_task_attachment`.
- **FastMCP:** Klare, englische Docstrings für das LLM (z.B. "Upload a local file as an attachment to a task").
- **API-Anbindung:** Wir nutzen weiterhin `_request(method, path, **kwargs)`.

### Anti-Patterns to Avoid

- **Gotcha:** `_headers()` setzt hardcodiert `Content-Type: application/json`. Wenn wir `httpx` anweisen, einen Multipart-Upload via `files=...` durchzuführen, setzt `httpx` automatisch den korrekten `Content-Type` inklusive `boundary`. Der hardcodierte Header würde dies überschreiben und der API-Call bei Vikunja schlägt fehl!

### Dependency Analysis

Keine neuen Dependencies. `httpx` und `pathlib` genügen.

### Testing Patterns

- Wir verwenden `@patch("altiplano.server._request")` wie bisher.
- Für das Dateisystem mocken wir `Path.is_file` und `Path.open` via `unittest.mock.mock_open`.

## Architekturentscheidungen

### Gewählter Ansatz

Der `_request`-Helfer wird so angepasst, dass er den `Content-Type` Header aus den von `_headers()` zurückgegebenen Headern entfernt, falls `files` in den `kwargs` vorkommt. Das Upload-Tool liest die Datei lokal aus.

### Erwogene Alternativen

- Alternative: Eigene Request-Funktion `_request_multipart` für Uploads. 
  - Entscheidung: Dagegen. Es ist wartbarer, `kwargs` in `_request` zu prüfen (`if "files" in kwargs`), um Code-Duplizierung beim Exception-Handling zu vermeiden.

### Security, Performance, Maintainability

- Security: Das Tool validiert, dass der übergebene Dateipfad existiert und eine Datei ist (`Path.is_file()`).
- Maintainability: `httpx` übernimmt die Multipart-Logik vollständig.

## Datenmodell und API-Mapping

- `PUT /tasks/{task_id}/attachments` (Vikunja erwartet Feld `files`).
- `GET /tasks/{task_id}/attachments` gibt eine Liste von Attachment-Objekten zurück (wir extrahieren `id`, `name`, `size`, `created`).

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Anpassung `_request` und neue Tools.
- `tests/test_server.py` - Neue Tests.

## Implementation Plan

### Phase 1: Foundation
Anpassen von `_request` in `server.py`, um Multipart-Uploads zu unterstützen.

### Phase 2: Core Implementation
Implementierung von `list_task_attachments` und `upload_task_attachment`.

### Phase 3: Testing and Validation
Hinzufügen von pytest Unit-Tests und manuelle Validierung.

## Step-by-Step Tasks

### Task 1: UPDATE `_request` function in `src/altiplano/server.py`

**Status:** planned  
**Ziel:** `_request` soll `Content-Type` verwerfen, wenn `files` vorhanden ist, damit `httpx` den Multipart-Header generieren kann.  
**IMPLEMENT:** 
In `_request`:
```python
    headers = _headers()
    if "files" in kwargs:
        headers.pop("Content-Type", None)
    async with httpx.AsyncClient(base_url=_base(), headers=headers, timeout=30) as client:
```
**GOTCHA:** Wenn wir `headers=_headers()` im `AsyncClient` Constructor verwenden, dürfen wir `_headers()` nicht direkt als Argument übergeben, ohne es vorher zu manipulieren.

### Task 2: ADD `list_task_attachments` in `src/altiplano/server.py`

**Status:** planned  
**Ziel:** Tool zum Abrufen der Anhänge eines Tasks.  
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
```
*Anmerkung: Das genaue Response-Format von Vikunja für Attachments kann variieren (oft direkt als Objekt mit `id`, `name`, `size` oder verschachtelt unter `file`). Im Zweifel direkt `a.get("name")` usw. zurückgeben oder das vollständige Objekt, falls unbekannt.*

### Task 3: ADD `upload_task_attachment` in `src/altiplano/server.py`

**Status:** planned  
**Ziel:** Tool zum Hochladen von Dateien.  
**IMPLEMENT:** 
```python
@mcp.tool()
async def upload_task_attachment(task_id: int, file_path: str) -> dict:
    """Upload a local file as an attachment to a task. file_path must be an absolute path."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with path.open("rb") as f:
        files = {"files": (path.name, f)}
        return await _request("PUT", f"/tasks/{task_id}/attachments", files=files)
```
**IMPORTS:** `from pathlib import Path` (bereits in `server.py` vorhanden).

### Task 4: ADD `delete_task_attachment` in `src/altiplano/server.py`

**Status:** planned  
**Ziel:** Tool zum Löschen von Dateien.  
**IMPLEMENT:** 
```python
@mcp.tool()
async def delete_task_attachment(task_id: int, attachment_id: int) -> dict:
    """Delete an attachment from a task."""
    return await _request("DELETE", f"/tasks/{task_id}/attachments/{attachment_id}")
```

### Task 5: UPDATE `tests/test_server.py`

**Status:** planned  
**Ziel:** Unit-Tests für die beiden neuen Tools und die Anpassung von `_request`.  
**IMPLEMENT:** 
- Test für `list_task_attachments`.
- Test für `upload_task_attachment` mit `@patch("pathlib.Path.is_file", return_value=True)` und `@patch("builtins.open", new_callable=unittest.mock.mock_open, read_data=b"dummy")` (oder via `pathlib.Path.open`).

**VALIDATE:**
- `uv run pytest`

## Testing Strategy

### Unit / Integration Tests

Tests mocken `_request` für die Tool-Logik und verifizieren, dass `files` korrekt übergeben wird.

### Edge Cases

- Datei existiert nicht -> Führt zu `FileNotFoundError` (sauber gehandhabt und als String vom MCP-Protokoll an den LLM weitergeleitet).

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

- Start des Servers: `uv run altiplano` im Inspector.
- Upload ausführen mit existierender Dummy-Datei via `upload_task_attachment` und Task-ID.
- Überprüfen im Vikunja Web-UI, ob die Datei am Task hängt.

## Acceptance Criteria

- [ ] `list_task_attachments` existiert und liefert Listen.
- [ ] `upload_task_attachment` existiert und lädt via Multipart hoch.
- [ ] `Content-Type` Bug bei `_request` mit `files` wird umgangen.
- [ ] Tests sind vorhanden und grün (`uv run pytest`).

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] Manuelle Prüfung ist dokumentiert
- [ ] Bereit für `/document` und `/commit`

## Documentation Notes

Endanwender-Doku (`starter-kit-usage/`) soll darauf hinweisen, dass für Dateianhänge der absolute Pfad der Datei auf dem Gerät erforderlich ist, auf dem der MCP Server läuft.

## Notes and Trade-offs

Derzeit beschränkt auf ein File pro Tool-Aufruf, da LLMs meist iterativ arbeiten.
