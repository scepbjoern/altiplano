# Plan: Task Security Tools

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001  
**Quelle:** User Request, `docs/project/prds/vikunja-mcp-server-v004.md`  
**Confidence Score:** 10/10 (Beide Tools sind simple, sichere Convenience-Wrapper, die den API-Anforderungen entsprechen).

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability / Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py, Tests |
| Abhängigkeiten | Vikunja API (POST `/tasks/{task_id}`) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Initiale kombinierte Planung für complete_task und move_task_to_project |

## Feature Description

Zwei dedizierte Sicherheits-Tools (`complete_task` und `move_task_to_project`) werden als sichere Convenience-Wrapper hinzugefügt. Sie ermöglichen KI-Agenten, gezielte, sichere Aktionen (Erledigen einer Aufgabe bzw. Verschieben in ein anderes Projekt) auszuführen, ohne das mächtige und parameterreiche `update_task` Tool nutzen zu müssen. Dies minimiert das Risiko unbeabsichtigter Datenänderungen durch Halluzinationen.

## User Story

```text
Als KI-Client (Technischer Konsument)
möchte ich die dedizierten Tools `complete_task` und `move_task_to_project` nutzen,
damit ich Aufgaben sicher als erledigt markieren oder in andere Projekte verschieben kann, ohne Gefahr zu laufen, andere Task-Attribute unbeabsichtlich zu überschreiben.
```

## Problem Statement

Das `update_task` Tool ist sehr flexibel und mächtig, birgt jedoch Risiken: Falls ein LLM beim Ändern des Status oder des Zielprojekts andere Parameter mitsendet oder halluziniert, können sensible Aufgabendaten überschrieben werden. Dedizierte, fokussierte Wrapper-Tools verhindern dieses Risiko.

## Solution Statement

Wir implementieren zwei neue Tools in `server.py`:
1. `complete_task(task_id: int, comment: str | None = None)` - Setzt den Status einer Aufgabe via `POST /tasks/{task_id}` fix auf `{"done": True}` und fügt optional einen Kommentar hinzu.
2. `move_task_to_project(task_id: int, project_id: int)` - Verschiebt eine Aufgabe via `POST /tasks/{task_id}` durch Fixieren des Zielprojekts `{"project_id": project_id}`.

## Scope

### Im Scope

- Neues MCP-Tool `complete_task` mit optionalem Kommentar.
- Neues MCP-Tool `move_task_to_project`.
- Testabdeckung in `test_server.py`.

### Nicht im Scope

- Destruktive Aktionen (z.B. Löschen von Aufgaben).

## Rollen und Berechtigungen

Keine Änderungen. Der API-Token benötigt Schreibzugriff auf Aufgaben und Kommentare in Vikunja.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Enthält das bestehende `update_task` Tool.
- `tests/test_server.py` - Warum: Test-Pattern für neue Tools.

## Codebase Intelligence

### Projektstruktur und Architektur

Bestehende Struktur mit `server.py` als FastMCP Endpoint und `test_server.py` für API-Mocks.

### Patterns to Follow

- Naming: `complete_task`, `move_task_to_project`
- FastMCP: `@mcp.tool()` Decorator mit eindeutigem, englischem Docstring.
- API-Anbindung: Verwendung von `await _request("POST", f"/tasks/{task_id}", json=...)`.

### Anti-Patterns to Avoid

- Keine Implementierung komplexer Logik; die Tools sind reine Wrapper.

## Architekturentscheidungen

### Gewählter Ansatz

Zwei neue FastMCP-Tools, die denselben Vikunja-API-Endpoint wie `update_task` nutzen, aber die Payload auf die jeweiligen Felder fixieren.

### Security, Performance, Maintainability

- Security: Erhöhte Ausführungssicherheit für LLMs, da keine versehentlichen Parameter überschrieben werden können.
- Performance: Direkte API-Calls, gleiche Performance wie `update_task`.
- Maintainability: Einfach testbar und verständlich.

## Datenmodell und API-Mapping

