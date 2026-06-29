# Plan: Labels in create_task

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-29  
**Plan-Version:** v001
**Quelle:** User Request, PRD v011  
**Confidence Score:** 9/10 - Klarer Scope, isolierte Änderung, bestehendes API-Pattern für Labels kann iterativ genutzt werden.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py / Tests |
| Abhängigkeiten | Vikunja API Label-Endpoint |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-29 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Der MCP-Server unterstützt beim Erstellen einer Aufgabe (`create_task`) bisher keine Labels. Nutzer müssen Aufgaben erstellen und danach pro Label einen separaten `add_label`-Aufruf tätigen.
Dieses Feature erlaubt es, beim Aufruf von `create_task` direkt eine optionale Liste von Label-IDs (`label_ids`) mitzugeben. Der Server verarbeitet diese nach der Task-Erstellung automatisch und gibt bei ungültigen Labels verständliche Teilfehler zurück.

## User Story

```text
Als Nutzer
möchte ich gefiltert Tasks abrufen und erstellen (inklusive direkter Zuweisung von Labels),
damit ich Tool-Aufrufe spare und Arbeitsabläufe flüssiger werden.
```

## Problem Statement

Fehlender Label-Support in `create_task` zwingt LLMs zu ineffizienten iterativen Aufrufen von `add_label`, was Tokens kostet, fehleranfällig ist und den Benutzer warten lässt.

## Solution Statement

`create_task` erhält den Parameter `label_ids: list[int] | None = None`. Der MCP-Server führt zuerst wie bisher den `PUT`-Request zur Task-Erstellung aus. Anschliessend iteriert er über die `label_ids` und fügt jedes Label einzeln per `PUT /tasks/{task_id}/labels` hinzu. Schlägt eine Label-Zuweisung fehl, fängt der Server den Fehler ab und listet ihn in der Response auf, sodass der Task zwar erstellt ist, der Nutzer aber über das ungültige Label informiert wird.

## Scope

### Im Scope

- `label_ids` (Liste von Ganzzahlen) als optionaler Parameter in `create_task`.
- Sequentielle API-Aufrufe an Vikunja für die Label-Zuweisung nach Task-Erstellung.
- Abfangen von Fehlern bei einzelnen Label-Zuweisungen (Partial Errors) in der Rückgabe.
- Unit-Tests für den Erfolgs- und Fehlerfall.

### Nicht im Scope

- Textbasierte Labels (`labels: ["@online"]`) – explizit gemäss PRD vorerst ausgeschlossen.

## Rollen und Berechtigungen

Keine Änderung. Es gelten die Berechtigungen des Vikunja API-Tokens.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: `create_task` und `add_label` Tools.
- `tests/test_server.py` - Warum: Mocking-Ansatz für `_request`.

## Codebase Intelligence

### Projektstruktur und Architektur

Die Datei `src/altiplano/server.py` enthält alle Tools. API-Requests werden über `_request` abgewickelt, was bei HTTP-Fehlern `RuntimeError` wirft.

### Patterns to Follow

- Fehlerbehandlung: Ein `try...except RuntimeError as exc` Block bei den Label-Zuweisungen, um den Flow nicht zu unterbrechen.
- FastMCP: Der Docstring von `create_task` muss den neuen Parameter `label_ids` dokumentieren.

### Anti-Patterns to Avoid

- Keine generellen `except Exception` Blöcke, fange nur `RuntimeError` (vom `_request` Helper geworfen) ab.

### Dependency Analysis

Keine neuen Dependencies.

### Testing Patterns

`pytest` Tests nutzen `@patch("altiplano.server._request", new_callable=AsyncMock)`.
Wir müssen einen Side-Effect für `mock_request` schreiben, der bei `PUT /projects/1/tasks` das Task-Dict zurückgibt und bei `PUT /tasks/.../labels` entweder Erfolg (`{"ok": True}`) oder einen Fehler wirft.

## Architekturentscheidungen

### Gewählter Ansatz

Da Vikunja im `PUT /projects/{id}/tasks` Endpoint möglicherweise nicht direkt eine Array-basierte Label-Zuweisung zulässt, iterieren wir serverseitig. Das schützt uns vor API-Änderungen und nutzt den bereits existierenden `/tasks/{task_id}/labels` Endpoint analog zu `add_label`.

### Erwogene Alternativen

- Alternative: Direktes Senden von `label_ids` im Payload von `PUT /projects/{id}/tasks`. - Entscheidung: Abgelehnt, da nicht sicher dokumentiert und potenziell inkompatibel mit Vikunja-Pflichtfeldern. Die serverseitige Iteration ist sicherer.

