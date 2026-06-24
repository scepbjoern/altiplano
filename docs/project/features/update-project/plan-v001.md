# Plan: update_project Tool

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001
**Quelle:** User Request, PRD v004  
**Confidence Score:** 10/10 (Vikunja API conventions are well understood, existing tools provide a clear pattern)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | fastmcp, httpx, server.py, Tests |
| Abhängigkeiten | Vikunja API `POST /projects/{id}` Endpoint |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Ein neues MCP-Tool, das es dem KI-Agenten ermöglicht, bestehende Projekte in Vikunja zu aktualisieren. Der Agent kann den Projektnamen, die Beschreibung, die Farbe und die Verschachtelung (Parent-Projekt) ändern.

## User Story

```text
Als Personal User
möchte ich Projektnamen, Beschreibungen und Farben via KI korrigieren können,
damit ich meine Ordnerstruktur und Projektübersicht bequem und automatisiert aufräumen kann.
```

## Problem Statement

Aktuell kann die KI über `create_project` zwar Projekte anlegen, aber Änderungen an Projekten (wie Namenskorrekturen, Farbänderungen oder das Verschieben in ein anderes Parent-Projekt) sind nicht möglich. 

## Solution Statement

Das neue `update_project` Tool nutzt die Vikunja-API (`POST /projects/{project_id}`), um selektive Änderungen an einem Projekt vorzunehmen. Analog zu `update_task` werden nur die explizit übergebenen Parameter an die API gesendet (PATCH-ähnliches Verhalten via POST).

## Scope

### Im Scope

- Update von `title` (Name des Projekts)
- Update von `description`
- Update von `hex_color` (Farbe des Projekts)
- Update von `parent_project_id` (Verschachtelung)

### Nicht im Scope

- Archivieren von Projekten (`is_archived`)
- Löschen von Projekten

## Rollen und Berechtigungen

Wird über den Vikunja-API-Token gesteuert. Der Token benötigt Schreibrechte für Projekte.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Existierende `update_task` Funktion als Pattern für partielle Updates.
- `tests/test_server.py` - Warum: API-Mocking Pattern für Tests.

### Relevante Dokumentation

- PRD v004 - Abschnitt 6 (MVP) und 8 (Kernfunktionen).

## Codebase Intelligence

### Projektstruktur und Architektur

Das Projekt nutzt `FastMCP`. Neue Tools werden mit dem Dekorator `@mcp.tool()` in `server.py` registriert. API-Anfragen laufen über die asynchrone `_request`-Funktion.

### Patterns to Follow

- Naming: `update_project`
- Fehlerbehandlung: Expliziter `ValueError`, falls keine Felder zum Update übergeben werden.
- API-Anbindung: `POST /projects/{project_id}` für Updates, Payload wird inkrementell aus nicht-`None` Werten aufgebaut.

### Anti-Patterns to Avoid

- Keine Änderungen am bestehenden `create_project` Code, außer ggf. Docstring.
- Keine "Full-Replacement"-Payloads: Es dürfen nur definierte Felder überschrieben werden.

### Dependency Analysis

Keine neuen Dependencies erforderlich.

### Testing Patterns

`pytest` mit `unittest.mock.patch` auf `altiplano.server._request` (AsyncMock).

## Architekturentscheidungen

### Gewählter Ansatz

Analog zu `update_task` werden alle optionalen Argumente mit `None` initialisiert. Ein `payload` Dictionary wird nur mit den Werten befüllt, die nicht `None` sind. Falls `payload` leer ist, wird ein `ValueError("No fields to update")` geworfen.

### Security, Performance, Maintainability

- Security: Durch das inkrementelle Payload-Aufbauen wird verhindert, dass durch Nichtangabe von Feldern versehentlich Daten in Vikunja gelöscht/geleert werden.
- Maintainability: Englischsprachige Docstrings für FastMCP, sauberes Type-Hinting.

## Datenmodell und API-Mapping

