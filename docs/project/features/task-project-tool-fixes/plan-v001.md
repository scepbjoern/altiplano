# Plan: Task- & Projekt-Tool-Fixes

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001
**Quelle:** User Request (Implementierungsplan "Fix: update_task Payload, Fehlende Felder in Projekt-Tools"), PRD v006  
**Confidence Score:** 8/10 (Projekt-Feld-Ergänzungen sind trivial und sicher; die Pflichtfeld-Annahme bei Task-Updates ist plausibel und durch das identische, bereits gelöste Problem bei `update_project` gut belegt, aber noch nicht gegen die echte Vikunja-Instanz validiert)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Bug Fix / Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py, Tests |
| Abhängigkeiten | Vikunja API `POST /tasks/{id}`, `PUT /projects`, `GET /tasks/{id}`, `GET /projects` |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan für Task- & Projekt-Tool-Fixes erstellt |

## Feature Description

Korrektur einer Payload-Lücke in vier Task-Update-Tools (`update_task`, `set_reminders`, `complete_task`, `move_task_to_project`), die das Pflichtfeld `title` nicht an Vikunja mitsenden, sowie Ergänzung fehlender Felder in den Projekt-Tools (`description`/`identifier` in `list_projects`, `hex_color`-Parameter in `create_project`). Beide Korrekturen schliessen Lücken, die bei der letzten Codeanalyse von `server.py` identifiziert wurden.

## User Story

```text
Als Personal User
möchte ich Aufgaben per Teil-Update (z.B. nur Beschreibung, Priorität oder Erinnerung ändern) zuverlässig aktualisieren können,
damit das Update nicht an einem von Vikunja verlangten, aber fehlenden Pflichtfeld (`title`) scheitert.

Als Nutzer
möchte ich in der Projektliste auch Beschreibung und Kennung sehen und beim Anlegen eines Projekts direkt eine Farbe vergeben können,
damit ich Projekte vollständig über die KI verwalten kann.
```

## Problem Statement

`update_task`, `set_reminders`, `complete_task` und `move_task_to_project` senden an `POST /tasks/{task_id}` nur die explizit geänderten Felder (plus den `updated`-Zeitstempel aus dem Optimistic-Locking-Feature). Vikunja verlangt vermutlich `title` als Pflichtfeld bei jedem Update — analog zum bereits bestätigten und gelösten Verhalten bei `POST /projects/{id}` in `update_project`. Ohne `title` im Payload schlägt ein reines Teil-Update (z.B. nur `description` ändern) voraussichtlich mit `2002 title: non zero value required` fehl.

Zusätzlich fehlen in den Projekt-Tools einige Felder: `list_projects` gibt `description` und `identifier` nicht zurück, und `create_project` bietet keinen Parameter zum Setzen der Projektfarbe (`hex_color`).

## Solution Statement

1. `update_task` wird auf das gleiche GET-Overlay-Pattern wie `update_project` umgestellt: vorab per `GET` den aktuellen Task laden, daraus einen vollständigen Basis-Payload (`title`, `description`, `done`, `priority`, `due_date`, `start_date`, `end_date`) bauen und die expliziten Änderungen darüberlegen.
2. `set_reminders`, `complete_task` und `move_task_to_project` ergänzen minimal `"title": task["title"]` aus der bereits vorhandenen GET-Antwort in ihren Payload (sie haben bereits ein GET für `updated`, müssen also keinen zusätzlichen Request machen).
3. `list_projects` ergänzt `description` und `identifier` in der zurückgegebenen Zusammenfassung.
4. `create_project` erhält einen neuen optionalen Parameter `hex_color`.

## Scope

### Im Scope

- Payload-Fix (`title` ergänzen) für `update_task`, `set_reminders`, `complete_task`, `move_task_to_project`.
- `list_projects`: `description` und `identifier` in der Rückgabe ergänzen.
- `create_project`: `hex_color`-Parameter ergänzen.
- Zugehörige Tests in `tests/test_server.py` anpassen bzw. neu erstellen.

### Nicht im Scope

- `update_project`: keine Codeänderung. Das Tool implementiert das GET-Overlay-Pattern bereits vollständig und gibt `identifier` bereits per Response-Passthrough zurück. Es erhält bewusst **keinen** `identifier`-Parameter (read-only Feld in Vikunja).
- `is_archived`-Handling in `update_project` (mögliches Folgerisiko, siehe PRD v006 Abschnitt 14 "Offene Frage") — separat zu prüfen, nicht Teil dieses Fixes.
- Manuelle Validierung gegen die echte Vikunja-Instanz, ob `title` tatsächlich als Pflichtfeld bei Task-Updates verlangt wird, ist Teil der Validierung dieses Plans, aber keine Vorbedingung für die Implementierung (die Korrektur ist auch ohne Bestätigung sicher und non-destruktiv).

