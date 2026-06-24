---
name: adapt-to-project
description: >
  Bereinigt den Starter-Kit-Workspace einmalig auf Basis des bestätigten PRDs: entfernt nicht benötigte MCP-Tools aus server.py und validiert die Tests. Vor dem ersten plan-feature ausführen. ONLY activate when the user explicitly runs /adapt-to-project or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  piv-phase: setup
  version: "2.0"
disable-model-invocation: true
argument-hint: "[path-to-prd]"
---

# Adapt to Project: Starter Kit bereinigen

## Input

Pfad zum bestätigten PRD: `$ARGUMENTS`

Beispiel:

```text
/adapt-to-project docs/project/prds/antragssystem-v002.md
```

## Zweck

Der Starter-Kit enthält standardmäßig eine Reihe von vordefinierten MCP-Tools für die Vikunja-API (Projekte, Tasks, Labels, Comments, Assignees). Wenn euer konkretes System nur einen Teil davon benötigt, bereinigt dieser Skill den Workspace gezielt auf Basis des PRDs und entfernt ungenutzte Tools, um eine saubere, minimale Codebasis zu hinterlassen.

Dieser Skill läuft **genau einmal pro Projekt**, nach PRD-Review, Review-Integration, fachlicher PRD-Bestätigung und vor dem ersten `/plan-feature`.

## Grundregeln

- Lösche keine Infrastruktur-Dateien (z.B. `__init__.py`, `server.py` Konfigurationslogik).
- **Entferne oder kommentiere aus** ungenutzte `@mcp.tool()` Definitionen in `src/altiplano/server.py`.
- Lösche oder aktualisiere die zugehörigen Tests in `tests/`, damit sie nicht fehlschlagen.
- Die Tests (`uv run pytest`) müssen nach der Bereinigung **zwingend** erfolgreich sein. Repariere alle Fehler selbst, bevor du abschliesst.

## Phase 1: PRD und Starter-Kit-Inventar lesen

Lies vollständig:

- Die PRD-Datei aus `$ARGUMENTS`
- `src/altiplano/server.py`
- `tests/` – vorhandene Tests

Suche im PRD nach dem Abschnitt **"Starter Kit Nutzung"** oder der Liste der benötigten Tools:

- **Abschnitt vorhanden:** Nutze die dort dokumentierten Tools als Grundlage für den Bereinigungsvorschlag.
- **Abschnitt fehlt:** Leite die Informationen selbst aus dem PRD ab und bestimme, welche MCP-Tools benötigt werden und welche irrelevant sind.

## Phase 2: Bereinigungsvorschlag erstellen

Erstelle eine Vorschlagsliste mit folgenden Kategorien:

### A) Ungenutzte MCP-Tools → aus server.py entfernen
Für jedes Tool in `src/altiplano/server.py` (z.B. `set_reminders`, `list_labels`), das laut PRD nicht benötigt wird:
- Schlage das Löschen oder Auskommentieren der Funktion inklusive `@mcp.tool()`-Dekoration vor.

### B) Ungenutzte Tests → aus tests/ entfernen
- Schlage das Löschen oder Auskommentieren von Tests in `tests/` vor, die gelöschte Tools testen.

### C) Nicht angetastet
Liste explizit auf, was erhalten bleibt (Infrastruktur, Konfiguration, genutzte Tools).

## Phase 3: Bestätigung einholen

Zeige den Bereinigungsvorschlag übersichtlich an und warte auf Bestätigung des Nutzers.

```text
Bereinigungsvorschlag für [Projektname] auf Basis von [PRD-Datei]:

A) MCP-Tools löschen: ...
B) Tests löschen/anpassen: ...
C) Nicht angetastet: ...

Soll ich diese Bereinigung so durchführen?
```

## Phase 4: Bereinigung durchführen

Nach Bestätigung:
1. **`src/altiplano/server.py`:** Ungenutzte Tools entfernen.
2. **`tests/`:** Ungenutzte Tests entfernen.
3. **Validierung:** Führe `uv run pytest` aus, um sicherzustellen, dass die verbleibenden Tests grün sind.

## Phase 5: Test-Validierung

Führe aus:

```bash
uv run pytest
```

Wenn Tests fehlschlagen, repariere die Mocks, Imports oder Testaufrufe selbst.

## Abschluss

Nach erfolgreichen Tests:
1. Zusammenfassung der durchgeführten Bereinigung ausgeben.
2. Liste der veränderten Dateien ausgeben.
3. Hinweis auf den nächsten Schritt:

```text
Nächster Schritt: Neue Agent-Session starten, /prime ausführen und mit /plan-feature das erste Feature aus dem PRD planen.
```

