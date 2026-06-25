# Plan: Task-Beziehungen

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001
**Quelle:** User Request (`/plan-feature Task-Beziehungen`), PRD v006 (Extended-/Luxus-Version)  
**Confidence Score:** 10/10 (API Endpunkte wurden erfolgreich via Test-Skript gegen die echte Instanz verifiziert)
## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Medium |
| Primär betroffene Systeme | server.py / Tests |
| Abhängigkeiten | Vikunja API Relations-Endpunkte |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Das Feature "Task-Beziehungen" (Task Relations) fügt dem MCP-Server die Fähigkeit hinzu, Relationen zwischen Aufgaben abzubilden und zu verwalten. Dies umfasst das Setzen von Abhängigkeiten (z.B. blockiert durch, Subtask, Duplicate) sowie das Auflisten und Entfernen dieser Relationen. Dies unterstützt komplexe Planungs- und Organisationsszenarien durch das LLM, insbesondere bei größeren Projekten.

## User Story

```text
Als KI-Client (bzw. Personal User via KI)
möchte ich Beziehungen zwischen Tasks abrufen, setzen und löschen können,
damit Abhängigkeiten, Subtasks und Duplikate sauber im Projekt abgebildet werden.
```

## Problem Statement

Bisher können Tasks nur isoliert oder innerhalb von Projekten/Buckets betrachtet werden. Es fehlt die Möglichkeit, hierarchische (Parent/Subtask) oder logische (Blockaden, Duplikate) Abhängigkeiten zwischen Aufgaben abzubilden. Das LLM kann somit keine Projektpläne erstellen, in denen Tasks logisch aufeinander aufbauen.

## Solution Statement

Implementierung von drei neuen MCP-Tools, die direkt mit den Vikunja Relations-Endpunkten interagieren:
- `list_task_relations`: Ruft bestehende Relationen für einen Task ab.
- `add_task_relation`: Erstellt eine Beziehung (z.B. "subtask", "blocking") zu einem anderen Task.
- `remove_task_relation`: Entfernt eine bestehende Beziehung.

## Scope

### Im Scope

- Auflisten von Task-Beziehungen (`list_task_relations`)
- Setzen von Task-Beziehungen (`add_task_relation`) mit den gängigen Relationstypen (parent, subtask, related, duplicate, blocking, blocked)
- Löschen von Task-Beziehungen (`remove_task_relation`)
- Mocks und Tests für diese drei Tools

### Nicht im Scope

- Komplexe graphenbasierte Auswertungen (dies übernimmt die KI clientseitig).
- Bulk-Updates von Relationen.

## Rollen und Berechtigungen

Keine neuen Rollen erforderlich. Die Ausführung erfolgt über den bestehenden API-Token in `server.py`.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Erweiterung um drei neue Tool-Definitionen.
- `tests/test_server.py` - Warum: Neue `httpx`-Mocks für die Relations-Aufrufe analog zu bestehenden Tests (z.B. `test_tool_list_task_attachments`).

### Relevante Dokumentation

- PRD `docs/project/prds/vikunja-mcp-server-v006.md` - Erwähnt "Tool zum Setzen von Relationen (Parent/Child, Blockaden)".

## Codebase Intelligence

### Projektstruktur und Architektur

Neue Tools werden analog zu den bestehenden Label- und Attachment-Tools in `src/altiplano/server.py` eingebaut.

### Patterns to Follow

- Naming: `list_task_relations`, `add_task_relation`, `remove_task_relation`
- Fehlerbehandlung: Verwendung der Standard-Exception-Muster in `_request`.
- FastMCP: `@mcp.tool()` Dekoratoren mit englischen, aussagekräftigen Docstrings.
- API-Anbindung: Verwendung von `await _request(...)`.

### Dependency Analysis

Keine neuen Dependencies erforderlich. Wir verwenden `httpx` und `fastmcp`.

### Testing Patterns

Wir nutzen `unittest.mock.patch` und `AsyncMock` für `_request` in `pytest`, wie bereits in `tests/test_server.py` etabliert.

## Architekturentscheidungen

### Gewählter Ansatz

Direktes Mapping auf die Vikunja API:
- `GET /tasks/{task_id}` (Vikunja liefert Relationen direkt im Feld `related_tasks` des Task-Objekts mit)
- `PUT /tasks/{task_id}/relations` (Payload: `{"other_task_id": 123, "relation_kind": "subtask"}`)
- `DELETE /tasks/{task_id}/relations/{relation_kind}/{other_task_id}` (Erfolgreich verifiziert)

