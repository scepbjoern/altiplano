# Plan: Project Identifier

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-29  
**Plan-Version:** v001
**Quelle:** `docs/project/prds/vikunja-mcp-server-v010.md`  
**Confidence Score:** 10/10 (Das Hinzufügen eines optionalen Parameters und die Mitführung in Payloads ist ein etabliertes Pattern, das bereits für `hex_color` erfolgreich angewendet wurde.)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py / Tests |
| Abhängigkeiten | Vikunja API `identifier` Feldverhalten |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-29 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Der MCP-Server soll das Feld `identifier` bei Vikunja-Projekten vollständig unterstützen. Dadurch können Nutzer beim Erstellen oder Aktualisieren eines Projekts einen spezifischen, sprechenden Identifier (z.B. `SHOP`) vergeben oder ihn wieder leeren. Dies führt dazu, dass neue Tasks dieses Projekts leicht identifizierbare Task-IDs wie `SHOP-12` erhalten.

## User Story

```text
Als Nutzer
möchte ich beim Erstellen oder Aktualisieren eines Projekts einen Project Identifier setzen können,
damit Tasks sprechende Task-IDs erhalten.
```

## Problem Statement

Aktuell gibt `list_projects` zwar das `identifier`-Feld zurück, es lässt sich jedoch weder in `create_project` noch in `update_project` über den MCP-Server setzen oder ändern. Dadurch bleibt das Potenzial von sprechenden Task-IDs in Vikunja ungenutzt, wenn man Projekte via LLM-Agenten managt.

## Solution Statement

Die Tools `create_project` und `update_project` werden in `server.py` um das optionale Argument `identifier` erweitert. Das Argument wird in den API-Payload integriert. In `update_project` wird sichergestellt, dass bei einem partiellen Update (z.B. nur Farbe ändern) der bestehende Identifier aus der API mitgelesen und im vollständigen POST-Payload erhalten bleibt, sodass keine unerwünschten Überschreibungen stattfinden.

## Scope

### Im Scope

- Ergänzen des Arguments `identifier` in `create_project`.
- Ergänzen des Arguments `identifier` in `update_project`.
- Erhaltung des aktuellen `identifier`-Werts in `update_project` (bei Updates von anderen Feldern).
- Validierung über `pytest` Mocks.

### Nicht im Scope

- Implementierung eigener clientseitiger Validierungsregeln (z.B. Regex für Identifier), da diese Logik an die Vikunja-API delegiert wird, um doppelte Validierungen zu vermeiden.
- Umwandlung bestehender Task-IDs, da Vikunja das intern handhabt.

## Rollen und Berechtigungen

Keine Änderung; Standard-Berechtigungen gemäss Vikunja-API-Token.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Enthält `create_project` und `update_project`.
- `tests/test_server.py` - Warum: Enthält `test_tool_create_project` und `test_tool_update_project`, die erweitert werden müssen.

## Codebase Intelligence

### Projektstruktur und Architektur

Alle Modifikationen beschränken sich auf die Tool-Definitionen in `server.py` und das Test-File `test_server.py`.

### Patterns to Follow

- **Optionale Argumente:** `identifier: str | None = None`
- **Payload-Overlay in update_project:** Der alte Wert wird via `project.get("identifier", "")` ausgelesen und in das Payload-Base-Dictionary geschrieben, analog zu `hex_color` oder `description`.

### Anti-Patterns to Avoid

- Keine eigene komplexe Regex-Validierung für den Identifier; Fehlermeldungen der Vikunja-API werden direkt zurückgeworfen (bereits durch `_request` implementiert).

### Dependency Analysis

Keine neuen Abhängigkeiten erforderlich.

### Testing Patterns

Die bestehenden Tests `test_tool_create_project` und `test_tool_update_project` in `test_server.py` arbeiten mit `@patch` für `_request`. Wir erweitern diese Mocks oder erstellen Varianten davon, die die Übergabe und Erhaltung des `identifier` prüfen.

## Architekturentscheidungen

### Gewählter Ansatz

Erweiterung der bestehenden Argumentlisten um `identifier`. Dies ist abwärtskompatibel, da es als `str | None` typisiert wird und bei Nicht-Angabe das bisherige Verhalten intakt bleibt.

### Erwogene Alternativen

- Alternative: Ein dediziertes Tool `set_project_identifier`. - Entscheidung: Abgelehnt, da es Vikunja-Konvention ist, Projekt-Details gemeinsam über `PUT /projects` bzw. `POST /projects/{id}` zu setzen.

### Security, Performance, Maintainability

- **Maintainability:** Das Schema der Tools bleibt konsistent mit den Vikunja-API-Ressourcen.

## Datenmodell und API-Mapping

- Das JSON-Payload für `PUT /projects` und `POST /projects/{id}` bekommt optional das Feld `"identifier"`.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - UPDATE: Erweitern der Funktionen `create_project` und `update_project`.
- `tests/test_server.py` - UPDATE: Erweitern der Tests `test_tool_create_project` und `test_tool_update_project` sowie ggf. Hinzufügen spezifischer Testfälle.

### Neue Dateien

- Keine.

## Implementation Plan

### Phase 1: Core Implementation
Anpassung von `create_project` und `update_project` in `server.py`.

