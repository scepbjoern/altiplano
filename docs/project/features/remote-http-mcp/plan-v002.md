# Plan: Remote HTTP MCP

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v002
**Quelle:** User Request (`/plan-feature Remote HTTP MCP`) und Review Feedback  
**Confidence Score:** 9/10 (Konventionen aus bestehenden Projekten des Nutzers adaptiert, saubere Trennung von Code und Deployment-Setup)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v002 |
| Komplexität | Medium |
| Primär betroffene Systeme | server.py, pyproject.toml, Docker, Compose |
| Abhängigkeiten | uvicorn, starlette |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |
| v002 | 2026-06-25 | Review Feedback | Docker-Setup an bestehende Nutzer-Konventionen (`deploy/` Folder, Compose, `.env`, `UID/GID`) angepasst. |

## Feature Description

Der MCP Server wird um einen HTTP-Server (Server-Sent Events / SSE) erweitert, damit er als Remote-Endpunkt für netzwerkbasierte LLM-Clients (z.B. ChatGPT, Claude) erreichbar ist. 
Außerdem wird das Projekt um ein standardisiertes Deployment-Setup ergänzt, das sich an den bestehenden Host-Strukturen des Nutzers (wie bei Compact Diary) orientiert. Dazu gehört ein dediziertes `deploy/`-Verzeichnis mit `docker-compose.yml` und `.env.example`, sowie ein `Dockerfile` im Projekt-Root, welches als Non-Root User ausgeführt werden kann (`UID`/`GID` Argumente).

## User Story

```text
Als Nutzer netzwerkbasierter KI-Assistenten (z.B. ChatGPT)
möchte ich den Altiplano MCP-Server über einen HTTP(SSE)-Endpunkt erreichen und per Docker Compose einfach updaten können,
damit ich meine Aufgaben auch remote verwalten kann und die Server-Wartung meinen gewohnten Mustern folgt.
```

## Problem Statement

Bisher unterstützt der Server ausschließlich den `stdio`-Transport und muss lokal gestartet werden. Ein professionelles, standardisiertes Deployment-Setup (Docker, Compose) fehlt bisher vollständig, was die Einbindung auf bestehenden Hosts (mit Reverse Proxies) erschwert.

## Solution Statement

1. Hinzufügen von `uvicorn` und `starlette` in `pyproject.toml`.
2. Anpassung der `main()`-Funktion in `server.py` zur Unterstützung von `MCP_TRANSPORT="sse"`.
3. Erstellen eines sicheren, anpassbaren `Dockerfile` (Non-Root via `UID`/`GID`).
4. Erstellen einer typischen Deployment-Struktur unter `deploy/docker-compose.yml` und `deploy/.env.example`.

## Scope

### Im Scope
- Erweiterung von `server.py` für `transport="sse"`.
- Hinzufügen von `uvicorn` und `starlette` als Abhängigkeiten.
- Erstellung eines `Dockerfile` mit Non-Root-User Support.
- Setup von `deploy/docker-compose.yml` und `deploy/.env.example`.

### Nicht im Scope
- Eigene Authentifizierungslogik im Python-Code (erfolgt durch Reverse Proxy).
- Aufteilung in PROD und TEST (für dieses Tool reicht eine einzelne PROD-Umgebung völlig aus).
- Skripte wie `entrypoint.sh` (da der Server stateless ist und nicht auf eine Datenbank warten muss, reicht ein direkter Start).

## Rollen und Berechtigungen

- Keine Änderungen an Vikunja-Rollen. Der HTTP-Endpunkt wird durch einen externen Reverse Proxy / Cloudflare Access abgesichert.

## Context References

### Pflichtlektüre vor Umsetzung
- `src/altiplano/server.py` - Hier muss die Transport-Weiche implementiert werden.
- `___TEMP/docker-compose.demo.yml` (als Referenz für Compose-Patterns: `build.context: ..`, Env-Files, Network).

## Codebase Intelligence

### Projektstruktur und Architektur
- Die Python-Architektur (`server.py`) bleibt minimal.
- Neues Deployment-Pattern: `Dockerfile` liegt im Root, `docker-compose.yml` und `.env.example` liegen im Verzeichnis `deploy/`.

### Patterns to Follow
- Verwendung von `UID` und `GID` Build-Argumenten im `Dockerfile`, um den Container ohne unnötige Root-Rechte laufen zu lassen.
- Nutzung der `.env` Datei im `deploy/` Ordner für alle Container-Settings (wie `APP_PORT`, `VIKUNJA_URL`).

### Dependency Analysis
- `uvicorn` und `starlette` werden als reguläre Dependencies via `pyproject.toml` installiert.

## Architekturentscheidungen

