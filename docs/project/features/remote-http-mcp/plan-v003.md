# Plan: Remote HTTP MCP

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v003
**Quelle:** User Request (`/plan-feature Remote HTTP MCP`) und Review Feedback  
**Confidence Score:** 9/10 (Review R01 integriert, alle Architekturfragen und Deploy-Grenzfälle wie Host-Binding und DNS-Rebinding sind adressiert)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v003 |
| Komplexität | Medium |
| Primär betroffene Systeme | server.py, test_server.py, Docker, Compose |
| Abhängigkeiten | mcp (bringt uvicorn & starlette bereits mit) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |
| v002 | 2026-06-25 | Review Feedback | Docker-Setup an bestehende Nutzer-Konventionen (`deploy/` Folder, Compose, `.env`, `UID/GID`) angepasst. |
| v003 | 2026-06-25 | Review Integration | Parallele Unterstützung von `sse` & `streamable-http`, DNS-Rebinding-Schutz, Host-Binding via `FASTMCP_HOST`, Tasks gemäss Template aktualisiert, Unit Tests & `.dockerignore` hinzugefügt. |

## Feature Description

Der MCP Server wird um netzwerkbasierte Transportprotokolle (Server-Sent Events / SSE sowie Streamable HTTP) erweitert, damit er als Remote-Endpunkt für LLM-Clients (z.B. ChatGPT, Claude) erreichbar ist. 
Außerdem wird das Projekt um ein standardisiertes Deployment-Setup ergänzt, das sich an den bestehenden Host-Strukturen des Nutzers (wie bei Compact Diary) orientiert. Dazu gehört ein dediziertes `deploy/`-Verzeichnis mit `docker-compose.yml` und `.env.example`, sowie ein `Dockerfile` im Projekt-Root, welches als Non-Root User ausgeführt werden kann und Best Practices (Healthcheck, .dockerignore) enthält.

## User Story

```text
Als Nutzer netzwerkbasierter KI-Assistenten (z.B. ChatGPT)
möchte ich den Altiplano MCP-Server über einen HTTP(SSE/Streamable)-Endpunkt erreichen und per Docker Compose einfach updaten können,
damit ich meine Aufgaben auch remote verwalten kann und die Server-Wartung meinen gewohnten Mustern folgt.
```

## Problem Statement

Bisher unterstützt der Server ausschließlich den `stdio`-Transport und muss lokal gestartet werden. Ein professionelles, standardisiertes Deployment-Setup (Docker, Compose) fehlt bisher vollständig, was die Einbindung auf bestehenden Hosts (mit Reverse Proxies wie Cloudflare) erschwert.

## Solution Statement

1. Anpassung der `main()`-Funktion in `server.py` zur Unterstützung von `MCP_TRANSPORT="sse"` und `MCP_TRANSPORT="streamable-http"`.
2. Konfiguration des Host-Bindings (`0.0.0.0`) und DNS-Rebinding-Schutzes (für Reverse Proxies).
3. Hinzufügen von Basis-Unit-Tests für die Transport-Weiche in `test_server.py`.
4. Erstellen eines sicheren, anpassbaren `Dockerfile` (Non-Root via `UID`/`GID`, Healthcheck) inkl. `.dockerignore`.
5. Erstellen einer typischen Deployment-Struktur unter `deploy/docker-compose.yml` und `deploy/.env.example` (inkl. `COMPOSE_PROJECT_NAME` und Port-Variablen).

## Scope

### Im Scope
- Erweiterung von `server.py` für `transport="sse"` und `transport="streamable-http"`.
- Unit-Test für die Transport-Weiche.
- Erstellung eines `Dockerfile` (Non-Root, Healthcheck) und `.dockerignore`.
- Setup von `deploy/docker-compose.yml` und `deploy/.env.example`.

### Nicht im Scope
- Explizites Pinnen von `uvicorn` oder `starlette` (werden über `mcp` bereitgestellt).
- Eigene Authentifizierungslogik im Python-Code (erfolgt durch Reverse Proxy).
- Aufteilung in PROD und TEST.
- Skripte wie `entrypoint.sh` (Server ist stateless).

## Rollen und Berechtigungen

- Keine Änderungen an Vikunja-Rollen. Der HTTP-Endpunkt wird durch einen externen Reverse Proxy / Cloudflare Access abgesichert.

## Context References

