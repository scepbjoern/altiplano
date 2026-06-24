---
name: create-rules
description: >
  Creates or updates project instruction files by analyzing the stack, repository structure, conventions, and available PIV skills. Use it when the project rules need to be generated or refreshed. ONLY activate when the user explicitly runs /create-rules or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  version: "3.0"
disable-model-invocation: true
---

# Create Rules: Instructions Aktualisieren

## Ziel

Erstelle oder aktualisiere die projektspezifischen Instructions-Dateien für Agenten.

Zieldateien:

- `CLAUDE.md`
- `KILO_INSTRUCTIONS.md`
- `AGENTS.md`

## Analyse

Lies mindestens:

- `pyproject.toml`
- `src/altiplano/server.py`
- `KILO_INSTRUCTIONS.md`, falls vorhanden
- `CLAUDE.md`, falls vorhanden
- `AGENTS.md`, falls vorhanden
- `TASKS.md`
- verfügbare Skills unter `.agents/skills/`

Ermittle:

- Python- und Paket-Versionen (via pyproject.toml)
- Registrierte MCP-Tools und API-Anbindung (via server.py)
- Testbefehle und pytest-Struktur
- verbotene Technologien und Anti-Patterns
- PIV-Workflow und Skill-Aufrufe

## Ausgabeprinzipien

### `KILO_INSTRUCTIONS.md`

Diese Datei ist der ausführliche Coding-Guide. Sie soll enthalten:

- Tech Stack und Verbote
- Sprache, Stil und Python-Regeln (PEP 8, Typ-Annotationen)
- Projektstruktur
- MCP-Konventionen (Tools, API-Requests, Fehlerbehandlung, Secrets)
- Testing mit pytest
- PIV-Loop mit `TASKS.md` als Feature-Index, `docs/project/features/[feature-name]/plan-v001.md` als initialem Plan, Feature-Plan-Review, Review-Integration und `docs/project/features/[feature-name]/plan-vNNN.md` als versionierter Arbeitsgrundlage für `/execute`
- Versionierte PRD-Updates mit `/update-prd`
- Versionierte Feature-Plan-Updates mit `/update-feature-plan`
- Verfügbare PIV-Skills aus `.agents/skills/`
- Verdachtsbasierte Abschluss-Reflexion mit `/reflect-rules`
- Stop-and-ask-Regeln
- Commit-Konventionen

### `CLAUDE.md`

Diese Datei ist kompakt. Sie soll:

- auf `KILO_INSTRUCTIONS.md` als primäre Quelle verweisen
- den Stack kurz nennen (Python, uv, mcp)
- auf `.agents/skills/` hinweisen
- klarstellen, dass PIV-Skills nur auf expliziten Aufruf aktiviert werden

### `AGENTS.md`

Diese Datei beschreibt den allgemeinen Projektkontext. Sie soll:

- Projektbeschreibung, Scope, Datenmodell (Vikunja-Ressourcen) und Team-TODOs enthalten
- auf `KILO_INSTRUCTIONS.md` für Coding-Regeln verweisen
- keine detaillierten Workflow-Regeln duplizieren

## Skill-Referenzblock

Nutze diesen Block, wenn eine Instructions-Datei Skill-Referenzen braucht:

```markdown
## Verfügbare PIV-Skills

Skills liegen in `.agents/skills/`. Aufruf per `/skill-name` im Chat.
Nie automatisch aktivieren – immer nur auf expliziten Aufruf.

| Skill | Aufruf | PIV-Phase |
|---|---|---|
| prime | `/prime` | Session-Start: Projekt-Kontext laden |
| create-prd | `/create-prd [Dateiname]` | Setup/Plan: PRD-Entwurf als `v001` generieren |
| review-prd | `/review-prd [Pfad-zum-PRD]` | Setup/Plan: PRD in frischer Reviewer-Session kritisch prüfen |
| integrate-prd-review | `/integrate-prd-review [Pfad-zum-PRD] [Pfad-zum-Review]` | Setup/Plan: Review bewerten und integrieren |
| update-prd | `/update-prd [Pfad-zum-PRD]` | Setup/Plan: PRD versioniert aktualisieren |
| adapt-to-project | `/adapt-to-project [Pfad-zum-PRD]` | Setup: Code nach bestätigtem PRD bereinigen, Tests validieren |
| plan-feature | `/plan-feature [Feature]` | Plan: initialen Feature-Plan `plan-v001.md` erstellen |
| review-feature-plan | `/review-feature-plan [Pfad-zum-Plan]` | Plan: Feature-Plan in frischer Reviewer-Session prüfen |
| integrate-feature-plan-review | `/integrate-feature-plan-review [Pfad-zum-Plan] [Pfad-zum-Review]` | Plan: Review integrieren und neue Plan-Version erstellen |
| update-feature-plan | `/update-feature-plan [Pfad-zum-Plan]` | Plan: Feature-Plan versioniert aktualisieren |
| execute | `/execute [Pfad-zum-Plan]` | Implement: Task-by-Task umsetzen |
| document | `/document [Pfad-zum-Plan]` | Validate/Docs: Feature-Dokumentation erstellen |
| reflect-rules | `/reflect-rules [Pfad-zum-Plan]` | Validate/Retro: Agent-Regeln und Skills verbessern |
| commit | `/commit` | Commit: Konventionellen Commit erstellen |
| create-rules | `/create-rules` | Setup: Instructions-Dateien aktualisieren |
| init-project | `/init-project` | Setup: Projekt initialisieren |
```

## Regeln

- Keine tool-spezifischen Commands neu erzeugen.
- `.agents/skills/` ist die kanonische Skill-Quelle.
- Bestehende projektspezifische Inhalte erhalten, wenn sie nicht veraltet oder widersprüchlich sind.

## Output

Nach Aktualisierung:

- Geänderte Dateien auflisten
- Wichtigste inhaltliche Änderungen zusammenfassen
- Offene TODOs oder Annahmen nennen

