# Developer Notes: Erweiterte Task-Suche und Bucket-Tasks

## Überblick

Dieses Feature erweitert die Aufgaben-Management-Schnittstelle des MCP-Servers um eine projektübergreifende Suchfunktion (`search_tasks`) sowie eine positionsbasierte Bucket-Abfrage (`get_bucket_tasks`). Die Implementierung nutzt den globalen `/tasks` und den view-spezifischen `/projects/{project_id}/views/{view_id}/tasks` API-Endpunkt von Vikunja.

## Referenzen

- Plan: [plan-v001.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/erweiterte-task-suche-und-bucket-tasks/plan-v001.md)
- PRD: [vikunja-mcp-server-v012.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/prds/vikunja-mcp-server-v012.md)

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| [server.py](file:///e:/bjoer/Documents/repos/altiplano/src/altiplano/server.py) | - `_task_summary` um `due_date` und `project_id` erweitert.<br>- `list_tasks` entfernt.<br>- `search_tasks` hinzugefügt (Kombination von Komfortparametern zu Vikunja-Filterausdruck).<br>- `get_bucket_tasks` hinzugefügt (positionsbasierte Aufgaben-Liste pro Bucket). |
| [test_server.py](file:///e:/bjoer/Documents/repos/altiplano/tests/test_server.py) | - MCP-Initialisierungstest aktualisiert (Austausch von `list_tasks` durch `search_tasks` und `get_bucket_tasks`).<br>- Testfälle für `search_tasks` und `get_bucket_tasks` inklusive aller Validierungen und Mocks hinzugefügt. |
| [TASKS.md](file:///e:/bjoer/Documents/repos/altiplano/TASKS.md) | - Feature als abgeschlossen (`done`) markiert und in den Index verschoben. |

## Architektur und Datenfluss

### 1. `search_tasks`
- **Endpunkt:** `GET /tasks`
- **Ablauf:** 
  1. Komfort-Filterparameter (z. B. `done`, `priority_min`, `label_ids`) werden in eine Liste von Filter-Klauseln überführt.
  2. Textsuche-Logik:
     - Wenn *nur* `text` übergeben wird (isoliert), wird der Vikunja-Query-Parameter `s` genutzt.
     - Wenn `text` *zusammen mit* Filtern übergeben wird, wird er in `(title ~ 'text' || description ~ 'text')` übersetzt und der Filterliste hinzugefügt.
  3. Die Filter-Klauseln werden mit ` && ` verbunden.
  4. Die Anfrage wird an die Vikunja-API gesendet. Die Rückgabe wird auf ein schlankeres Datenformat (`_task_summary`) gemappt.

### 2. `get_bucket_tasks`
- **Endpunkt:** `GET /projects/{project_id}/views/{view_id}/tasks`
- **Ablauf:**
  1. Wenn keine `view_id` übergeben wird, wird `_resolve_kanban_view_id` aufgerufen, um die Kanban-View-ID des Projekts zu ermitteln.
  2. Ein Request an den view-spezifischen Task-Endpunkt von Vikunja wird mit dem Filter `bucket_id = {bucket_id}` und den Sortierparametern `sort_by=position` und `order_by=asc` gesendet.
  3. Die Aufgaben werden in der positionsabhängigen Kanban-Reihenfolge zurückgegeben.

## Datenmodell und API-Mapping

Die von den neuen Tools zurückgegebenen Task-Objekte verwenden eine erweiterte Version von `_task_summary`:
```python
{
    "id": t.get("id"),
    "identifier": t.get("identifier"),
    "title": t.get("title"),
    "done": t.get("done"),
    "priority": t.get("priority"),
    "due_date": t.get("due_date"),
    "project_id": t.get("project_id"),
}
```

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `test_mcp_initialization` | Prüft die korrekte Registrierung von `search_tasks` und `get_bucket_tasks` auf dem Server. |
| `test_tool_search_tasks_isolated_text` | Prüft, ob bei alleiniger Verwendung von `text` der Parameter `s` gesendet wird. |
| `test_tool_search_tasks_combined` | Verifiziert die komplexe Kombination strukturierter Komfort-Parameter mit Textsuche zu einem Vikunja-Filterausdruck. |
| `test_tool_search_tasks_sorting_validation` | Testet die clientseitige Validierung von Sortier-Parametern (Längenübereinstimmung, erlaubte Richtungen). |
| `test_tool_get_bucket_tasks` | Validiert den gesamten Ablauf zur Ermittlung der Kanban-View-ID und dem anschließenden positionsbasierten Abrufen der Tasks. |

Alle Tests wurden erfolgreich ausgeführt:
```bash
uv run pytest
```

## Betriebs- und Setup-Hinweise

Keine neuen Umgebungsvariablen oder Setup-Schritte nötig. Das Feature nutzt die bestehende API-Konfiguration (`VIKUNJA_URL` und `VIKUNJA_API_TOKEN`).

## Wartungshinweise

- **Python-Versions-Gotcha:** Bei Datumsersetzungen und Text-Escaping im F-String wurde darauf geachtet, keine Backslashes (`\`) innerhalb der geschweiften Klammern `{}` zu verwenden, um die Kompatibilität mit Python < 3.12 (speziell Python 3.11) zu gewährleisten.
- **Escape-Logik:** Single-Quotes in Filtern wie `title_contains` und `text` werden über `.replace("'", "\\'")` escaped, um SQL/Filter-Syntax-Fehler in Vikunja zu vermeiden.
