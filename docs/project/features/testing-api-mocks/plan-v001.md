# Plan: Testing & API-Mocks

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001
**Quelle:** User Request (`/plan-feature Testing & API-Mocks`) und PRD v003  
**Confidence Score:** 9/10 - Klar umrissene Standardaufgabe im Python-Ökosystem. Das Patchen von internen API-Wrappern ist ein bewährtes und stabiles Pattern.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Chore / Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | Tests (`tests/`) |
| Abhängigkeiten | `pytest` (und `unittest.mock` aus der Standardbibliothek) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Initiales Setup von sauberen API-Mocks für `httpx`, um die lokale Testausführung der MCP-Tools gegen die Vikunja-Schnittstellen abzusichern, ohne echte Requests an die Produktivinstanz abzusetzen.

## User Story

```text
Als Entwickler
möchte ich lokale Tests schreiben, die API-Calls mocken,
damit ich neue Tools sicher entwickeln kann, ohne meine Vikunja-Produktivdaten zu gefährden.
```

## Problem Statement

Laut PRD und Coding-Regeln sind echte API-Requests in Tests strikt verboten. Bisher existiert in `tests/test_server.py` nur ein Test, der die FastMCP-Registrierung prüft, aber kein Pattern, um die asynchronen `httpx`-Aufrufe in `server.py` sauber für die Tool-Tests zu mocken.

## Solution Statement

Einführung eines wiederverwendbaren Mock-Patterns via `unittest.mock.AsyncMock`, mit dem API-Responses in Tests kontrolliert simuliert werden können. Ein initialer Test für `list_projects` wird als Referenzimplementierung bereitgestellt.

## Scope

### Im Scope

- Setup eines sauberen Mock-Patterns für Vikunja-API-Requests in `test_server.py`.
- Test-Abdeckung für mindestens ein bestehendes Tool (`list_projects`) zur Demonstration des Patterns.

### Nicht im Scope

- Vollständige Test-Abdeckung für alle bereits bestehenden Tools (laut Brownfield-Pragmatismus im `KILO_INSTRUCTIONS.md` nicht erforderlich).
- Integration-Tests mit einer echten Vikunja-Instanz.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Dort wird die Helferfunktion `_request` definiert und von allen Tools verwendet.
- `KILO_INSTRUCTIONS.md` - Warum: Enthält den "Brownfield-Pragmatismus", der echtes API-Testing verbietet.

## Codebase Intelligence

### Projektstruktur und Architektur

Die asynchrone Kommunikation passiert zentral in `src/altiplano/server.py` in der Funktion `_request(method, path, **kwargs)`. Diese Funktion kapselt `httpx.AsyncClient` und verarbeitet die Responses zentral.

### Patterns to Follow

- **Mocking:** Anstatt externe Libraries hinzuzufügen, wird `unittest.mock.patch` genutzt, um `altiplano.server._request` asynchron zu mocken. Das hält die Dependencies minimal und ist exakt auf den internen Flow zugeschnitten.
- **Naming:** Tests für Tools beginnen mit `test_tool_<tool_name>`.

### Anti-Patterns to Avoid

- Keine Testanfragen an eine echte URL. Keine Credentials in Tests voraussetzen.

## Architekturentscheidungen

### Gewählter Ansatz

Wir patchen die interne Helferfunktion `altiplano.server._request` in den Tests mittels `@patch("altiplano.server._request", new_callable=AsyncMock)`.
Begründung: Es ist die pragmatischste Lösung (Brownfield-Ansatz). Wir müssen nicht den kompletten `httpx.AsyncClient` mocken, sondern nur unsere standardisierte Schnittstelle.

### Erwogene Alternativen

- Alternative: Einbindung von `pytest-httpx` oder `respx` - Entscheidung: Wurde nicht gewählt, um die Abhängigkeiten in `pyproject.toml` minimal zu halten und da alle Tools sauber durch die zentrale Funktion `_request` gehen.

## Betroffene Dateien

### Bestehende Dateien

- `tests/test_server.py` - Aktion: Ergänzung des Mock-Setups und eines Beispiel-Tests für `list_projects`.

## Implementation Plan

### Phase 1: Foundation (Mocking Pattern)

- Nutzung von `unittest.mock.patch` auf `altiplano.server._request`.

### Phase 2: Core Implementation (Beispiel-Test)

- Schreiben eines asynchronen Tests für das Tool `list_projects`, der den Mock nutzt und eine vordefinierte Projektliste zurückgibt.

### Phase 3: Validation

- Ausführung von `uv run pytest` zur Verifikation.

## Step-by-Step Tasks

### Task 1: UPDATE `tests/test_server.py`

**Status:** done  
**Ziel:** Mock-Pattern etablieren und einen Test für `list_projects` schreiben.  
**IMPLEMENT:** 
- Importiere `patch` und `AsyncMock` aus `unittest.mock`.
- Importiere `list_projects` aus `altiplano.server`.
- Schreibe `async def test_tool_list_projects():`.
- Nutze `@patch("altiplano.server._request", new_callable=AsyncMock)` als Dekorator.
- Setze den Return-Value des Mocks auf eine gefakte API-Response (z.B. `[{"id": 1, "title": "Test Project", "parent_project_id": 0, "is_archived": False}]`).
- Rufe `await list_projects()` auf und aserte, dass das Resultat der gemockten Struktur entspricht.
- Aserte, dass `_request` mit den korrekten Argumenten (`"GET", "/projects"`) aufgerufen wurde.
**PATTERN:** Asynchrones Testing mit `pytest.mark.anyio`.  
**IMPORTS:** `from unittest.mock import patch, AsyncMock`, `from altiplano.server import list_projects`.  
**GOTCHA:** Da das Tool in FastMCP registriert ist, rufen wir für Unittests direkt die asynchrone Python-Funktion `list_projects` auf.  
**ACCEPTANCE CRITERIA:**
- [x] `_request` wird erfolgreich gemockt.
- [x] Test für `list_projects` ist grün und erreicht keine echte API.

**VALIDATE:**
- `uv run pytest tests/test_server.py` (Erfolgreich ausgeführt: 2 Tests bestanden)

## Testing Strategy

- Wir testen direkt die asynchronen Tool-Funktionen, indem wir `_request` mocken, was jeglichen externen Traffic unterbindet.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen.
- [ ] Keine echte API wird im Test aufgerufen.
- [ ] Relevante pytest-Tests sind ergänzt und grün.

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt

## Offene Fragen

- Keine.
