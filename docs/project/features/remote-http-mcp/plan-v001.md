# Plan: Remote HTTP MCP

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001
**Quelle:** User Request (`/plan-feature Remote HTTP MCP`), PRD v006  
**Confidence Score:** 9/10 (Umsetzung nutzt native Features von FastMCP, Containerisierung ist Standard-Aufgabe)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v001 |
| Komplexität | Medium |
| Primär betroffene Systeme | server.py, pyproject.toml, Docker |
| Abhängigkeiten | uvicorn, starlette |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Der MCP Server wird um einen HTTP-Server (Server-Sent Events / SSE) erweitert, damit er nicht nur als lokaler `stdio`-Prozess läuft, sondern auch als Remote-Endpunkt für netzwerkbasierte LLM-Clients (z.B. ChatGPT, Claude) erreichbar ist. Dazu wird die Transport-Schicht übergebungsvariablen-gesteuert konfigurierbar gemacht und ein Dockerfile für die einfache Deployment-Automatisierung hinter einem Reverse Proxy hinzugefügt.

## User Story

```text
Als Nutzer netzwerkbasierter KI-Assistenten (z.B. ChatGPT)
möchte ich den Altiplano MCP-Server über einen HTTP(SSE)-Endpunkt erreichen,
damit ich meine Vikunja-Aufgaben auch remote (z.B. vom Smartphone) verwalten kann.
```

## Problem Statement

Bisher unterstützt der Server ausschließlich den `stdio`-Transport. Für Clients, die nicht auf dem gleichen Host lokalisiert sind (wie z.B. ChatGPT, Custom GPTs, Remote Claude Instanzen), ist dieser Transportweg unbrauchbar.

## Solution Statement

Durch Hinzufügen von `uvicorn` und `starlette` sowie die Anpassung der `main()`-Funktion in `server.py` kann `mcp.run(transport="sse")` genutzt werden. Die Steuerung erfolgt über eine neue Environment-Variable `MCP_TRANSPORT` (Default: `stdio`). Zusätzlich wird ein `Dockerfile` zur einfachen Containernutzung bereitgestellt.

## Scope

### Im Scope
- Erweiterung von `server.py` um eine dynamische Weiche für `transport="sse"` basierend auf `MCP_TRANSPORT`.
- Hinzufügen von `uvicorn` und `starlette` als (optionale) Server-Dependencies in der `pyproject.toml`.
- Erstellung eines schlanken `Dockerfile` für das Deployment des MCP-Servers.

### Nicht im Scope
- Eigene Authentifizierungslogik im Python-Code (wird gemäß PRD durch einen Reverse Proxy / Cloudflare Access gelöst).
- Änderungen an den MCP Tools (diese bleiben unberührt).
- SSL/TLS-Terminierung im Python-Code (erfolgt durch Reverse Proxy).

## Rollen und Berechtigungen

- Keine Änderungen an Rollen; der API-Token zu Vikunja bestimmt weiterhin die Berechtigungen. Die Nutzung des HTTP-Endpunkts sollte netzwerkseitig abgesichert werden (Reverse Proxy).

## Context References

### Pflichtlektüre vor Umsetzung
- `src/altiplano/server.py` - Warum: Hier befindet sich die `main()` Methode, welche `mcp.run()` aufruft.
- `pyproject.toml` - Warum: Dort müssen `uvicorn` und `starlette` hinzugefügt werden.