## Rollen und Berechtigungen

Wird über den Vikunja-API-Token gesteuert. Der Token benötigt weiterhin Lese- und Schreibrechte für Projekte und Tasks. Keine Änderungen an Rollen/Berechtigungen.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Enthält `update_project` (Referenzmuster für das GET-Overlay-Pattern) sowie die vier betroffenen Task-Tools und die beiden Projekt-Tools.
- `tests/test_server.py` - Warum: Bestehende Mock-Patterns für GET-vor-POST-Sequenzen (`test_tool_update_project`, `test_tool_complete_task`, `test_tool_move_task_to_project`).
- `docs/project/features/optimistic-locking/plan-v001.md` - Warum: Hat das GET-vor-POST-Pattern für `updated` eingeführt, aber die `title`-Lücke bei Task-Tools offen gelassen.

### Relevante Dokumentation

- `docs/project/prds/vikunja-mcp-server-v006.md` - Abschnitt 6 (MVP), 8 (Kernfunktionen), 14 (Risiken: neuer Eintrag zu `title`-Pflichtfeld).

## Codebase Intelligence

### Projektstruktur und Architektur

`FastMCP`-Tools werden mit `@mcp.tool()` in `server.py` registriert. Alle Vikunja-API-Aufrufe laufen über die asynchrone `_request`-Funktion. `update_project` (server.py, Zeilen 131-170) implementiert bereits exakt das Muster, das auf `update_task` übertragen werden soll: erst `changes`-Dict aus den übergebenen Parametern bauen, dann per `GET` den aktuellen Zustand laden, daraus einen vollständigen Basis-Payload bauen, `updated` ergänzen, `changes` überlagern (`payload.update(changes)`), dann `POST`.

### Patterns to Follow

- Naming und Funktionssignaturen bleiben unverändert (keine Breaking Changes an bestehenden Parametern).
- GET-Overlay-Pattern aus `update_project` (server.py:131-170) 1:1 auf `update_task` übertragen.
- Bei `set_reminders`/`complete_task`/`move_task_to_project`: minimal-invasiv nur `title` ergänzen, da diese Tools bereits ein gezieltes GET für `updated` durchführen und kein voller Basis-Payload nötig ist (sie überschreiben ohnehin nur ihre eigenen, fixen Felder).
- Fehlerbehandlung: bestehendes `ValueError("No fields to update")` Verhalten in `update_task` unverändert beibehalten.

### Anti-Patterns to Avoid

- Keine Änderungen an `update_project` (bereits korrekt implementiert).
- Kein `identifier`-Parameter bei `create_project`/`update_project` (read-only Feld in Vikunja, siehe PRD v006 Abschnitt 6 "Out of Scope").
- Keine Full-Replacement-Payloads, die nicht über GET geladene, unbekannte Felder raten oder hart kodieren.

### Dependency Analysis

Keine neuen Dependencies erforderlich.

### Testing Patterns

`pytest` mit `unittest.mock.patch` auf `altiplano.server._request` (AsyncMock), teils mit `side_effect`-Funktion, um GET und POST unterschiedlich zu beantworten (siehe `test_tool_update_project`, `test_tool_complete_task`).

## Architekturentscheidungen

### Gewählter Ansatz

Für `update_task` wird das vollständige GET-Overlay-Pattern aus `update_project` übernommen (Konsistenz zwischen den beiden wichtigsten Update-Tools). Für `set_reminders`, `complete_task` und `move_task_to_project` reicht eine minimale Ergänzung um `title`, da diese Tools ohnehin nur fixe, eng begrenzte Payloads senden und kein generisches Teil-Update anbieten.

### Erwogene Alternativen

- Alternative: Auch bei `set_reminders`/`complete_task`/`move_task_to_project` den vollen Basis-Payload (alle Felder) senden, analog zu `update_task`. Entscheidung: nicht gewählt, da diese Tools bewusst nur einzelne, fixe Felder ändern sollen (Sicherheitsprinzip aus dem Task-Security-Tools-Feature) und ein voller Basis-Payload das Risiko unbeabsichtigter Seiteneffekte erhöhen würde, ohne einen zusätzlichen Nutzen zu bieten.

### Security, Performance, Maintainability