### Pflichtlektüre vor Umsetzung
- `src/altiplano/server.py` - Hier muss die Transport-Weiche implementiert werden.
- `tests/test_server.py` - Für die Ergänzung des Tests zur Transport-Weiche.
- `___TEMP/docker-compose.demo.yml` - Referenz für Compose-Patterns (`build.context: ..`, Env-Files, Network, `COMPOSE_PROJECT_NAME`).
- [FastMCP Transports](https://jlowin.github.io/fastmcp/api/server/#fastmcp.FastMCP.run) - Referenz für `transport` Parameter (`sse`, `streamable-http`) und DNS-Rebinding Settings (sofern via Code oder `mcp.settings` gesteuert).

## Codebase Intelligence

### Projektstruktur und Architektur
- Die Python-Architektur (`server.py`) bleibt minimal.
- Neues Deployment-Pattern: `Dockerfile` und `.dockerignore` liegen im Root, `docker-compose.yml` und `.env.example` liegen im Verzeichnis `deploy/`.

### Patterns to Follow
- Verwendung von `UID` und `GID` Build-Argumenten im `Dockerfile`, um den Container ohne unnötige Root-Rechte laufen zu lassen.
- Nutzung der `.env` Datei im `deploy/` Ordner für alle Container-Settings (`APP_PORT`, `VIKUNJA_URL`, `FASTMCP_PORT`, `FASTMCP_HOST`).

### Dependency Analysis
- `uvicorn` und `starlette` sind bereits transitive Dependencies von `mcp>=1.2.0`. Es sind keine Änderungen an der `pyproject.toml` erforderlich, solange `uv sync` erfolgreich ist.

## Architekturentscheidungen

### Gewählter Ansatz
Wir lesen `MCP_TRANSPORT` in der `main()` Methode aus und rufen `mcp.run(transport=...)` entsprechend mit "sse", "streamable-http" oder dem Default "stdio" auf.
Das Host-Binding auf `0.0.0.0` für Docker wird primär über die Umgebungsvariable `FASTMCP_HOST=0.0.0.0` (in Compose/.env) gesteuert, um den Code für `stdio` unberührt zu lassen.

### Erwogene Alternativen
- **Ausschliesslich Streamable HTTP:** Wurde abgewogen, jedoch zugunsten einer parallelen Unterstützung von `sse` und `streamable-http` entschieden, da einige Clients (wie ChatGPT) evtl. Legacy-Anforderungen haben.

## Betroffene Dateien

### Bestehende Dateien
- `src/altiplano/server.py` - UPDATE: `main()` Funktion umbauen (Transport-Weiche).
- `tests/test_server.py` - UPDATE: Unit-Test für `main()` ergänzen.

### Neue Dateien
- `.dockerignore` - CREATE: Ausschluss unnötiger Dateien aus dem Build.
- `Dockerfile` - CREATE: Basis Image Definition, Non-Root-User, Healthcheck.
- `deploy/docker-compose.yml` - CREATE: Compose Setup.
- `deploy/.env.example` - CREATE: Umgebungsvariablen Template.

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Jeder Task ist atomic und einzeln validierbar.

### Task 1: UPDATE server.py
**Status:** planned  
**Ziel:** `main()` um Transport-Weiche ("stdio", "sse", "streamable-http") ergänzen und DNS-Rebinding klären.  
**IMPLEMENT:** 
In `src/altiplano/server.py` die `main()`-Methode anpassen:
```python
def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport in ("sse", "streamable-http"):
        # DNS-Rebinding-Schutz: Evtl. FastMCP Parameter für Host-Zulassung oder 
        # stateless_http=True evaluieren. (Z.B. mcp.settings ignorieren oder setzen).
        mcp.run(transport=transport)
    else:
        mcp.run()
```
**PATTERN:** `os.environ.get()` analog zu Vikunja API-Keys in `_conf()`.  
**IMPORTS:** `os` (bereits vorhanden).  
**GOTCHA:** FastMCP >= 1.27 hat einen DNS-Rebinding-Schutz. Wenn `mcp.run()` keine externen Hosts zulässt, muss das hier evtl. konfiguriert werden (z.B. über `mcp.settings` oder beim `FastMCP` Konstruktoraufruf).  
**ACCEPTANCE CRITERIA:**
- [ ] `server.py` wertet `MCP_TRANSPORT` aus und unterstützt 3 Modi.

**VALIDATE:**
- `uv run altiplano` startet standardmässig in `stdio`.
- `MCP_TRANSPORT=sse uv run altiplano` startet einen HTTP-Server.

### Task 2: UPDATE test_server.py
**Status:** planned  
**Ziel:** Logik der Transport-Weiche durch einen einfachen Test absichern.  
**IMPLEMENT:**
Einen Test `test_main_transport_selection(monkeypatch)` ergänzen, der mockt/verifiziert, dass `mcp.run` mit dem korrekten Parameter aufgerufen wird, wenn die ENV-Variable gesetzt ist.  
**PATTERN:** Bestehende pytest und `monkeypatch` Tests in der Datei.  
**IMPORTS:** `pytest`.  
**GOTCHA:** `mcp.run` sollte gepatcht werden, damit der Test nicht wirklich blockierend einen Server hochfährt.  
**ACCEPTANCE CRITERIA:**
- [ ] Unit-Test für `main()` existiert und deckt ENV-Variablen-Auswertung ab.

**VALIDATE:**
- `uv run pytest tests/test_server.py` besteht.

### Task 3: CREATE .dockerignore
**Status:** planned  
**Ziel:** Build-Kontext sauber halten.  
**IMPLEMENT:**
Erstelle `.dockerignore` im Root.  
Inhalt: `.venv/`, `.git/`, `___TEMP/`, `__pycache__/`, `tests/`, `docs/`, `deploy/`.  
**PATTERN:** Standard Python/uv `.dockerignore`.  
**IMPORTS:** n/a.  
**GOTCHA:** Verhindern, dass `deploy/.env` versehentlich in den Build gelangt.  
**ACCEPTANCE CRITERIA:**
- [ ] `.dockerignore` ist vorhanden und schliesst `.venv` etc. aus.

**VALIDATE:**
- Review der Dateiinhalte.

### Task 4: CREATE Dockerfile
**Status:** planned  
**Ziel:** Ein robustes Dockerfile für den Einsatz als HTTP-Server erstellen.  
**IMPLEMENT:**
Schreibe `Dockerfile` basierend auf `ghcr.io/astral-sh/uv:python3.11-alpine` (oder `slim`).
- ARG `UID=1000` und `GID=1000`
- Erstelle entsprechenden Gruppe und Benutzer (Non-Root).
- Kopiere Quellcode und führe `uv sync --frozen` (oder `uv pip install .`) durch.
- Setze ENV `FASTMCP_HOST=0.0.0.0` (als Fallback).
- Füge einen einfachen `HEALTHCHECK CMD curl --fail http://localhost:${FASTMCP_PORT:-8000}/ || exit 1` (oder entsprechenden Endpunkt) hinzu.
- CMD: `altiplano`  
**PATTERN:** Dockerfile Best Practices, Referenz CompACT Diary (für UID/GID).  
**IMPORTS:** n/a.  
**GOTCHA:** Auf Alpine könnten Build-Tools (gcc, musl-dev) fehlen, falls FastMCP Dependencies diese benötigen. Falls `uv sync` fehlschlägt, auf Debian `slim` wechseln.  
**ACCEPTANCE CRITERIA:**
- [ ] Dockerfile im Root-Verzeichnis vorhanden, läuft non-root und hat einen Healthcheck.

**VALIDATE:**
- `docker build -t altiplano-mcp .` läuft erfolgreich durch.

### Task 5: CREATE Deploy Setup (Compose & .env)
**Status:** planned  
**Ziel:** Das standardisierte Deployment-Setup erstellen.  
**IMPLEMENT:**
- Erstelle Verzeichnis `deploy/`.
- Erstelle `deploy/.env.example` mit: `COMPOSE_PROJECT_NAME=altiplano`, `VIKUNJA_URL`, `VIKUNJA_API_TOKEN`, `MCP_TRANSPORT=sse`, `FASTMCP_HOST=0.0.0.0`, `FASTMCP_PORT=8000`, `APP_PORT=6274`, `UID=1000`, `GID=1000`.
- Erstelle `deploy/docker-compose.yml` mit Service `app`, `build.context: ..`, Build-Args für `UID`/`GID`, Restart-Policy `unless-stopped` und Port-Mapping auf `${APP_PORT:-6274}:${FASTMCP_PORT:-8000}`.  
**PATTERN:** CompACT Diary `___TEMP/docker-compose.demo.yml`.  
**IMPORTS:** n/a.  
**GOTCHA:** DNS-Rebinding über Proxy. Ggf. in `.env.example` Cloudflare Header dokumentieren.  
**ACCEPTANCE CRITERIA:**
- [ ] Compose File und Env-Template sind vollständig.

**VALIDATE:**
- Im Verzeichnis `deploy/`: `docker compose config` wirft keine Fehler.

## Testing Strategy

### Unit / Integration Tests
- `uv run pytest` muss für alle bestehenden Tools durchlaufen (`stdio` Default).
- Der neue `test_main_transport_selection` prüft die Weiche.

### Edge Cases
- DNS-Rebinding: Aufruf über die Server-IP statt `localhost` könnte geblockt werden, wenn Host nicht explizit in FastMCP erlaubt ist.

## Validation Commands

### Level 1: pytest
```bash
uv run pytest
```

### Level 2: Manual Validation
Starten via uv:
```bash
MCP_TRANSPORT=sse FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 uv run altiplano
```
In zweitem Terminal (SSE Route Test):
```bash
curl -N -H "Accept: text/event-stream" http://localhost:8000/sse
```
(Für Streamable HTTP typischerweise `http://localhost:8000/mcp`).

Docker Compose Test:
```bash
cd deploy
cp .env.example .env
docker compose up --build -d
docker compose logs -f
curl http://localhost:6274/sse
```

## Acceptance Criteria

- [ ] `server.py` ist für `sse` und `streamable-http` vorbereitet und getestet.
- [ ] Deployment erfolgt sauber über `deploy/docker-compose.yml`.
- [ ] Container bindet korrekt auf `0.0.0.0` und läuft als Non-Root-User.
- [ ] Alle Unit-Tests bestehen.
- [ ] DNS-Rebinding-Schutz bei Reverse-Proxy Einsatz ist evaluiert/behoben.

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt und validiert.
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt.
- [ ] Feature ist bereit für `/document` und `/commit`.

## Documentation Notes

- In `user-guide.md` sollte erklärt werden, wie man den Server via Docker Compose startet und in LLM-Clients als Remote-Endpunkt (inkl. Cloudflare Access Tunnel) einbindet.

## Offene Fragen

- Keine (durch Review r01 geklärt).