### Security, Performance, Maintainability

- Security: Unverändert.
- Performance: Ein API-Call für Task-Erstellung + N API-Calls für N Labels. Da N meist klein ist (1-3), ist das akzeptabel.
- Maintainability: Rückgabe eines `label_errors` Arrays im Response-Dict, was für den LLM-Client klar lesbar ist.

## Datenmodell und API-Mapping

Neuer Parameter in `create_task`: `label_ids: list[int] | None = None`.
Return-Dict von `create_task` wird um `label_errors: list[str]` ergänzt, falls Fehler auftreten.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Signatur und Logik von `create_task` erweitern.
- `tests/test_server.py` - Tests für `create_task` anpassen/erweitern.
- `TASKS.md` - Index nachführen.

## Implementation Plan

### Phase 1: Core Implementation

`create_task` in `server.py` erhält den `label_ids`-Parameter und iteriert nach Erstellung über die Labels.

### Phase 2: Testing and Validation

Tests in `test_server.py` hinzufügen (Erfolgsfall und Partial-Error-Fall).

## Step-by-Step Tasks

### Task 1: UPDATE src/altiplano/server.py

**Status:** planned  
**Ziel:** `create_task` unterstützt `label_ids`.  
**IMPLEMENT:** 
- Signatur: `label_ids: list[int] | None = None` hinzufügen.
- Docstring aktualisieren (Hinweis auf `label_ids`).
- Nach `res = await _request(...)`: Wenn `label_ids` existiert, über die IDs iterieren.
- Für jede ID: `try: await _request("PUT", f"/tasks/{res['id']}/labels", json={"label_id": label_id}) except RuntimeError as exc: errors.append(str(exc))`
- Wenn `errors` nicht leer ist, `res["label_errors"] = errors` setzen.
- `return res`  
**PATTERN:** Fehlerbehandlung ähnlich wie `_request` Exception Wrapping.  
**ACCEPTANCE CRITERIA:**
- [ ] Signatur ist aktualisiert.
- [ ] Erfolgreiche Zuweisung schlägt nicht fehl.
- [ ] Fehlerhafte Zuweisungen werden in `label_errors` gesammelt.

### Task 2: UPDATE tests/test_server.py

**Status:** planned  
**Ziel:** Testabdeckung für die neuen Funktionalitäten in `create_task`.  
**IMPLEMENT:** 
- Test `test_tool_create_task` (falls vorhanden, sonst neu) mit und ohne `label_ids`.
- Test `test_tool_create_task_with_label_errors` schreiben, in dem der Mock für einen Label-Call einen Fehler wirft.  
**PATTERN:** `test_tool_complete_task_with_comment` (Mock mit Side-Effect für verschiedene Routen).  
**ACCEPTANCE CRITERIA:**
- [ ] Test für erfolgreiche Erstellung inkl. Labels ist grün.
- [ ] Test für Erstellung mit Teilfehler bei Labels ist grün und prüft auf `label_errors`.

## Testing Strategy

### Unit / Integration Tests

Tests nutzen `AsyncMock` mit `side_effect`, um je nach `method` und `path` unterschiedliche Rückgaben (oder Exceptions) zu simulieren.

### Edge Cases

- `label_ids` ist eine leere Liste `[]` -> Keine Zuweisungen, kein Fehler.
- Eine von mehreren Label-IDs existiert nicht -> Task wird erstellt, gutes Label zugewiesen, ungültiges Label wirft Exception, welche in `label_errors` erscheint.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest tests/test_server.py -k create_task
```

### Level 2: Manual Validation

Start des MCP Servers (`uv run altiplano`) und Aufruf von `create_task` via Inspector mit einer gültigen und einer ungültigen Label-ID.

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen
- [ ] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [ ] Relevante pytest-Tests sind ergänzt und grün
- [ ] Manuelle Flows validierbar
- [ ] Dokumentationsbedarf notiert

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] Alle relevanten Tests laufen erfolgreich
- [ ] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Endanwender sollten in der Usage-Dokumentation (sofern es eine gibt) darauf hingewiesen werden, dass sie Labels nun in einem Schritt zuweisen können.

## Notes and Trade-offs

Sequentielle API-Requests erhöhen die Latenz leicht, was bei lokaler Ausführung jedoch tolerabel ist.

## Offene Fragen

- Keine

## Plan Review Notes

Nicht relevant.
