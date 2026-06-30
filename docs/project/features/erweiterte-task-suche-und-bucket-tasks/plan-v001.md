# Feature Plan: Erweiterte Task-Suche und Bucket-Tasks

**Plan-Version:** v001
**PRD-Referenz:** `docs/project/prds/vikunja-mcp-server-v012.md`

## Plan-Änderungshistorie
| Version | Datum | Beschreibung |
|---|---|---|
| v001 | 2026-06-30 | Initialer Entwurf nach PRD v012. |

## 1. Feature-Zusammenfassung
Ersatz des bisherigen projektbezogenen `list_tasks`-Tools durch eine leistungsstarke, projektübergreifende `search_tasks`-Suche über den globalen `/api/v1/tasks`-Endpunkt. Ergänzung eines `get_bucket_tasks`-Tools, um Tasks spezifischer Kanban-Buckets korrekt und in der richtigen Reihenfolge abzurufen.

**User Story:**
- Als Nutzer möchte ich Tasks gefiltert und projektübergreifend suchen sowie Tasks eines bestimmten Buckets (Kanban-Spalte) abrufen.

**Feature-Typ:** New Capability / Enhancement / Refactor
**Komplexität:** Medium
**Primär betroffene Systeme:** `server.py`, `tests/test_server.py`

## 2. Architektur & Design-Entscheidungen

### `search_tasks`
- **Endpunkt:** `GET /api/v1/tasks`
- **Filter-Logik:** Konstruktion eines rohen Vikunja-Filterstrings durch Kombination von Komfortparametern mit `&&`. Wenn `text` allein verwendet wird, wird `s` gesendet. Werden strukturierte Filter mit `text` kombiniert, wird `text` in `title ~ '...' || description ~ '...'` übersetzt.
- **Offene Fragen & Annahmen:**
  - Semantik für Arrays (`label_ids`, `assignee_ids`): Wir verwenden standardmäßig `in` (any match: `labels in 1,2`).
  - Datumsvergleiche: Wir verwenden strikt `<` für `_before` und `>` für `_after`.
  - Paginierung: Wir geben `per_page` an Vikunja weiter (default 50).
  - Vikunja unterstützt `title ~ '...'`. Falls dies beim Testen fehlschlägt, passen wir den Plan an.

### `get_bucket_tasks`
- **Logik:**
  1. Kanban-View auflösen (falls `view_id` nicht übergeben).
  2. Tasks für diese View via Vikunja API abrufen (z.B. `GET /projects/{project_id}/views/{view_id}`).
  3. Den Bucket mit `bucket_id` in der Struktur suchen und die dort enthaltenen Tasks extrahieren.
  4. Die Tasks in der vorgegebenen Bucket-Reihenfolge zurückgeben.

### Entfernung `list_tasks`
- Das Tool `list_tasks` wird komplett gelöscht.
- Die Tests für `list_tasks` (sofern vorhanden) werden gelöscht.

## 3. Tasks

### TASK 1: Implementierung `search_tasks` in `server.py`
- **STATUS:** done
- **IMPLEMENT:**
  - Entferne `list_tasks`.
  - Füge `@mcp.tool()` `search_tasks` mit den im PRD beschriebenen Argumenten hinzu.
  - Implementiere die Filterstring-Konstruktion.
  - Sende GET-Request an `/api/v1/tasks`.
- **VALIDATE:**
  - **Automatisiert:** `test_tool_search_tasks_isolated_text`, `test_tool_search_tasks_combined` und `test_tool_search_tasks_sorting_validation` in `test_server.py` erfolgreich ausgeführt.

### TASK 2: Implementierung `get_bucket_tasks` in `server.py`
- **STATUS:** done
- **IMPLEMENT:**
  - Füge `@mcp.tool()` `get_bucket_tasks` hinzu.
  - Löse `view_id` auf, wenn fehlend.
  - Rufe Views/Tasks ab und filtere nach `bucket_id`.
- **VALIDATE:**
  - **Automatisiert:** `test_tool_get_bucket_tasks` in `test_server.py` erfolgreich ausgeführt.

### TASK 3: API-Mocks und Tests in `test_server.py` anpassen
- **STATUS:** done
- **IMPLEMENT:**
  - Entferne etwaige Erwähnungen von `list_tasks` aus `test_server.py` (z.B. in `test_mcp_initialization`).
  - Füge API-Mock-Tests für `search_tasks` hinzu, um die korrekte Bildung des `filter`-Strings zu überprüfen.
  - Füge API-Mock-Tests für `get_bucket_tasks` hinzu.
- **VALIDATE:**
  - **Automatisiert:** `uv run pytest` wurde erfolgreich ausgeführt (45 tests passed).

## 4. Plan Quality Score
**Score: 9/10**
- Der Plan ist umsetzbar, berücksichtigt die API-Logik und die bestehende Architektur. Die offenen Fragen aus dem PRD wurden mit pragmatischen Annahmen beantwortet (z.B. `<` für Datumsvergleiche, `in` für Arrays), die während der Implementierung leicht anpassbar sind.

## 5. Documentation Results
Folgende Dokumente wurden im Zuge dieses Features erstellt:
- [user-guide.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/erweiterte-task-suche-und-bucket-tasks/user-guide.md): Anleitung für Endanwender zur Verwendung von `search_tasks` und `get_bucket_tasks`.
- [developer-notes.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/erweiterte-task-suche-und-bucket-tasks/developer-notes.md): Technische Notizen zur API-Struktur und zum Testaufbau.