### Security, Performance, Maintainability

- Security: Tool Parameter streng typisiert (`task_id: int`, `other_task_id: int`, `relation_kind: str`).
- Performance: Keine komplexen n+1 Queries. Wir rufen Relationen nur explizit auf Nachfrage ab.

## Datenmodell und API-Mapping

Die Vikunja-API liefert Relationen üblicherweise als Liste von Objekten, die u.a. `task_id`, `other_task_id` und `relation_kind` enthalten. Das Mapping wird die wesentlichen Felder filtern und an das LLM zurückgeben.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - UPDATE: Hinzufügen der Relations-Tools.
- `tests/test_server.py` - UPDATE: Hinzufügen der entsprechenden Mocks und Unit Tests.

## Implementation Plan

### Phase 1: Foundation (Recherche & Verifizierung API)
Prüfen der genauen Vikunja API-Struktur für `GET`, `PUT` und `DELETE` von Relationen.

### Phase 2: Core Implementation
Einbau von `list_task_relations`, `add_task_relation` und `remove_task_relation` in `server.py`.

### Phase 3: Testing and Validation
Schreiben der `pytest` Mocks und lokale Ausführung von `uv run pytest`.

## Step-by-Step Tasks

### Task 1: UPDATE server.py mit Relations-Tools

**Status:** done  
**Ziel:** Drei neue Tools in `server.py` registrieren.  
**IMPLEMENT:**
1. Füge `@mcp.tool()` `list_task_relations(task_id: int) -> dict` hinzu. Implementierung ruft `GET /tasks/{task_id}` auf und extrahiert das Feld `related_tasks`.
2. Füge `@mcp.tool()` `add_task_relation(task_id: int, other_task_id: int, relation_kind: str) -> dict` hinzu. Implementierung ruft `PUT /tasks/{task_id}/relations` auf.
3. Füge `@mcp.tool()` `remove_task_relation(task_id: int, other_task_id: int, relation_kind: str) -> dict` hinzu. Implementierung ruft `DELETE /tasks/{task_id}/relations/{relation_kind}/{other_task_id}` auf.
**PATTERN:** Orientierung an `add_label` / `remove_label`.  
**GOTCHA:** `list_task_relations` muss beachten, dass `related_tasks` ggf. `null` oder nicht vorhanden ist.  
**ACCEPTANCE CRITERIA:**
- [x] Tools sind in `server.py` definiert.
- [x] Klare Docstrings in Englisch.

**VALIDATE:**
- Manuelle Prüfung durch MCP Inspector: Tools werden gelistet.
- **Automatische Prüfung:** Mocks in `test_server.py` erstellt und verifiziert.

### Task 2: UPDATE test_server.py mit Mocks für Relations

**Status:** done  
**Ziel:** Tests für die drei neuen Tools schreiben.  
**IMPLEMENT:** 
- Erstelle `test_tool_list_task_relations`, `test_tool_add_task_relation`, `test_tool_remove_task_relation` mit `AsyncMock` für `_request`.
- Erweitere `test_mcp_initialization`, sodass die neuen Tools im Tool-Namen-Array erwartet werden.
**PATTERN:** Orientierung an `test_tool_add_label`.  
**ACCEPTANCE CRITERIA:**
- [x] 3 neue Tests in `test_server.py`.
- [x] `test_mcp_initialization` ist aktualisiert.

**VALIDATE:**
- `uv run pytest` (Muss 100% grün sein). -> Alle 30 Tests bestanden.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. Server starten: `npx @modelcontextprotocol/inspector uv run altiplano`
2. `list_task_relations(task_id=XYZ)` aufrufen
3. `add_task_relation(task_id=XYZ, other_task_id=ABC, relation_kind="blocking")` ausführen und verifizieren.

## Acceptance Criteria

- [x] Feature implementiert alle Scope-Anforderungen.
- [x] Typvalidierung und API-Fehlerbehandlung sind korrekt.
- [x] Relevante pytest-Tests sind ergänzt und grün.

## Completion Checklist

- [x] Alle Tasks sind umgesetzt.
- [x] Jeder Task wurde validiert.
- [x] Alle Tests laufen erfolgreich.
- [x] Feature ist bereit für `/document` und `/commit`.

## Documentation Notes

Das Feature "Task-Beziehungen" wurde erfolgreich in diesen Dateien dokumentiert:
* [user-guide.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/task-beziehungen/user-guide.md)
* [developer-notes.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/task-beziehungen/developer-notes.md)

## Offene Fragen

- Keine (API-Endpunkte wurden durch manuelles Script verifiziert).
