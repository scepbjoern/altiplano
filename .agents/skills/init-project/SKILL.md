---
name: init-project
description: >
  Guides a new team through initializing a project from altiplano, including dependencies, environment variables, and first tool checks. Use it when setting up a fresh project from this starter kit. ONLY activate when the user explicitly runs /init-project or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  version: "2.0"
disable-model-invocation: true
---

# Init Project: Starter-Kit Initialisieren

## Ziel

Richte ein neues Projekt auf Basis von `altiplano` ein. Dieser Workflow ist für lokale Entwicklung und Testen des MCP-Servers gedacht.

## Voraussetzungen Prüfen

Prüfe oder fordere den Nutzer auf zu prüfen:

- Python >= 3.10
- uv (moderner Python Paket- und Projektmanager)
- Git

## Setup-Schritte

### 1. Repository Klonen und Umbenennen

```bash
git clone [url] [neuer-projektname]
```

### 2. Ins Projektverzeichnis Wechseln

```bash
cd [neuer-projektname]
```

### 3. Dependencies und Virtual Environment synchronisieren

`uv` erstellt automatisch eine virtuelle Umgebung und installiert alle Abhängigkeiten aus `pyproject.toml` / `uv.lock`:

```bash
uv sync
```

### 4. Environment Einrichten

Erstelle eine `.env`-Datei oder eine Datei unter `~/.config/altiplano/env` mit den Vikunja-API-Daten:

```env
VIKUNJA_URL="https://todo.example.com/api/v1"
VIKUNJA_API_TOKEN="tk_..."
```

### 5. Server starten und testen

Testet den Server lokal mit dem MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run altiplano
```

### 6. Projektkontext Ausfüllen

Öffne `AGENTS.md` und fülle alle `[TODO]`-Felder aus:

- Projektbeschreibung
- Schnittstellen und Scope der Vikunja-Integration
- Scope (In/Out)
- Datenmodell
- Team

## Entwicklungsregeln nach Setup

- PRD-Änderungen nach fachlicher Klärung oder Dozentenfeedback mit `/update-prd` als neue PRD-Version dokumentieren und committen.
- Neue Features mit `/plan-feature` planen, `plan-v001.md` committen, in frischer Session mit `/review-feature-plan` prüfen, in der Autor-Session mit `/integrate-feature-plan-review` in eine neue Plan-Version überführen, bei späterem Änderungsbedarf `/update-feature-plan` nutzen, dann mit `/execute` umsetzen.
- Root-`TASKS.md` bleibt Feature-Index; Detailtasks liegen in `docs/project/features/[feature-name]/plan-vNNN.md`.
- Änderungen an `server.py` müssen immer durch pytest (`uv run pytest`) abgesichert werden.

## Output

Gib am Ende aus:

- Welche Setup-Schritte erledigt wurden
- Welche Schritte der Nutzer noch manuell ausführen muss (z.B. Konfiguration)
- Ob der MCP-Server erfolgreich getestet wurde
- Welche `[TODO]`-Felder in `AGENTS.md` noch offen sind