- `task_id` -> entfällt, es ist `project_id: int`
- `title: str | None`
- `description: str | None`
- `hex_color: str | None`
- `parent_project_id: int | None`

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - ADD: `update_project` Funktion.
- `tests/test_server.py` - ADD: Unit-Test für `update_project`.

### Neue Dateien

- Keine

## Implementation Plan

### Phase 1: Core Implementation
Tool `update_project` in `server.py` definieren und implementieren.

### Phase 2: Testing and Validation
Unit-Test in `test_server.py` ergänzen und validieren.

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Jeder Task ist atomic und einzeln validierbar.

### Task 1: ADD update_project Tool

**Status:** planned  
**Ziel:** Das Tool `update_project` ist im Server registriert und sendet korrekte API-Requests.  
**IMPLEMENT:** In `src/altiplano/server.py` nach `create_project` (oder bei den project-Tools) die asynchrone Funktion `update_project(project_id: int, title: str | None = None, description: str | None = None, hex_color: str | None = None, parent_project_id: int | None = None) -> dict` hinzufügen. Payload-Aufbau analog zu `update_task`. API-Call: `await _request("POST", f"/projects/{project_id}", json=payload)`.  
**PATTERN:** `update_task` in `server.py`  
**GOTCHA:** `ValueError` werfen, wenn keine Parameter gesetzt sind.  
**ACCEPTANCE CRITERIA:**

- [ ] `update_project` ist mit `@mcp.tool()` dekoriert.
- [ ] Optionale Argumente werden berücksichtigt.
- [ ] Leere Updates werden abgefangen.

**VALIDATE:**

- `uv run pytest` (nachdem der Test in Task 2 geschrieben wurde)

### Task 2: ADD Tests für update_project

**Status:** planned  
**Ziel:** Die Tool-Logik ist durch API-Mocks testgeprüft.  
**IMPLEMENT:** In `tests/test_server.py` die Funktion `test_tool_update_project` hinzufügen. Zwei Fälle testen: Erfolgreiches Update und der `ValueError` Fall.  
**PATTERN:** `test_tool_list_projects` in `tests/test_server.py`  
**IMPORTS:** `update_project` von `altiplano.server` importieren.  
**ACCEPTANCE CRITERIA:**

- [ ] Erfolgreiches Update ruft `_request` mit `POST` und den übergebenen Werten auf.
- [ ] Fehlerfall (`No fields to update`) wirft Exception.

**VALIDATE:**

- `uv run pytest`

## Testing Strategy

### Unit / Integration Tests

- Testen, ob der `payload` nur die explizit übergebenen Keys enthält.
- Testen, ob der Endpoint `POST /projects/{id}` aufgerufen wird.

### Edge Cases

- Aufruf von `update_project(project_id=123)` (ohne weitere Parameter) muss failen.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. Server starten via `npx @modelcontextprotocol/inspector uv run altiplano`
2. `update_project` mit einer gültigen Projekt-ID und `{ "hex_color": "123456" }` aufrufen.
3. Ergebnis in der Vikunja UI oder per `list_projects` (falls bereits ausgebaut) validieren.

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen
- [ ] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [ ] Relevante pytest-Tests sind ergänzt und grün
- [ ] Relevante manuelle Flows sind validiert
- [ ] Keine bekannten Regressionen in bestehenden Kernworkflows
- [ ] Dokumentationsbedarf ist notiert

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] Alle relevanten Tests laufen erfolgreich oder Ausnahmen sind begründet
- [ ] Manuelle Prüfung (MCP Inspector / Claude Desktop) ist dokumentiert
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt
- [ ] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Das Tool muss in der künftigen Entwickler- und Endanwenderdokumentation (`docs/starter-kit-usage`) erwähnt werden.

## Notes and Trade-offs

- Wir verlassen uns darauf, dass `POST /projects/{id}` der korrekte Endpoint für partielle Updates in Vikunja ist. Falls das nicht zutrifft, muss der Request auf `PUT` oder ein anderes Format angepasst werden. Die bestehenden API-Konventionen (wie in `update_task` genutzt) deuten stark auf `POST` hin.

## Offene Fragen

- Keine.

## Plan Review Notes

(Wird später ergänzt)
