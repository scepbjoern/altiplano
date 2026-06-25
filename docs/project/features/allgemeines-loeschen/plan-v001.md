# Plan: Allgemeines Löschen

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001
**Quelle:** PRD v006 (Kapitel 6, 7, 13, 15)  
**Confidence Score:** 9/10 - Klar umrissene Vikunja API-Endpunkte und einfaches Bestätigungs-Pattern.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Medium |
| Primär betroffene Systeme | fastmcp / server.py / Tests |
| Abhängigkeiten | Vikunja API `DELETE` Endpunkte für Tasks, Comments und Buckets |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Einführung von Tools für destruktive Delete-Operationen (Löschen) von Tasks, Kommentaren und Kanban-Buckets. Um unbeabsichtigten Datenverlust durch die KI zu verhindern, verlangen alle Lösch-Tools zwingend einen zweistufigen Bestätigungs-Prozess (`confirm=True`), welcher der KI explizit vorschreibt, zuerst die menschliche Erlaubnis einzuholen.

## User Story

```text
Als Nutzer
möchte ich veraltete Tasks, Kommentare und Kanban-Buckets komplett löschen können, aber mit einer Sicherheits-Bestätigung,
damit mein Vikunja aufgeräumt bleibt, ohne dass versehentlich Daten durch die KI vernichtet werden.
```

## Problem Statement

Der MCP Server bietet aktuell aus Sicherheitsgründen (Scope des MVP) keine Möglichkeit an, Ressourcen endgültig zu löschen. Für das langfristige Aufräumen von Projekten ist dieses Feature (Extended Scope) jedoch nötig, darf aber niemals ohne explizite Erlaubnis von der KI ausgeführt werden.

## Solution Statement

Implementierung von drei neuen Tools: `delete_task`, `delete_comment` und `delete_bucket`.
Alle drei Tools nehmen einen Parameter `confirm: bool = False` entgegen.
Wenn das Tool mit `confirm=False` aufgerufen wird, bricht es mit einem `ValueError` ab, dessen Meldung die KI unmissverständlich anweist, den User zu fragen. Erst nach dem "Ja" des Users darf die KI das Tool mit `confirm=True` aufrufen, woraufhin der tatsächliche HTTP `DELETE` Request abgesetzt wird.

## Scope

### Im Scope

- `delete_task(task_id: int, confirm: bool = False)`
- `delete_comment(task_id: int, comment_id: int, confirm: bool = False)`
- `delete_bucket(project_id: int, bucket_id: int, confirm: bool = False)`
- Zweistufiges Bestätigungs-Pattern.
- Testabdeckung via `pytest` und API-Mocks.

### Nicht im Scope

- Löschen von Projekten.
- Stilles / automatisiertes Löschen ohne User-Prompt.
- Papierkorb-Funktionalität (Vikunja löscht direkt).

## Rollen und Berechtigungen

- Personal User: Hat Vollzugriff. Die Löschung erfordert das Einverständnis.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Bestehende Struktur der Tools und Verwendung von `_request`.
- `tests/test_server.py` - Warum: Bestehende Mocking-Patterns für `DELETE` Requests (z.B. `test_tool_delete_task_attachment`).

## Codebase Intelligence

### Projektstruktur und Architektur

Das Projekt nutzt `mcp.server.fastmcp.FastMCP` und `httpx` in `src/altiplano/server.py`.

### Patterns to Follow

- **API-Anbindung:** Aufruf via `await _request("DELETE", f"/tasks/{task_id}")`.
- **Bestätigungs-Pattern:** 
  ```python
  if not confirm:
      raise ValueError("DANGER: This is a destructive operation. You MUST ask the human user for explicit confirmation before proceeding. If the user explicitly approves, call this tool again with confirm=true.")
  ```
- **Fehlerbehandlung:** Die generische Fehlerbehandlung via `_request` greift auch für `DELETE`.

### Anti-Patterns to Avoid

- Keine eigene Bestätigungs-Logik einbauen, die auf stdin wartet. Der Prozess muss statuslos bleiben; die KI speichert den Kontext.

### Dependency Analysis

- Keine neuen Dependencies erforderlich.

### Testing Patterns

- Eigene asynchrone Testfunktionen in `tests/test_server.py` via `@patch("altiplano.server._request", new_callable=AsyncMock)`.
- Teste sowohl den Fall `confirm=False` (Prüfung auf `ValueError`) als auch `confirm=True` (Prüfung auf Aufruf von `_request` mit `DELETE`).

## Architekturentscheidungen

### Gewählter Ansatz

Bestätigung über booleschen Tool-Parameter. Dies ist der empfohlene Weg bei MCP-Integrationen, um LLMs zu einer Unterbrechung zu zwingen, da sie auf Fehlertext ("You MUST ask...") reagieren.

### Erwogene Alternativen