- Security: Die Änderungen ändern keine Berechtigungslogik. Das Prinzip "nur explizit gewünschte Felder ändern" bleibt erhalten, da unveränderte Felder aus dem GET-Response 1:1 zurückgespiegelt werden.
- Performance: Kein zusätzlicher API-Call, da alle betroffenen Tools bereits ein GET für `updated` durchführen (Optimistic Locking).
- Maintainability: Konsistentes Pattern zwischen `update_project` und `update_task` erleichtert künftige Wartung.

## Datenmodell und API-Mapping

- `update_task`: Payload-Basis `{"title": task["title"], "description": task.get("description", ""), "done": task.get("done", False), "priority": task.get("priority", 0), "due_date": task.get("due_date"), "start_date": task.get("start_date"), "end_date": task.get("end_date")}`, überlagert mit `changes` und `updated`.
- `set_reminders`: Payload `{"title": task["title"], "reminders": [...]}` + `updated`.
- `complete_task`: Payload `{"title": task["title"], "done": True}` + `updated`.
- `move_task_to_project`: Payload `{"title": task["title"], "project_id": project_id, "done": is_done}` + `updated`.
- `list_projects`: Rückgabe-Dict um `"identifier": p.get("identifier", "")` und `"description": p.get("description", "")` ergänzt.
- `create_project`: Payload um `"hex_color"` ergänzt, wenn übergeben.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - UPDATE: `update_task`, `set_reminders`, `complete_task`, `move_task_to_project`, `list_projects`, `create_project`.
- `tests/test_server.py` - UPDATE: `test_tool_update_task`, `test_tool_set_reminders`, `test_tool_complete_task`, `test_tool_complete_task_with_comment`, `test_tool_move_task_to_project`, `test_tool_list_projects`. ADD: `test_tool_create_project`.

### Neue Dateien

- Keine

## Implementation Plan

### Phase 1: Task-Tool-Payload-Fix
`update_task` auf das GET-Overlay-Pattern umstellen; `set_reminders`, `complete_task`, `move_task_to_project` um `title` ergänzen.

### Phase 2: Projekt-Tool-Feld-Ergänzungen
`list_projects` um `description`/`identifier` ergänzen; `create_project` um `hex_color`-Parameter ergänzen.

### Phase 3: Testing and Validation
Bestehende Tests anpassen, neuen Test für `create_project` ergänzen, `uv run pytest` ausführen, optional manuelle Validierung gegen die echte Vikunja-Instanz.

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Jeder Task ist atomic und einzeln validierbar.

### Task 1: UPDATE update_task — vollständiges GET-Overlay-Pattern

**Status:** planned  
**Ziel:** `update_task` sendet bei jedem Update ein vollständiges Pflichtfeld-Set (inkl. `title`), analog zu `update_project`.  
**IMPLEMENT:** In `src/altiplano/server.py` die Funktion `update_task` umbauen: explizite Parameter zunächst in ein `changes`-Dict sammeln (wie bisher), dann per `GET /tasks/{task_id}` den aktuellen Task laden und daraus einen Basis-`payload` bauen: `{"title": task["title"], "description": task.get("description", ""), "done": task.get("done", False), "priority": task.get("priority", 0), "due_date": task.get("due_date"), "start_date": task.get("start_date"), "end_date": task.get("end_date")}`. `updated` weiterhin bedingt ergänzen (`if "updated" in task`). Danach `payload.update(changes)` und mit diesem `payload` den `POST`-Request ausführen.  
**PATTERN:** `update_project` in `server.py` (Zeilen 131-170) — identische Struktur (changes sammeln, GET, Basis-Payload bauen, overlay, POST).  
**GOTCHA:** Der bestehende `ValueError("No fields to update")`-Check muss weiterhin auf dem `changes`-Dict (vor dem GET) erfolgen, nicht auf dem finalen `payload`.  
**ACCEPTANCE CRITERIA:**

- [ ] `update_task` baut den Payload aus dem GET-Response plus überlagerten `changes`.
- [ ] Ein Aufruf mit nur `description` (ohne `title`) sendet trotzdem `title` im POST-Payload.
- [ ] `ValueError` bei leeren `changes` bleibt erhalten.

**VALIDATE:**

- `uv run pytest` (nach Anpassung des zugehörigen Tests in Task 4)

### Task 2: UPDATE set_reminders, complete_task, move_task_to_project — title ergänzen

**Status:** planned  
**Ziel:** Alle drei Tools senden `title` aus der bereits vorhandenen GET-Antwort im Payload mit.  
**IMPLEMENT:** In `src/altiplano/server.py`:
- `set_reminders`: Payload-Dict um `"title": task["title"]` ergänzen (Reihenfolge: `{"title": task["title"], "reminders": [...]}`).
- `complete_task`: Payload-Dict um `"title": task["title"]` ergänzen (`{"title": task["title"], "done": True}`).
- `move_task_to_project`: Payload-Dict um `"title": task["title"]` ergänzen (`{"title": task["title"], "project_id": project_id, "done": is_done}`).

