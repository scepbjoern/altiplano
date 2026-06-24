# Plan: List Projects Hex Color

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001
**Quelle:** docs/project/prds/vikunja-mcp-server-v004.md (Kapitel 6 & 15)  
**Confidence Score:** 10/10 (Es ist eine sehr kleine Erweiterung des bestehenden Tools, Tests sind bereits vorbereitet).

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py, Tests |
| Abhängigkeiten | Vikunja API liefert bereits `hex_color` im Project Object. |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Das `list_projects` Tool soll um das Attribut `hex_color` in der Ausgabe ergänzt werden. Dies wurde im Rahmen des MVP-Scopes in PRD v004 definiert (US-1). Dadurch kann die KI Projekte mit ihren zugewiesenen Farben auslesen und dem Nutzer kontextbezogen anzeigen oder später via `update_project` gezielt anpassen.

## User Story

```text
Als Personal User
möchte ich eine Liste meiner Projekte inkl. Farbe sehen,
damit ich den Überblick behalte und Farben via KI anpassen kann.
```

## Problem Statement

Aktuell gibt `list_projects` zwar Verschachtelung (`parent_project_id`) und Status (`is_archived`) zurück, die Farbe (`hex_color`) fehlt jedoch. Damit fehlen der KI Metadaten, um Projekte eindeutig visuell zu identifizieren oder Farbanpassungen vorzuschlagen.

## Solution Statement

Wir ergänzen das Dictionary-Mapping in der Return-Liste der `list_projects` Methode in `src/altiplano/server.py` um das Feld `"hex_color": p.get("hex_color", "")`. Parallel wird der bestehende Test in `tests/test_server.py` angepasst, um sicherzustellen, dass die Farbe korrekt durchgereicht wird.

## Scope

### Im Scope

- Ergänzen des Feldes `hex_color` im Return von `list_projects`.
- Aktualisieren der entsprechenden pytest Unit-Tests.

### Nicht im Scope

- Anpassungen anderer Tools.
- Hinzufügen weiterer Felder, die nicht im PRD v004 für MVP definiert sind.

## Rollen und Berechtigungen

Keine besonderen neuen Berechtigungen notwendig. Es handelt sich um ein bereits vorhandenes Lese-Tool.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Enthält `list_projects` Tool.
- `tests/test_server.py` - Warum: Enthält `test_tool_list_projects`.

### Relevante Dokumentation

- `docs/project/prds/vikunja-mcp-server-v004.md` - Warum: Definition von US-1 und Feature-Kandidaten.

## Codebase Intelligence

### Projektstruktur und Architektur

Bestehende Struktur mit `server.py` als MCP Endpoint und `tests/test_server.py` für API Mocks wird beibehalten.

### Patterns to Follow

- Naming: `hex_color`
- Fehlerbehandlung: Keine Änderung an der Fehlerbehandlung (Nutzung von `.get("hex_color", "")` für sicheres Auslesen).
- FastMCP: Keine Änderungen an Tool-Argumenten oder Docstrings notwendig.

### Anti-Patterns to Avoid

- Keine umfangreichen Refactorings des `list_projects` Tools.

### Dependency Analysis

Keine neuen Dependencies.

### Testing Patterns

Der bestehende Mock in `test_server.py` für `list_projects` nutzt `mock_request.return_value`. Wir ergänzen lediglich `hex_color` in den Mock-Daten und in der erwarteten Return-Liste.

## Architekturentscheidungen

### Gewählter Ansatz

Erweiterung des Dict-Comprehensions in `list_projects` in `src/altiplano/server.py` um `hex_color`.

### Security, Performance, Maintainability

- Security: Keine Änderung.
- Performance: Keine Änderung, da `hex_color` bereits von Vikunja in der Projekt-Liste mitgesendet wird.
- Maintainability: Einfache, transparente Ergänzung, die gut getestet ist.

## Datenmodell und API-Mapping

Vikunja API Project Objekt enthält `hex_color`. Dieses wird 1:1 an das MCP Output Dictionary durchgereicht. Falls es fehlt (obwohl in Vikunja üblich), wird ein leerer String oder der Default-Wert zurückgegeben. Da Vikunja Farben meist in Hex (`ff0000`) ohne `#` liefert, ist `.get("hex_color", "")` ein sicheres Mapping.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Ergänzung von `hex_color` im `list_projects` Output.
- `tests/test_server.py` - Ergänzung von `hex_color` im Mock und Assert.

### Neue Dateien

- Keine.

## Implementation Plan

### Phase 1: Foundation

Entfällt, da Infrastruktur besteht.

### Phase 2: Core Implementation

Anpassung des `list_projects` Tool-Returns in `server.py`.

### Phase 3: Integration and Mappings

Entfällt, ist Teil von Phase 2.

### Phase 4: Testing and Validation

Anpassung von `tests/test_server.py` und Ausführung von `pytest`.

## Step-by-Step Tasks

### Task 1: UPDATE src/altiplano/server.py

**Status:** planned  
**Ziel:** `hex_color` dem Return-Dictionary von `list_projects` hinzufügen.  
**IMPLEMENT:** In der List-Comprehension innerhalb von `list_projects` das Feld `"hex_color": p.get("hex_color", ""),` ergänzen.  
**PATTERN:** `.get("is_archived", False)` als Vorbild für sicheres Dictionary-Lesen.  
**IMPORTS:** Keine neuen Imports nötig.  
**GOTCHA:** Keine.  
**ACCEPTANCE CRITERIA:**

- [ ] Das Tool gibt das Feld `hex_color` zurück.

**VALIDATE:**

- `uv run pytest`

### Task 2: UPDATE tests/test_server.py

**Status:** planned  
**Ziel:** Den Test `test_tool_list_projects` an die neue Ausgabe anpassen.  
**IMPLEMENT:** Im Mock-Return für `mock_request` ein `"hex_color": "00ff00"` (oder ähnlich) ergänzen. Im abschließenden `assert result == [...]` ebenfalls das `hex_color` Feld erwarten.  
**PATTERN:** Bestehendes Mocking-Pattern aus `test_tool_list_projects`.  
**IMPORTS:** Keine.  
**GOTCHA:** Beide Dictionaries (Mock-Input und expected Output) müssen übereinstimmen.  
**ACCEPTANCE CRITERIA:**

- [ ] `test_server.py` beinhaltet `hex_color` in der Validierung für `list_projects`.

**VALIDATE:**

- `uv run pytest`

## Testing Strategy

### Unit / Integration Tests

Bestehender pytest-Lauf (`test_tool_list_projects`) wird erweitert.

### Regression Tests

Keine kritischen Regressionen zu erwarten.

### Edge Cases

- `hex_color` fehlt in der Vikunja-Antwort (wird durch `.get` abgefangen).

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. Server lokal starten: `uv run altiplano`
2. Mit einem MCP Inspector das Tool `list_projects` aufrufen.
3. Prüfen, ob im zurückgegebenen JSON das Feld `hex_color` für die Projekte vorhanden ist.

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

Nach der Implementierung sollte das `list_projects` Tool in etwaigen Beispielen mit dem neuen Feld `hex_color` erwähnt werden.

## Notes and Trade-offs

Die Implementation ist minimalinvasiv. Ein Default-Leerstring `""` ist sicher, falls die Farbe in der API wirklich fehlen sollte, da Vikunja teils keinen Farbwert zwingend verlangt.

## Offene Fragen

- Keine

## Plan Review Notes

(Wird später durch den Review ergänzt.)