### Phase 2: Testing and Validation
Erweitern der zugehörigen Unit-Tests in `test_server.py`.

## Step-by-Step Tasks

### Task 1: UPDATE server.py: create_project

**Status:** planned  
**Ziel:** `create_project` unterstützt das Feld `identifier`.  
**IMPLEMENT:** 
- Füge `identifier: str | None = None` als Parameter hinzu.
- Ergänze den Docstring um "Use `identifier` to set a custom project identifier (e.g. 'SHOP').".
- Wenn `identifier is not None`, setze `payload["identifier"] = identifier`.  
**PATTERN:** Identisch zur Implementierung von `hex_color`.  
**GOTCHA:** None.  
**ACCEPTANCE CRITERIA:**
- [ ] `create_project` nimmt `identifier` entgegen und reicht es im Payload an `_request` weiter.

**VALIDATE:**
- Wird durch Task 3 getestet.

### Task 2: UPDATE server.py: update_project

**Status:** planned  
**Ziel:** `update_project` unterstützt das Feld `identifier` und erhält bestehende Werte.  
**IMPLEMENT:** 
- Füge `identifier: str | None = None` als Parameter hinzu.
- Ergänze den Docstring.
- Bei der Bildung von `changes` füge `changes["identifier"] = identifier` hinzu, wenn nicht `None`.
- Beim Auslesen des bestehenden Projekts füge `"identifier": project.get("identifier", "")` in das Base-Payload ein, damit ein gesetzter Identifier bei Updates von anderen Feldern (z.B. title) nicht versehentlich geleert wird, da Vikunja einen kompletten Payload erwartet.  
**PATTERN:** Identisch zur Implementierung von `hex_color`.  
**GOTCHA:** Vikunja erwartet beim POST für Updates ggf. das `identifier` Feld. Der Default sollte `""` sein, wenn es bisher nicht existierte.  
**ACCEPTANCE CRITERIA:**
- [ ] `update_project` sendet `identifier` im Changes-Dictionary.
- [ ] Nicht geänderte Identifier werden im Payload beibehalten.

**VALIDATE:**
- Wird durch Task 4 getestet.

### Task 3: UPDATE test_server.py: test_tool_create_project

**Status:** planned  
**Ziel:** Test prüft, ob `identifier` in `create_project` korrekt übertragen wird.  
**IMPLEMENT:** 
- Erweitere den bestehenden Test `test_tool_create_project` oder erstelle einen neuen Test `test_tool_create_project_with_identifier`.
- Prüfe, ob der mock für `PUT /projects` mit `"identifier": "SHOP"` aufgerufen wird.  
**PATTERN:** `test_tool_create_project`  
**ACCEPTANCE CRITERIA:**
- [ ] Test für `create_project` mit `identifier` ist grün.

**VALIDATE:**
- `uv run pytest tests/test_server.py`

### Task 4: UPDATE test_server.py: test_tool_update_project

**Status:** planned  
**Ziel:** Test prüft `identifier`-Updates und die Erhaltung nicht geänderter Identifier.  
**IMPLEMENT:** 
- Erweitere `test_tool_update_project` und überprüfe, dass ein bestehender `identifier` beim Updaten anderer Felder erhalten bleibt.
- Erstelle eventuell einen neuen Test `test_tool_update_project_identifier`, um die Änderung des Identifiers explizit zu testen, inklusive dem Leeren des Identifiers (`identifier=""`).  
**PATTERN:** `test_tool_update_project`  
**ACCEPTANCE CRITERIA:**
- [ ] Test für Erhaltung des Identifiers ist grün.
- [ ] Test für Ändern/Leeren des Identifiers ist grün.

**VALIDATE:**
- `uv run pytest tests/test_server.py`

## Testing Strategy

### Unit / Integration Tests

- API-Request Mocks in `test_server.py` validieren die gesendeten JSON-Payloads.

### Regression Tests

- Bestehende Tests für `create_project` und `update_project` ohne das neue Argument prüfen sicherstellen, dass die Rückwärtskompatibilität gewahrt ist.

### Edge Cases

- **Identifier leeren:** Muss durch die Übergabe eines leeren Strings `""` an `update_project` möglich sein. (Der Parameter `identifier` ist dann nicht `None`, sondern `""`, wird ins `changes`-Dict übernommen und überschreibt den Wert).

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen.
- [ ] Typvalidierung und API-Fehlerbehandlung sind korrekt (wird durch bestehendes `_request` Pattern abgedeckt).
- [ ] Relevante pytest-Tests sind ergänzt und grün.
- [ ] Keine bekannten Regressionen in bestehenden Kernworkflows.

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] Alle relevanten Tests laufen erfolgreich oder Ausnahmen sind begründet
- [ ] Manuelle Prüfung (MCP Inspector / Claude Desktop) ist dokumentiert
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt
- [ ] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Das neue Feature muss in der Entwickler- und Benutzerdokumentation erwähnt werden (Update der Tool-Beschreibungen im `README.md` und in allfälligen User Guides).

## Notes and Trade-offs

Keine wesentlichen Trade-offs.

## Offene Fragen

- Keine.

## Plan Review Notes

Nicht relevant.
