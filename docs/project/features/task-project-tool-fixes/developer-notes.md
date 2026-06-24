# Developer Notes: Task- & Projekt-Tool-Fixes

## Überblick

Dieses Feature behebt zwei Klassen von Lücken im MCP-Server:

1. **Task-Update-Payload-Lücke:** Task-Update-Tools (`update_task`, `set_reminders`, `complete_task`, `move_task_to_project`) sendeten nicht das Vikunja-Pflichtfeld `title` im Payload. Bei reinen Teil-Updates (z.B. nur `priority` ändern) würde Vikunja mit `2002 title: non zero value required` ablehnen. Die Lösung nutzt das bewährte GET-Overlay-Pattern von `update_project`, um einen vollständigen Basis-Payload zu bauen.

2. **Projekt-Tool-Feld-Lücke:** `list_projects` gab `description` und `identifier` nicht zurück, und `create_project` bot keinen Parameter für `hex_color`. Dies wurde ergänzt.

Die Änderungen sind nicht-brechend und vollständig mit bestehenden Tests validiert.

## Referenzen

- **Plan:** `docs/project/features/task-project-tool-fixes/plan-v001.md`
- **PRD:** `docs/project/prds/vikunja-mcp-server-v006.md` (Abschnitte 6, 8, 14)
- **Vorgänger-Feature:** `docs/project/features/optimistic-locking/plan-v001.md` (führte GET-vor-POST-Pattern für `updated` ein)

## Betroffene Dateien

| Datei | Änderung |
|---|---|
| `src/altiplano/server.py` | `update_task`: vollständiges GET-Overlay-Pattern (wie `update_project`). `set_reminders`, `complete_task`, `move_task_to_project`: Ergänzung um `title` im Payload. `list_projects`: Ergänzung um `identifier` und `description`. `create_project`: neuer optionaler Parameter `hex_color`. |
| `tests/test_server.py` | `test_tool_update_task`: erweitert mit vollständigem Basis-Payload-Check. `test_tool_update_task_partial` (neu): verifiziert `title` bei Teil-Update. `test_tool_set_reminders`, `test_tool_complete_task`, `test_tool_move_task_to_project`: POST-Assertions mit `title`. `test_tool_list_projects`: erweitert um `identifier`/`description`. `test_tool_create_project` (neu): validiert `hex_color` Parameter. |

## Architektur und Datenfluss

### Allgemein (wie bisher)

1. **FastMCP-Tool-Registrierung:** Jedes Tool ist mit `@mcp.tool()` dekoriert und wird beim Server-Start registriert.
2. **Async-Requests:** Alle Vikunja-API-Aufrufe laufen über die Hilfsfunktion `_request(method, path, **kwargs)`, die `httpx.AsyncClient` nutzt.
3. **Error Handling:** `httpx.HTTPStatusError` wird in `RuntimeError` mit strukturierter Fehlermeldung konvertiert.

### Task-Update-Pattern (neu)

`update_task`, `set_reminders`, `complete_task` und `move_task_to_project` folgen jetzt diesem Ablauf:

1. **GET aktuellen Task:** `task = await _request("GET", f"/tasks/{task_id}")`
2. **Basis-Payload bauen (unterschiedlich nach Tool):**
   - **`update_task`:** Vollständiger Payload mit allen Feldern (`title`, `description`, `done`, `priority`, `due_date`, `start_date`, `end_date`)
   - **Andere Tools:** Minimal nur `title: task["title"]` + ihre spezifischen Felder
3. **`updated` ergänzen (falls vorhanden):** Für Optimistic Locking
4. **POST mit vollständigem Payload:** `await _request("POST", f"/tasks/{task_id}", json=payload)`

### Projekt-Tool-Änderungen (minimal)

- **`list_projects`:** Rückgabe-Dict um `"identifier": p.get("identifier", "")` und `"description": p.get("description", "")` erweitert.
- **`create_project`:** Neuer optionaler Parameter `hex_color: str | None = None` mit Payload-Ergänzung `if hex_color is not None: payload["hex_color"] = hex_color`.

## Datenmodell und API-Mapping

### Vikunja-API Shapes (POST /tasks/{id})

```python
# Minimal (war vorher nur so):
{ "done": true, "updated": "2023-..." }

# Neu (Task-Updates müssen immer alle Felder enthalten):
{
  "title": "Task Title",                    # Pflichtfeld
  "description": "...",                     # optional
  "done": false,                            # required für POST
  "priority": 0,                            # optional
  "due_date": "2023-...",                   # optional
  "start_date": "2023-...",                 # optional
  "end_date": "2023-...",                   # optional
  "updated": "2023-..."                     # für Optimistic Locking
}
```