- *Alternative:* Ein separates `request_delete` Tool, welches ein Token zurückgibt, und ein `confirm_delete` Tool. 
- *Entscheidung:* Over-Engineering. Ein `confirm=True` Parameter mit einem harten Error bei `False` ist für LLMs verständlich genug und einfacher zu warten.

### Security, Performance, Maintainability

- **Security:** Verhindert Halluzinationen, die zu Datenverlust führen.
- **Performance:** Vernachlässigbar.
- **Maintainability:** Pattern ist universell für zukünftige Delete-Tools adaptierbar.

## Datenmodell und API-Mapping

- `delete_task`: `DELETE /tasks/{task_id}`
- `delete_comment`: `DELETE /tasks/{task_id}/comments/{comment_id}`
- `delete_bucket`: `DELETE /projects/{project_id}/views/{view_id}/buckets/{bucket_id}` (wobei `view_id` wie bei `update_bucket` über `_resolve_kanban_view_id(project_id)` geholt wird).

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - ADD: Die 3 neuen FastMCP Tools.
- `tests/test_server.py` - ADD: Tests für die 3 Tools.

### Neue Dateien

Keine neuen Dateien.

## Implementation Plan

### Phase 1: Core Implementation

Implementierung der drei Tools mit dem Bestätigungsparadigma in `server.py`.

### Phase 2: Testing and Validation

Tests für alle drei Tools in `test_server.py` (jeweils mit und ohne `confirm=True`).

## Step-by-Step Tasks

### Task 1: UPDATE src/altiplano/server.py

**Status:** done  
**Ziel:** Hinzufügen der Lösch-Tools für Tasks, Comments und Buckets.  
**IMPLEMENT:** 
- Erstelle `@mcp.tool()` `delete_task(task_id: int, confirm: bool = False)`.
- Erstelle `@mcp.tool()` `delete_comment(task_id: int, comment_id: int, confirm: bool = False)`.
- Erstelle `@mcp.tool()` `delete_bucket(project_id: int, bucket_id: int, confirm: bool = False)`. Nutze hier `view_id = await _resolve_kanban_view_id(project_id)`.
- Integriere die Exception bei `not confirm` und den `DELETE` Call bei `confirm`.  
**PATTERN:** `remove_assignee` (für generisches `DELETE`), Bestätigungs-Pattern.  
**GOTCHA:** `delete_bucket` benötigt den View-Resolve-Schritt.  
**ACCEPTANCE CRITERIA:**
- [x] 3 Tools sind registriert und nutzen `confirm` Flag.
- [x] Aufruf ohne `confirm` bricht korrekt ab.

**VALIDATE:**
- `uv run pytest` (Erfolgreich ausgeführt, Syntax ist valide)

### Task 2: UPDATE tests/test_server.py

**Status:** done  
**Ziel:** Testabdeckung der Lösch-Tools sicherstellen.  
**IMPLEMENT:** 
- Test `test_tool_delete_task` (mit/ohne confirm).
- Test `test_tool_delete_comment` (mit/ohne confirm).
- Test `test_tool_delete_bucket` (mit/ohne confirm).
- In `test_mcp_initialization` die drei neuen Tools ins Assert aufnehmen.  
**PATTERN:** `test_tool_delete_task_attachment`  
**ACCEPTANCE CRITERIA:**
- [x] 100% Pass Rate für neue Tools in pytest.
- [x] `ValueError` bei fehlendem `confirm` wird in Tests validiert.

**VALIDATE:**
- `uv run pytest` (26/26 Tests bestanden, inklusive der neuen Tests für die Bestätigung und Fehlerbehandlung)

## Testing Strategy

### Unit / Integration Tests

Tests mocken `_request` und prüfen ob die HTTP-Methode "DELETE" und die Pfade korrekt konstruiert wurden. 

### Edge Cases

- `confirm=False` bei LLM-Aufruf.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

Über MCP Inspector prüfen:
1. `delete_task` ohne confirm aufrufen -> Fehler muss erscheinen.
2. `delete_task` mit confirm=true aufrufen -> `DELETE` muss passieren.

## Acceptance Criteria

- [x] Alle 3 Löschfunktionen existieren als MCP Tools.
- [x] Zweistufiger Bestätigungs-Prozess ist via `confirm` Parameter durchgesetzt.
- [x] Tests validieren das Abbrechen bei `confirm=False`.

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Das Bestätigungs-Pattern muss prominent in der `docs/starter-kit-usage/`-Doku platziert werden, damit Anwender wissen, dass die KI bei Zerstörungsbefehlen immer nachfragen wird.

## Notes and Trade-offs

Die KI könnte bei schlechter Instruktion das `confirm=true` Argument direkt beim ersten Mal übergeben. Gegen mutwillige "System Prompt Overrides" ist der Server hiermit nicht immun; es dient vor allem dem Schutz gegen Flüchtigkeits-Entscheidungen der KI (Halluzinationen).