### Relevante Dokumentation
- [FastMCP Documentation](https://jlowin.github.io/fastmcp/api/server/) - Warum: Zeigt, wie der `transport="sse"` in `FastMCP` aktiviert wird.

## Codebase Intelligence

### Projektstruktur und Architektur
- Die aktuelle Architektur ist minimal (`server.py`). Diese Einfachheit soll beibehalten werden. Ein `Dockerfile` im Root-Verzeichnis ist das einzige neue strukturelle Element.

### Patterns to Follow
- Verwendung von Umgebungsvariablen mit dem Fallback `stdio`, um abwärtskompatibel zu bleiben.

### Anti-Patterns to Avoid
- Erstellen von eigenen FastAPI / Starlette-Instanzen, wenn `FastMCP.run(transport="sse")` dies out-of-the-box übernimmt.

### Dependency Analysis
- `uvicorn` und `starlette` werden benötigt. Wir ergänzen sie am besten als Standard-Dependencies. Für Einfachheit und da es ein zentrales Feature wird, können sie direkt zu den `dependencies` hinzugefügt werden.

## Architekturentscheidungen

### Gewählter Ansatz
Wir lesen `MCP_TRANSPORT` in der `main()` Methode aus. Wenn der Wert `sse` ist, rufen wir `mcp.run(transport="sse")` auf (Port kann ggf. in `FastMCP` nicht konfiguriert werden, wir prüfen das Verhalten von `uvicorn` und der Lib). Wir packen das Ganze in ein Alpine/Slim basiertes Python-Dockerfile, das `uv` nutzt, um die App zu installieren und den Server zu starten.

### Erwogene Alternativen
- *Alternative:* FastAPI-App manuell bauen und FastMCP mounten. *Entscheidung:* Dagegen, da `FastMCP.run` bereits einen integrierten SSE-Runner mit uvicorn mitbringt und dies den Code unnötig aufblähen würde.

### Security, Performance, Maintainability
- **Security:** Der HTTP-Endpunkt ist standardmäßig offen. Wir weisen in der Dokumentation ausdrücklich darauf hin, dass dieser Server zwingend hinter einem authentifizierenden Reverse Proxy betrieben werden muss, wenn er im Internet exponiert wird.
- **Maintainability:** Minimaler Code-Impact in `server.py` (nur die `main()` Methode).

## Betroffene Dateien

### Bestehende Dateien
- `pyproject.toml` - ADD: `uvicorn` und `starlette` zu den Dependencies hinzufügen.
- `src/altiplano/server.py` - UPDATE: `main()` Funktion anpassen, um `MCP_TRANSPORT` und `PORT` auszuwerten.

### Neue Dateien
- `Dockerfile` - CREATE: Container-Image Definition für den Server.

## Implementation Plan

### Phase 1: Dependencies & Code
Dependencies in `pyproject.toml` ergänzen und `server.py` umbauen.

### Phase 2: Containerization
`Dockerfile` schreiben und testen.

## Step-by-Step Tasks

### Task 1: UPDATE pyproject.toml
**Status:** planned  
**Ziel:** Hinzufügen von `uvicorn` und `starlette` als Abhängigkeiten.  
**IMPLEMENT:** Ergänze `uvicorn>=0.30.0` und `starlette>=0.37.2` in der `dependencies`-Liste in `pyproject.toml`.  
**ACCEPTANCE CRITERIA:**
- [ ] `pyproject.toml` enthält `uvicorn` und `starlette`.
- [ ] `uv sync` oder `uv run` installiert die neuen Abhängigkeiten erfolgreich.

**VALIDATE:**
- `uv sync`

### Task 2: UPDATE server.py
**Status:** planned  
**Ziel:** `main()` so umbauen, dass `MCP_TRANSPORT` ("stdio" oder "sse") respektiert wird.  
**IMPLEMENT:** 
In `src/altiplano/server.py` die `main()`-Methode anpassen:
```python
def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        # Note: Depending on FastMCP's run() method kwargs, we might just call it like this.
        # It relies on environment variables for binding, or hardcodes to localhost.
        # We will need to verify if host/port parameters exist in the current mcp version.
        mcp.run(transport="sse")
    else:
        mcp.run()
```
*GOTCHA:* FastMCP's `run()` Signatur für SSE prüfen, um den Server von außen (Docker-Container) erreichbar zu machen. Falls FastMCP nur auf 127.0.0.1 bindet und sich das nicht ändern lässt, erfordert dies evtl. doch ein manuelles Mounten in eine FastAPI-App oder das Verwenden von internen Settings.
**ACCEPTANCE CRITERIA:**
- [ ] `server.py` wertet `MCP_TRANSPORT` aus.
- [ ] Lokaler `stdio`-Betrieb funktioniert weiterhin reibungslos.

**VALIDATE:**
- `uv run pytest`

### Task 3: CREATE Dockerfile
**Status:** planned  
**Ziel:** Ein Dockerfile für den Einsatz als HTTP-Server erstellen.  
**IMPLEMENT:**
Schreibe ein standardmäßiges `Dockerfile` basierend auf `python:3.11-slim` oder `ghcr.io/astral-sh/uv:python3.11-alpine`. 
Es sollte das Projekt via `uv` installieren, `MCP_TRANSPORT=sse` setzen, und als CMD `altiplano` (den CLI entrypoint) ausführen.
**ACCEPTANCE CRITERIA:**
- [ ] Dockerfile im Root-Verzeichnis vorhanden.
- [ ] Image lässt sich bauen.

**VALIDATE:**
- Manuelle Prüfung: `docker build -t altiplano-mcp .`

## Testing Strategy

### Unit / Integration Tests
- Bestehende Tests (`uv run pytest`) müssen weiterhin erfolgreich durchlaufen, da `stdio` nicht beeinträchtigt wird.

### Manual Validation
- Ausführen des Servers mit `MCP_TRANSPORT=sse uv run altiplano` und Überprüfen per Browser oder curl auf SSE Endpoint (z. B. `http://localhost:8000/sse` oder `http://localhost:8000`).

## Acceptance Criteria

- [ ] `pyproject.toml` aktualisiert
- [ ] `server.py` unterstützt `MCP_TRANSPORT=sse`
- [ ] `Dockerfile` vorhanden und funktionstüchtig
- [ ] Lokale `stdio` Ausführung bleibt unberührt
- [ ] Keine Fehler in der bestehenden Test-Suite

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] Alle relevanten Tests laufen erfolgreich
- [ ] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Beim Document-Schritt muss im User Guide ergänzt werden, wie der Docker-Container gestartet wird (inkl. Volumen für `.config/altiplano/env` oder ENV-Variablen `VIKUNJA_URL`/`VIKUNJA_API_TOKEN`) und dass ein Reverse Proxy mit Basic Auth o.Ä. für Remote-Zugriffe zwingend empfohlen wird.

## Offene Fragen
- Keine kritischen Fragen.