### Gewählter Ansatz
Wir lesen `MCP_TRANSPORT` in der `main()` Methode aus und rufen bei "sse" `mcp.run(transport="sse")` auf. 
Für Docker definieren wir ein Slim/Alpine Python Image, richten mit übergebenen `UID`/`GID` einen Anwender ein, und kopieren den Code via `uv`. 
Die `docker-compose.yml` im `deploy/` Verzeichnis referenziert das Root-Verzeichnis als Build-Kontext (`context: ..`). 

## Betroffene Dateien

### Bestehende Dateien
- `pyproject.toml` - ADD: `uvicorn` und `starlette`.
- `src/altiplano/server.py` - UPDATE: `main()` Funktion umbauen.

### Neue Dateien
- `Dockerfile` - CREATE: Basis Image Definition, Non-Root-User.
- `deploy/docker-compose.yml` - CREATE: Compose Setup.
- `deploy/.env.example` - CREATE: Umgebungsvariablen Template.

## Step-by-Step Tasks

### Task 1: UPDATE pyproject.toml
**Status:** planned  
**Ziel:** Hinzufügen von `uvicorn` und `starlette` als Abhängigkeiten.  
**IMPLEMENT:** Ergänze `uvicorn>=0.30.0` und `starlette>=0.37.2` in der `dependencies`-Liste in `pyproject.toml`.  
**ACCEPTANCE CRITERIA:**
- [ ] `pyproject.toml` enthält `uvicorn` und `starlette`.

### Task 2: UPDATE server.py
**Status:** planned  
**Ziel:** `main()` so umbauen, dass `MCP_TRANSPORT` ("stdio" oder "sse") respektiert wird.  
**IMPLEMENT:** 
In `src/altiplano/server.py` die `main()`-Methode anpassen:
```python
def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        # Hier ist evtl. Anpassung nötig, um den FastMCP Server auf 0.0.0.0 zu binden,
        # falls FastMCP das unterstützt, oder das Image übernimmt das durch Uvicorn-Configs.
        mcp.run(transport="sse")
    else:
        mcp.run()
```
**ACCEPTANCE CRITERIA:**
- [ ] `server.py` wertet `MCP_TRANSPORT` aus.

### Task 3: CREATE Dockerfile
**Status:** planned  
**Ziel:** Ein robustes Dockerfile für den Einsatz als HTTP-Server erstellen.  
**IMPLEMENT:**
Schreibe ein standardmäßiges `Dockerfile` basierend auf einem leichten Python-Image (z.B. Alpine oder Debian Slim) zusammen mit `uv`.
- ARG `UID=1000` und `GID=1000`
- Erstelle entsprechenden Gruppe und Benutzer.
- Führe `uv sync` oder `uv pip install` für die Applikation durch.
- CMD: Starten der Applikation via `altiplano` CLI Kommando.
**ACCEPTANCE CRITERIA:**
- [ ] Dockerfile im Root-Verzeichnis vorhanden und läuft non-root.

### Task 4: CREATE Deploy Setup (docker-compose & .env.example)
**Status:** planned  
**Ziel:** Das standardisierte Deployment-Setup analog zu bestehenden Host-Strukturen erstellen.  
**IMPLEMENT:**
- Erstelle das Verzeichnis `deploy/`.
- Erstelle `deploy/docker-compose.yml` mit Service `app`, `build.context: ..`, Build-Args für `UID`/`GID`, Restart-Policy `unless-stopped` und Port-Mapping auf `${APP_PORT:-6274}:8000` (FastMCP SSE Default ist meist 8000).
- Erstelle `deploy/.env.example` mit `VIKUNJA_URL`, `VIKUNJA_API_TOKEN`, `MCP_TRANSPORT=sse`, `APP_PORT=6274`, `UID=1000`, `GID=1000` sowie optionalen Cloudflare Headern (`CF_CLIENT_ID`, `CF_CLIENT_SECRET`).
**ACCEPTANCE CRITERIA:**
- [ ] `deploy/docker-compose.yml` referenziert `.env` korrekt.
- [ ] `deploy/.env.example` enthält alle notwendigen Variablen.

## Testing Strategy

### Unit / Integration Tests
- `uv run pytest` muss weiterhin für alle bestehenden Tools durchlaufen (`stdio` Default).

### Manual Validation
- `docker compose up --build -d` im Ordner `deploy/` ausführen.
- Überprüfen der Logs (`docker compose logs -f`).
- Curl Test auf `http://localhost:6274/sse` (oder entsprechender SSE Startpunkt).

## Acceptance Criteria

- [ ] `server.py` und `pyproject.toml` sind für SSE vorbereitet.
- [ ] Deployment erfolgt sauber über `deploy/docker-compose.yml`.
- [ ] Container läuft aus Sicherheitsgründen nicht als `root`.
- [ ] Alle Tests bestehen weiterhin.

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt und validiert.
- [ ] Plan-/PRD-Abweichungen (Hinzufügen von deploy-Strukturen) sind abgenommen.
- [ ] Feature ist bereit für `/document` und `/commit`.
