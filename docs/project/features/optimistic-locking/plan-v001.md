# Plan: Optimistic Locking Support

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001  
**Quelle:** User Request, PRD v005  
**Confidence Score:** 10/10 (Das Verhalten von Vikunja bezüglich der optimistischen Konkurrenzsteuerung über das `updated`-Feld ist verstanden und lässt sich analog zu bestehenden Requests implementieren)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Bugfix / Capability |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py, Tests |
| Abhängigkeiten | Vikunja API GET/POST Endpunkte für Projekte und Tasks |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan für Optimistic Locking erstellt |

## Feature Description

Integration der optimistischen Konkurrenzsteuerung (Optimistic Locking) der Vikunja-API. Alle Tools, die schreibend/ändernd auf bestehende Projekte oder Tasks zugreifen (per `POST`), müssen zuvor den aktuellen Zustand per `GET` abfragen, den `updated`-Zeitstempel extrahieren und diesen im Payload des Update-Requests mitschicken. Dies verhindert Fehler des Typs `412 Precondition Failed`.

## User Story

```text
Als Personal User
möchte ich, dass Projekt- und Task-Updates (wie das Verschieben von Projekten ins Root-Verzeichnis) zuverlässig funktionieren und nicht aufgrund von Versionskonflikten der API mit 412 Precondition Failed fehlschlagen.
```

## Problem Statement

Vikunja erzwingt für Updates an Projekten und Tasks (via `POST /projects/{id}` und `POST /tasks/{id}`) optimistisches Sperren. Wenn der Client keinen oder einen veralteten `updated`-Zeitstempel im Payload mitschickt, antwortet die API mit `412 Precondition Failed`. Die aktuellen Implementierungen der MCP-Tools senden diesen Zeitstempel nicht mit.

## Solution Statement

Wir passen alle Tools, die ein Update an einem Projekt oder Task durchführen, so an, dass sie:
1. Vorab das Objekt per `GET` abrufen (z.B. `GET /projects/{id}` oder `GET /tasks/{id}`).
2. Den Wert des Feldes `updated` aus der API-Antwort auslesen.
3. Diesen Wert unter dem Key `updated` in den Update-Payload (`POST`) einfügen.

## Scope

### Im Scope

- Anpassung von `update_project` (Projekt-Updates).
- Anpassung von `update_task` (Task-Updates).
- Anpassung von `set_reminders` (Task-Reminder-Updates).
- Anpassung von `complete_task` (Task-Status-Updates).
- Anpassung von `move_task_to_project` (Task-Projekt-Updates).
- Aktualisierung der Mocks in `tests/test_server.py`, um die doppelten Requests (erst GET, dann POST) abzubilden.

### Nicht im Scope

- Optimistic Locking für Neuanlagen (`create_project`, `create_task`), da diese per `PUT` neu erzeugt werden und noch keinen vorherigen Zustand haben.
- Automatische Konfliktauflösung (wenn sich der Zustand zwischen GET und POST ändert, schlägt es weiterhin fehl, was das korrekte Verhalten bei echten Konflikten ist).

## Rollen und Berechtigungen

Keine Änderungen an den Rechten notwendig. Der API-Token benötigt weiterhin Lese- und Schreibrechte auf Projekte und Tasks.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Bestehende Implementierung von `update_project`, `update_task` und `move_task_to_project`.
- `tests/test_server.py` - Aufbau der Mocks.

### Relevante Dokumentation

- PRD v005 - Abschnitt 6 (MVP) und 14 (Risiken).

## Codebase Intelligence

### Projektstruktur und Architektur

Die Tools verwenden `_request("GET", ...)` und `_request("POST", ..., json=payload)`. Wir fügen vor den `POST`-Requests einen synchronisierten `GET`-Request ein, um das `updated`-Feld zu besorgen.

### Patterns to Follow

In `move_task_to_project` wird bereits ein GET-Request durchgeführt, um den Status `done` zu bewahren:
```python
task = await _request("GET", f"/tasks/{task_id}")
is_done = task.get("done", False)
return await _request("POST", f"/tasks/{task_id}", json={"project_id": project_id, "done": is_done})
```
Dieses Pattern wird erweitert, um auch `updated` zu extrahieren.

### Anti-Patterns to Avoid

- Keine manuell hardcodierten `updated`-Zeitstempel.
- Keine Updates ohne vorherigen GET-Request, es sei denn, die API benötigt dort kein Optimistic Locking (z.B. Kommentare).

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Anpassung der Tools `update_project`, `update_task`, `set_reminders`, `complete_task`, `move_task_to_project`.
- `tests/test_server.py` - Aktualisierung der Tests, um die GET-Mocks zu integrieren.

## Implementation Plan

### Phase 1: Core Implementation (server.py)
1. `update_project` anpassen (GET-Request einbauen, `updated` mitschicken).
2. `update_task` anpassen (GET-Request einbauen, `updated` mitschicken).
3. `set_reminders` anpassen (GET-Request einbauen, `updated` mitschicken).
4. `complete_task` anpassen (GET-Request einbauen, `updated` mitschicken).
5. `move_task_to_project` anpassen (aus dem bestehenden GET-Request auch `updated` extrahieren und mitschicken).

### Phase 2: Testing and Validation (test_server.py)
1. Test-Mocks für alle modifizierten Tools so anpassen, dass sie auf den GET-Request reagieren und den POST-Request mit dem korrekten `updated`-Feld validieren.

## Step-by-Step Tasks

### Task 1: Projekt-Update anpassen
- **Status:** done  
- **Ziel:** `update_project` führt vorab GET aus und sendet `updated` mit.
- **Implementierung:** GET auf `/projects/{project_id}` durchführen. `payload["updated"] = project["updated"]` setzen (falls vorhanden).
- **Validierung:** Unit-Test `test_tool_update_project` in `tests/test_server.py` geschrieben und erfolgreich ausgeführt (8/8 tests passed).

### Task 2: Task-Update-Tools anpassen
- **Status:** done  
- **Ziel:** `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` führen vorab GET aus und senden `updated` mit.
- **Implementierung:** Jeweils GET auf `/tasks/{task_id}` durchführen und `payload["updated"] = task["updated"]` in den POST-Payload integrieren.
- **Validierung:** Unit-Tests für alle 4 Tools geschrieben und erfolgreich ausgeführt (10/10 passed).

### Task 3: Unit-Tests aktualisieren
- **Status:** done  
- **Ziel:** Alle Tests in `tests/test_server.py` laufen fehlerfrei durch und prüfen das Verhalten.
- **Implementierung:** Mocking der GET-Requests in allen betroffenen Testfunktionen ergänzt. Neue Tests für `update_task` und `set_reminders` hinzugefügt.
- **Validierung:** `uv run pytest` — 10/10 passed.

## Testing Strategy

### Unit / Integration Tests
- Jedes modifizierte Tool wird über einen Mock-Test abgedeckt, der verifiziert, dass:
  1. Zuerst ein GET-Request auf die korrekte ID erfolgt.
  2. Der POST-Request den empfangenen `updated`-Wert mitschickt.

## Validation Commands

```bash
uv run pytest
```

**Ergebnis:** 10 passed in 0.38s ✅

## Acceptance Criteria

- [x] Alle Modifikations-Tools (Projekte & Tasks) implementieren das Optimistic Locking Pattern.
- [x] Keine Regressionen in anderen Tools.
- [x] Alle pytest-Tests sind erfolgreich.
- [ ] Der 412-Fehler tritt bei Updates auf echten Instanzen nicht mehr auf. *(manuelle Validierung ausstehend)*

