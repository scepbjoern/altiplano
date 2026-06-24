---
name: prime
description: >
  Loads the project context at the beginning of a session and summarizes the current architecture, stack, rules, tasks, and recent changes. Use this workflow before planning or implementation work when the agent needs a compact project briefing. ONLY activate when the user explicitly runs /prime or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  piv-phase: plan
  version: "2.0"
disable-model-invocation: true
---

# Prime: Projektkontext Laden

## Ziel

Baue zu Beginn einer Arbeitssession ein kompaktes, belastbares Bild des Repos auf. Schreibe keinen Code und ändere keine Dateien.

## Pflichtlektüre

Lies, falls vorhanden, diese Dateien in sinnvoller Reihenfolge:

- `CLAUDE.md` oder `KILO_INSTRUCTIONS.md`
- `AGENTS.md`
- `README.md`
- PRDs und Konzeptdateien unter `docs/`
- `TASKS.md`
- `pyproject.toml`
- `src/altiplano/server.py`
- `tests/` Teststruktur

## Git-Kontext

Ermittle zusätzlich:

- Letzte Änderungen mit `git log --oneline -10`
- Aktuellen Branch, Arbeitsbaumstatus und uncommitted changes mit `git status`

**Mehrpersonen-Erkennung:** Prüfe in `TASKS.md`, ob mehrere unterschiedliche Namen in der Spalte `Verantwortlich` oder mehrere unterschiedliche Feature-Branches eingetragen sind. Falls ja, ist dies ein kollaboratives Repository. Weise in diesem Fall im Output-Abschnitt „Kollaborationsstatus" aktiv und konkret darauf hin:
- ob der aktuelle lokale Stand vor Planung oder Umsetzung synchronisiert werden sollte (Pull von `main` oder dem gemeinsamen Branch)

## Analysefokus

Ermittle:

- Zweck des Projekts und digitalisierter Prozess / Integrations-Scope
- Tech Stack und nicht verhandelbare Konventionen
- Paketmanager, Build- und Testbefehle (uv, pytest)
- Registrierte MCP-Tools und Vikunja-API-Client-Struktur in `server.py`
- Teststrategie mit pytest
- Aktive und abgeschlossene Features laut `TASKS.md`
- Im Mehrpersonen-Fall: Verantwortliche Personen, Branches und mögliche parallele Arbeit laut `TASKS.md`
- Relevante TODOs, Risiken und offene Entscheidungen
- Sofortige Auffälligkeiten, Inkonsistenzen oder Risiken, die vor Planung oder Umsetzung bekannt sein sollten

## Output

Gib eine kompakte, gut scannbare Zusammenfassung mit diesen Abschnitten aus:

1. Projektübersicht
2. Struktur und wichtige Dateien (z.B. server.py, tests)
3. Tech Stack und Kernregeln
4. Aktueller Stand laut `TASKS.md`
5. Test- und Validierungsbefehle (uv, pytest, MCP Inspector)
6. Aktueller Branch, Arbeitsbaumstatus und letzte Änderungen aus Git
7. Auffälligkeiten, Risiken oder offene Entscheidungen
8. Kollaborationsstatus, falls `TASKS.md` Verantwortliche oder Branches enthält
9. Mögliche nächste Planning- oder Implementation-Tasks

Halte die Zusammenfassung kurz. Keine Dateien schreiben, keine Verzeichnisse erstellen, keine Commits ausführen.
