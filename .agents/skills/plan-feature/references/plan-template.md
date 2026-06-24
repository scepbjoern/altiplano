# Plan: <Feature-Name>

## Status

**Feature-Status:** planned  
**Erstellt:** YYYY-MM-DD  
**Plan-Version:** v001
**Quelle:** <User Request, PRD oder Datei>  
**Confidence Score:** <#/10 mit kurzer Begründung>

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability / Enhancement / Refactor / Bug Fix |
| Plan-Version | v001 |
| Komplexität | Low / Medium / High |
| Primär betroffene Systeme | fastmcp / httpx / server.py / Tests |
| Abhängigkeiten | <Libraries, ENV-Werte, Daten, Entscheidungen> |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | YYYY-MM-DD | Initiale Planung | Erster Feature-Plan erstellt |

Bei späteren Änderungen ergänzen `/integrate-feature-plan-review` oder `/update-feature-plan` neue Zeilen, ohne alte Einträge zu entfernen.

## Feature Description

<Detaillierte Beschreibung des Features, Zweck und Nutzen für Nutzer.>

## User Story

```text
Als <Rolle/Konsument>
möchte ich <Aktion/Ziel>,
damit <Nutzen/Wert>.
```

## Problem Statement

<Welches konkrete Problem oder welche Chance adressiert das Feature?>

## Solution Statement

<Wie löst der geplante Ansatz das Problem?>

## Scope

### Im Scope

- ...

### Nicht im Scope

- ...

## Rollen und Berechtigungen

<Betroffene Rollen oder Berechtigungsstufen (wird meist über den Vikunja-API-Token gesteuert).>

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: <konkreter Einstiegspunkt>
- `tests/test_server.py` - Warum: <ähnliches Testpattern>

### Relevante Dokumentation

- [Dokumentationstitel](https://example.com/docs#section) - Warum: <konkrete Relevanz>

## Codebase Intelligence

### Projektstruktur und Architektur

<Relevante Verzeichnisse, Hilfsfunktionen und bestehende Python-Patterns.>

### Patterns to Follow

- Naming: <konkrete Regel oder Python/PEP 8 Konvention>
- Fehlerbehandlung: <Exception-Handling bei API-Requests>
- FastMCP: <Tool-Registrierung, Docstrings für Tool-Beschreibungen>
- API-Anbindung: <Verwendung der `_request`-Helferfunktion>

### Anti-Patterns to Avoid

- Kein Node.js, Next.js, React, Prisma, Tailwind CSS, DaisyUI, LangChain.
- Keine Vitest- oder Playwright-Regeln.
- Keine parallele Architektur neben bestehenden `src/altiplano/` and `tests/` Patterns.

### Dependency Analysis

<Relevante Dependencies aus `pyproject.toml`. Keine neuen Packages ohne Begründung und Bestätigung.>

### Testing Patterns

<Bestehende pytest-Patterns, die gespiegelt werden sollen.>

## Architekturentscheidungen

### Gewählter Ansatz

<Beschreibung und Begründung.>

### Erwogene Alternativen

- Alternative: <Beschreibung> - Entscheidung: <warum nicht gewählt>

### Security, Performance, Maintainability

- Security: <Rollen, Inputvalidierung in den Tools>
- Performance: <Effiziente API-Filterung (server-seitig), Vermeidung von Multipacket-Anfragen>
- Maintainability: <Saubere Typschnittstellen, verständliche Tool-Docstrings>

## Datenmodell und API-Mapping

<Wie werden Vikunja-API-Shapes in MCP-Datenstrukturen übersetzt? Gibt es Mocks oder Fallbacks?>

## Betroffene Dateien

### Bestehende Dateien

- `pfad` - Aktion und Grund

### Neue Dateien

- `pfad` - Zweck und Grund

## Implementation Plan

### Phase 1: Foundation

<Typen, API-Request-Helfer, Hilfsfunktionen.>

### Phase 2: Core Implementation

<MCP Tool-Definitionen, API-Logik.>

### Phase 3: Integration and Mappings

<Anbindung an die Vikunja-API-Endpoints, Transformationen.>

### Phase 4: Testing and Validation

<pytest, manuelle Validierung via MCP Inspector.>

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Jeder Task ist atomic und einzeln validierbar.

Aktionskeywords:

- `CREATE`: neue Datei oder Funktion
- `UPDATE`: bestehende Datei/Funktion ändern
- `ADD`: Funktionalität ergänzen
- `REMOVE`: veralteten Code entfernen, nur mit expliziter Bestätigung
- `REFACTOR`: Struktur ändern ohne Verhalten zu ändern
- `MIRROR`: bestehendes Pattern bewusst spiegeln

### Task 1: <ACTION> <target_file_or_area>

**Status:** planned  
**Ziel:** <konkretes Ergebnis>  
**IMPLEMENT:** <präzise Umsetzung>  
**PATTERN:** <Datei/Zeilen/Pattern, das gespiegelt wird>  
**IMPORTS:** <notwendige Imports oder Dependencies>  
**GOTCHA:** <Fallstrick, Constraint oder Edge Case>  
**ACCEPTANCE CRITERIA:**

- [ ] <messbares Kriterium>
- [ ] <messbares Kriterium>

**VALIDATE:**

- `uv run pytest`
- Manuelle Prüfung: <konkrete Schritte (z.B. MCP Inspector Aufrufe)>

## Testing Strategy

### Unit / Integration Tests

<pytest-Tests für API-Requests, Mocking und Tool-Logik.>

### Regression Tests

<Bestehende pytest-Tests erweitern, wenn Kernverhalten stabil bleiben muss.>

### Edge Cases

- <Fehlerfall, ungültiger API-Token, falsche Parameter, Statuskonflikt>

## Validation Commands

Führe diese Befehle nur aus, wenn sie für das Feature relevant sind. Dokumentiere nicht ausführbare Schritte mit Begründung.

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

<Konkrete Schritte im MCP Inspector oder in Claude Desktop und erwartete Ergebnisse.>

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

<Welche Endanwender- und Entwicklerdokumentation soll der spätere `/document`-Skill erstellen?>

## Notes and Trade-offs

<Designentscheidungen, Trade-offs, offene Risiken, spätere Erweiterungen.>

## Offene Fragen

- Keine oder konkrete Fragen

## Plan Review Notes

<Wird durch `/integrate-feature-plan-review` in späteren Plan-Versionen ergänzt. Beim initialen `plan-v001.md`: Nicht relevant.>