- `complete_task`: POST Request auf `/tasks/{task_id}` mit JSON `{"done": True}`. Wenn `comment` angegeben ist, folgt ein PUT Request auf `/tasks/{task_id}/comments` mit `{"comment": comment}`.
- `move_task_to_project`: POST Request auf `/tasks/{task_id}` mit JSON `{"project_id": project_id}`.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Hinzufügen der Tools.
- `tests/test_server.py` - Hinzufügen der Tests und Aktualisierung der Tool-Liste.

## Implementation Plan

### Phase 1: Core Implementation

Hinzufügen von `complete_task` und `move_task_to_project` in `server.py`.

### Phase 2: Testing and Validation

Hinzufügen der Tests in `tests/test_server.py`.

## Step-by-Step Tasks

### Task 1: CREATE complete_task and move_task_to_project tools in server.py

**Status:** done  
**Ziel:** Neue Tools `complete_task` und `move_task_to_project` erstellen.  
**IMPLEMENT:**
```python
@mcp.tool()
async def complete_task(task_id: int, comment: str | None = None) -> dict:
    """Mark a task as done. This is a safe convenience wrapper for update_task.
    
    If a `comment` is provided, it is added to the task comments.
    """
    res = await _request("POST", f"/tasks/{task_id}", json={"done": True})
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
    return await _request("POST", f"/tasks/{task_id}", json={"project_id": project_id, "done": is_done})
```
**PATTERN:** `update_task` und `add_comment` als Vorbild für die API-Aufrufe.  
**IMPORTS:** Keine neuen.  
**GOTCHA:** Tools müssen mit `@mcp.tool()` registriert sein.  
**ACCEPTANCE CRITERIA:**
- [x] Beide Tools sind in `server.py` definiert.

**VALIDATE:**
- `uv run pytest`

### Task 2: UPDATE tests/test_server.py

**Status:** done  
**Ziel:** Die neuen Tools in die Tests aufnehmen.  
**IMPLEMENT:**
1. In `test_mcp_initialization` die Tools `"complete_task"` und `"move_task_to_project"` zur Liste `expected_tools` hinzufügen.
2. Drei neue Tests erstellen: `test_tool_complete_task`, `test_tool_complete_task_with_comment` und `test_tool_move_task_to_project`.  
**PATTERN:** `test_tool_update_project` und Mocking mit `AsyncMock`.  
**IMPORTS:** Keine neuen.  
**GOTCHA:** `complete_task` mit Kommentar ruft `_request` zweimal auf (POST, dann PUT).  
**ACCEPTANCE CRITERIA:**
- [x] `test_mcp_initialization` prüft das Vorhandensein beider Tools.
- [x] Alle neuen Tests laufen erfolgreich durch.

**VALIDATE:**
- `uv run pytest`

## Testing Strategy

### Unit / Integration Tests

Spezifische Tests für die Validierung der API-Aufrufe.

### Regression Tests

`test_mcp_initialization` stellt sicher, dass die Tools ordnungsgemäß im MCP-Server registriert sind.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. `uv run altiplano` starten.
2. Im MCP Inspector die Tools testen und prüfen, ob die entsprechenden API-Calls abgesetzt werden.

## Acceptance Criteria

- [x] Feature implementiert alle Scope-Anforderungen
- [x] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [x] Relevante pytest-Tests sind ergänzt und grün
- [x] Relevante manuelle Flows sind validiert
- [x] Keine bekannten Regressionen in bestehenden Kernworkflows
- [x] Dokumentationsbedarf ist notiert

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Alle relevanten Tests laufen erfolgreich oder Ausnahmen sind begründet
- [x] Manuelle Prüfung (MCP Inspector / Claude Desktop) ist dokumentiert
- [x] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt
- [x] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Beide Tools sollen in den User Guide und die Developer Notes aufgenommen werden.

### Documentation Results

Folgende Dokumente wurden erstellt:
- [user-guide.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/task-security-tools/user-guide.md)
- [developer-notes.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/task-security-tools/developer-notes.md)

## Notes and Trade-offs

Die Tools überlappen funktional mit `update_task`, bieten aber wichtige LLM-Sicherheitsschranken.

## Offene Fragen

Keine offenen Fragen (Zusammenlegung und Scope wurden vom Nutzer geklärt).

## Plan Review Notes

(Wird später durch den Review ergänzt.)