### GET /tasks/{id} → MCP-Rückgabe

Basis-Payload wird aus GET-Response aufgebaut:

```python
payload: dict[str, Any] = {
    "title": task["title"],
    "description": task.get("description", ""),
    "done": task.get("done", False),
    "priority": task.get("priority", 0),
    "due_date": task.get("due_date"),
    "start_date": task.get("start_date"),
    "end_date": task.get("end_date"),
}
```

Falls `updated` im GET-Response: `if "updated" in task: payload["updated"] = task["updated"]`

### GET /projects → MCP-Rückgabe

```python
{
    "id": p["id"],
    "title": p["title"],
    "parent_project_id": p.get("parent_project_id", 0),
    "is_archived": p.get("is_archived", False),
    "hex_color": p.get("hex_color", ""),
    "identifier": p.get("identifier", ""),       # neu
    "description": p.get("description", ""),     # neu
}
```

## Validierung und Tests

| Prüfung | Ergebnis |
|---|---|
| **pytest** | `uv run pytest` → 12/12 Tests grün (0.37s) |
| **Neue Tests** | `test_tool_update_task_partial`, `test_tool_create_project` |
| **Angepasste Tests** | `test_tool_update_task`, `test_tool_set_reminders`, `test_tool_complete_task`, `test_tool_complete_task_with_comment`, `test_tool_move_task_to_project`, `test_tool_list_projects` |
| **Mock-Pattern** | Bestehende Mocks mit `@patch("altiplano.server._request", new_callable=AsyncMock)` + `side_effect`-Funktionen für GET/POST-Unterscheidung |
| **Manuelle Validierung (MCP Inspector)** | Nicht durchgeführt. Zentrale Annahme (`title` als Pflichtfeld) ist durch `update_project` Analogie gut begründet und durch Tests validiert. Eine echte Vikunja-Instanz könnte über `npx @modelcontextprotocol/inspector uv run altiplano` geprüft werden. |

## Betriebs- und Setup-Hinweise

Keine neuen Umgebungsvariablen oder Konfigurationsdateien erforderlich. Alle Änderungen sind bestehenden Strukturen kompatibel.

## Wartungshinweise

### GET-Overlay-Pattern Konsistenz

Das Pattern aus `update_project` wurde 1:1 auf `update_task` übertragen. Falls künftig weitere Update-Tools das gleiche Pattern brauchen:

1. Erst `changes`-Dict aus Parametern sammeln.
2. Dann `if not changes: raise ValueError("No fields to update")`.
3. Task/Project per GET laden.
4. Basis-Payload mit allen erforderlichen Feldern bauen.
5. `updated` bedingt ergänzen.
6. `payload.update(changes)` überlagern.

### Minimal-invasive Ergänzung bei Spezial-Tools

`set_reminders`, `complete_task` und `move_task_to_project` brauchen **nicht** den vollen Basis-Payload, sondern nur `title` ergänzt. Diese Separation ist bewusst:

- **Security:** Diese Tools ändern nur fixe, eng begrenzte Felder (Erinnerungen, done-Status, project_id). Das Prinzip "nur explizit gewünschte Felder ändern" bleibt erhalten.
- **Maintenance:** Kein zusätzlicher API-Call, da alle Tools bereits ein GET für `updated` durchführen.

Falls Sie künftig einen dieser Tools erweitern (z.B. `move_task_to_project` auch `priority` ändern lassen), erwägen Sie, das Tool auf das volle GET-Overlay-Pattern wie `update_task` zu upgradieren.

### `identifier`-Feld ist read-only

Vikunja vergibt `identifier` automatisch (z.B. `#1`, `#2` pro Projekt). Kein Parameter bei `create_project` oder `update_project`.

## Bekannte Einschränkungen

- Zentrale Annahme ("Vikunja verlangt `title` bei Task-Updates") wurde nicht gegen eine echte Instanz validiert, nur durch Tests und Analogie zu `update_project`. Falls Ihre Instanz anders konfiguriert ist, sind die zusätzlichen `title`-Felder harmlos.
- `hex_color` ist optional und wird nicht validiert (z.B. auf Format). Vikunja akzeptiert beliebige Strings als `hex_color`.