Alle drei Tools führen bereits ein `GET /tasks/{task_id}` aus (für `updated`/`is_done`) — kein zusätzlicher API-Call nötig.  
**PATTERN:** Bestehende GET-Aufrufe in denselben Funktionen.  
**GOTCHA:** `task["title"]` direkt verwenden (nicht `.get`), da `title` bei jedem existierenden Task vorhanden sein muss; ein fehlendes `title` im GET-Response wäre ein Datenintegritätsproblem, kein normaler Fall.  
**ACCEPTANCE CRITERIA:**

- [ ] `set_reminders`, `complete_task`, `move_task_to_project` senden `title` im POST-Payload.
- [ ] Bestehendes Verhalten (Erinnerungen setzen, Status, Projekt-Wechsel) bleibt unverändert.

**VALIDATE:**

- `uv run pytest` (nach Anpassung der zugehörigen Tests in Task 4)

### Task 3: UPDATE list_projects, create_project — fehlende Felder ergänzen

**Status:** planned  
**Ziel:** `list_projects` gibt `description`/`identifier` zurück; `create_project` kann `hex_color` setzen.  
**IMPLEMENT:** In `src/altiplano/server.py`:
- `list_projects`: Rückgabe-Dict um `"identifier": p.get("identifier", "")` und `"description": p.get("description", "")` ergänzen.
- `create_project`: neuen optionalen Parameter `hex_color: str | None = None` ergänzen; im Payload `if hex_color is not None: payload["hex_color"] = hex_color`. Docstring um einen Hinweis zur Farbvergabe ergänzen (analog zu `update_project`).

**PATTERN:** `update_project`-Parameterbehandlung für `hex_color` (Zeilen 136, 150-151).  
**GOTCHA:** Kein `identifier`-Parameter bei `create_project` ergänzen — das Feld ist read-only in Vikunja und wird bereits automatisch im Response zurückgegeben (kein explizites Mapping in `create_project` nötig, da reiner Passthrough).  
**ACCEPTANCE CRITERIA:**

- [ ] `list_projects` liefert `description` und `identifier` pro Projekt.
- [ ] `create_project` akzeptiert `hex_color` und sendet es im `PUT`-Payload, wenn gesetzt.
- [ ] `create_project` bleibt ohne `hex_color` funktionsfähig (Parameter optional).

**VALIDATE:**

- `uv run pytest` (nach Anpassung/Ergänzung der zugehörigen Tests in Task 4)

### Task 4: UPDATE tests/test_server.py

**Status:** planned  
**Ziel:** Alle Änderungen aus Task 1-3 sind durch Tests abgedeckt; alle bestehenden Tests laufen weiterhin grün.  
**IMPLEMENT:**
- `test_tool_update_task`: GET-Mock um `description`, `done`, `priority` ergänzen; POST-Assertion prüft vollständigen Basis-Payload mit überlagertem `title`. Einen zweiten Testfall ergänzen, der nur `description` übergibt und prüft, dass `title` trotzdem im POST-Payload enthalten ist.
- `test_tool_set_reminders`: GET-Mock um `title` ergänzen; POST-Assertion erwartet `title` im Payload.
- `test_tool_complete_task` und `test_tool_complete_task_with_comment`: GET-Mock um `title` ergänzen; POST-Assertion erwartet `title` im Payload.
- `test_tool_move_task_to_project`: GET-Mock um `title` ergänzen; POST-Assertion erwartet `title` im Payload.
- `test_tool_list_projects`: Mock-Response um `description`/`identifier` ergänzen; Assertion erwartet beide Felder in der Rückgabe.
- Neuer Test `test_tool_create_project`: Mock für `PUT /projects`, ruft `create_project` mit `hex_color="00ff00"` auf und prüft, dass `hex_color` im gesendeten Payload enthalten ist.

**PATTERN:** `test_tool_update_project` (Mocking mit `side_effect`-Funktion für GET/POST), `test_tool_complete_task` (bestehende Struktur).  
**IMPORTS:** Keine neuen.  
**GOTCHA:** Bei `test_tool_update_task` muss der GET-Mock-Task alle Felder enthalten, die der neue Basis-Payload erwartet (`title`, `description`, `done`, `priority`), sonst schlagen die Assertions fehl.  
**ACCEPTANCE CRITERIA:**

- [ ] Alle bestehenden Tests laufen weiterhin erfolgreich.
- [ ] Neue/angepasste Tests decken den `title`-Payload-Fix für alle vier Task-Tools ab.
- [ ] Neuer Test deckt `hex_color` in `create_project` ab.
- [ ] `test_tool_list_projects` deckt `description`/`identifier` ab.

**VALIDATE:**

- `uv run pytest`

## Testing Strategy

### Unit / Integration Tests

- Für jedes der vier Task-Tools: Verifikation, dass `title` im POST-Payload enthalten ist, auch wenn `title` nicht explizit als Parameter übergeben wurde.
- Für `update_task`: zusätzlicher Testfall mit Teil-Update ohne `title` (z.B. nur `priority`), der den vollständigen Basis-Payload prüft.
- Für `list_projects`: Prüfung, dass `description`/`identifier` aus dem Vikunja-Response übernommen werden.
- Für `create_project`: Prüfung, dass `hex_color` im `PUT`-Payload landet, wenn übergeben, und fehlt, wenn nicht übergeben.

### Regression Tests

- `test_mcp_initialization` prüft weiterhin, dass alle Tools (inkl. `create_project`) registriert sind — keine Änderung an der Tool-Liste nötig, da `create_project` bereits existiert.

### Edge Cases

- `update_task` ohne jegliche Parameter (ausser `task_id`) muss weiterhin `ValueError("No fields to update")` werfen, bevor ein GET-Request erfolgt.
- Task ohne `due_date`/`start_date`/`end_date` im GET-Response: `task.get(...)` liefert `None`, was im POST-Payload als `null` gesendet wird — das entspricht "kein Datum gesetzt" und überschreibt nichts Unbeabsichtigtes.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. Server starten via `npx @modelcontextprotocol/inspector uv run altiplano`.
2. `update_task` mit einer echten Task-ID und ausschliesslich `{"description": "Testbeschreibung"}` aufrufen — Erwartung: kein `2002`-Fehler, Beschreibung wird aktualisiert, Titel bleibt unverändert. Dies validiert die zentrale Annahme aus PRD v006 Abschnitt 14.
3. `list_projects` aufrufen und prüfen, ob `description`/`identifier` in der Antwort enthalten sind.
4. `create_project` mit `hex_color="00ff00"` aufrufen und in der Vikunja-UI prüfen, ob die Farbe gesetzt wurde.

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen
- [ ] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [ ] Relevante pytest-Tests sind ergänzt und grün
- [ ] Relevante manuelle Flows sind validiert (insb. Teil-Update ohne `title` gegen echte Instanz)
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

Nach Abschluss sollen `user-guide.md` und `developer-notes.md` im Feature-Ordner `docs/project/features/task-project-tool-fixes/` ergänzt werden (via `/document`). Inhaltlich relevant: Hinweis, dass Task-Update-Tools jetzt immer vollständige Pflichtfelder senden, und dass `list_projects`/`create_project` um `description`/`identifier`/`hex_color` erweitert wurden.

## Notes and Trade-offs

- Die zentrale Annahme (Vikunja verlangt `title` bei jedem Task-Update) ist nicht zu 100% bestätigt, aber durch die Analogie zum identischen, bereits bestätigten Verhalten bei Projekten gut begründet. Die Korrektur ist in jedem Fall sicher: Wird `title` von Vikunja gar nicht zwingend verlangt, ändert das Mitsenden des unveränderten aktuellen Titels nichts am Ergebnis.
- Bewusst keine Vereinheitlichung auf ein generisches "Payload aus GET + Overlay"-Helper-Pattern in dieser Iteration, um den Diff klein und die bestehenden, einfachen Tool-Implementierungen lesbar zu halten. Bei weiteren ähnlichen Fixes künftig eine gemeinsame Hilfsfunktion erwägen.
- `is_archived` in `update_project` wird in diesem Plan bewusst nicht angefasst (siehe PRD v006 Abschnitt 14, "Offene Frage").

## Offene Fragen

- Sendet Vikunja `2002 title: non zero value required` tatsächlich auch bei Task-Updates (nicht nur bei Projekten)? Validierung erfolgt in Task 4 / Level-2-Manual-Validation gegen die echte Instanz.
- Soll künftig ein gemeinsamer Helper (`_overlay_payload` o.ä.) für das GET-Overlay-Pattern eingeführt werden, um Duplikation zwischen `update_project` und `update_task` zu reduzieren? Nicht Teil dieses Plans, ggf. als eigenständiges Refactoring-Feature vorschlagen.

## Plan Review Notes

(Wird später durch den Review ergänzt.)
