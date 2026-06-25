# Feature Plan Review: Remote HTTP MCP v002 Runde 01

## Metadaten

| Feld | Wert |
|---|---|
| Feature-Plan | `docs/project/features/remote-http-mcp/plan-v002.md` |
| Logische Plan-Version | `v002` |
| Review-Runde | `r01` |
| Reviewer-Kontext | Frische Session nach `/prime` bestätigt: ja |
| Vorherige Review-/Integration-Datei | Nicht relevant (v002 entstand aus v001-Review-Feedback, aber kein formaler Review-Skill-Lauf dokumentiert) |
| Referenziertes PRD | Nicht relevant (Feature aus User Request, kein separates PRD) |

## Kurzfazit

Der Plan ist strukturell gut aufgebaut und adressiert ein klares, sinnvolles Feature: den Altiplano MCP-Server über ein Netzwerk-Transportprotokoll erreichbar zu machen und ein standardisiertes Docker-Deployment bereitzustellen. Die Trennung in vier Tasks ist nachvollziehbar und die Scope-Grenzen (kein eigenes Auth, kein entrypoint.sh) sind vernünftig gesetzt.

Allerdings enthält der Plan mehrere technische Ungenauigkeiten und Lücken, die `/execute` vor unnötige Recherche- und Architekturentscheidungen stellen würden. Die grössten Risiken sind: (1) `uvicorn` und `starlette` müssen **nicht** als explizite Dependencies hinzugefügt werden, da sie bereits transitive Dependencies von `mcp>=1.2.0` sind, (2) SSE ist ein **deprecated** MCP-Transportprotokoll – der Plan sollte `streamable-http` als modernen Standard einsetzen oder zumindest beide Optionen bewusst abwägen, (3) das Host/Port-Binding in Docker-Containern erfordert explizite Konfiguration (`0.0.0.0`) und das DNS-Rebinding-Schutzverhalten von MCP SDK ≥1.27 ist nicht adressiert, und (4) die Tasks enthalten keine PATTERN, IMPORTS, GOTCHA oder VALIDATE-Abschnitte gemäss Plan-Template.

## Stärken

- Klare Scope-Abgrenzung: Kein eigenes Auth, kein entrypoint.sh, kein PROD/TEST-Split – alles passend für einen stateless MCP-Server.
- Das `deploy/`-Pattern mit `docker-compose.yml` und `.env.example` orientiert sich sinnvoll an bestehenden Nutzer-Konventionen (CompACT Diary Referenz).
- Non-Root-User im Dockerfile via `UID`/`GID` Build-Args ist eine solide Sicherheitsentscheidung.
- Die Plan-Änderungshistorie von v001 zu v002 ist nachvollziehbar dokumentiert.
- Die Referenz auf `___TEMP/docker-compose.demo.yml` als Pattern-Vorlage ist hilfreich.

## Kritische Findings

| Bereich | Finding | Warum relevant | Konkreter Verbesserungsvorschlag |
|---|---|---|---|
| Dependencies | `uvicorn` und `starlette` werden als neue Dependencies geplant, sind aber bereits transitive Dependencies von `mcp>=1.2.0` (bestätigt in `uv.lock`: `mcp` v1.27.2 listet beide). | Unnötige explizite Dependencies verursachen potenzielle Versionskonflikte und Wartungsaufwand. `/execute` würde sie hinzufügen und damit ein Redundanz-Problem schaffen. | Task 1 streichen oder umformulieren: Prüfen, ob `mcp` die Dependencies bereits mitbringt (ja), und nur bei Bedarf pinnen. Stattdessen nach `uv sync` verifizieren, dass `uvicorn` und `starlette` bereits verfügbar sind. |
| Transportprotokoll | Plan setzt auf `transport="sse"`, das im MCP-Ökosystem offiziell als **deprecated/legacy** gilt. Streamable HTTP (`transport="streamable-http"`) ist der empfohlene Standard. | Neues Feature auf veraltetem Protokoll aufzubauen erzeugt technische Schuld. Viele neuere MCP-Clients unterstützen primär Streamable HTTP. | Primär `streamable-http` verwenden. Alternativ: Beide Transporte unterstützen (`MCP_TRANSPORT` akzeptiert `sse`, `streamable-http`, `stdio`), aber den Default für Remote auf `streamable-http` setzen. |
| Host-Binding | Kein expliziter Plan, wie der Server im Container auf `0.0.0.0` gebunden wird. FastMCP bindet standardmässig auf `127.0.0.1`. | Container-internes `127.0.0.1`-Binding macht den Server von aussen unerreichbar – der gesamte Docker-Use-Case würde still scheitern. | Host-Binding über `FASTMCP_HOST=0.0.0.0` Umgebungsvariable oder `mcp = FastMCP("altiplano", host="0.0.0.0")` im Code konfigurieren. Im Dockerfile oder `docker-compose.yml` als ENV setzen. |
| DNS-Rebinding-Schutz | MCP SDK ≥1.27 hat einen DNS-Rebinding-Schutz. Bei Zugriff über IP oder Reverse-Proxy-Domain kann `HTTP 421 Misdirected Request` auftreten. | Deployment hinter Cloudflare/Reverse Proxy ist explizit im Scope – ohne `stateless_http=True` oder korrekte `allowed_hosts` Konfiguration schlägt der Zugriff fehl. | Recherchieren und dokumentieren, wie der DNS-Rebinding-Schutz für Container-Deployments korrekt konfiguriert wird (z.B. Wildcard `*` oder explizite Domain in Settings). |
| Task-Qualität | Tasks fehlen PATTERN, IMPORTS, GOTCHA und VALIDATE gemäss Plan-Template. | Ein `/execute`-Agent kann die Tasks nicht ohne eigene Recherche umsetzen. Besonders GOTCHA für Host-Binding und VALIDATE mit konkreten Curl-Befehlen fehlen. | Alle Tasks gemäss Template-Standard ergänzen. |

## Architektur und Codebase-Fit

### Transport-Weiche in `main()`

Der gewählte Ansatz, `MCP_TRANSPORT` in der `main()`-Funktion auszuwerten, ist korrekt und minimal-invasiv. Allerdings sollte der Plan auch den Port konfigurierbar machen (z.B. über `MCP_PORT` oder `FASTMCP_PORT`), da verschiedene Deployment-Szenarien unterschiedliche interne Ports erfordern können.

Die aktuelle `main()`-Funktion (Zeile 669–670 in `server.py`) ist trivial (`mcp.run()`). Die Erweiterung um die Transport-Weiche ist sauber und betrifft nur diese Stelle. Bestehende Tools und die `_request()`-Helferfunktion bleiben unberührt – das ist korrekt.

### FastMCP-Konfiguration

Der Plan erwähnt in Task 2, dass „evtl. Anpassung nötig" sei, um auf `0.0.0.0` zu binden. Das ist keine optionale Überlegung, sondern eine **zwingende Voraussetzung** für den Docker-Use-Case. Die Lösung ist entweder:
- `mcp = FastMCP("altiplano", host="0.0.0.0")` (statisch im Code, problematisch für stdio-Modus)
- `FASTMCP_HOST=0.0.0.0` als Umgebungsvariable im Dockerfile/Compose (bevorzugt, da kein Code-Impact)

### Dependency-Analyse

Die `mcp` v1.27.2 im Lock-File bringt bereits `uvicorn`, `starlette`, `sse-starlette`, `pydantic-settings` und weitere relevante Packages als transitive Dependencies mit. Das bedeutet:
- Task 1 (Dependencies hinzufügen) ist **überflüssig** in der jetzigen Form.
- Falls die explizite Deklaration gewünscht ist (z.B. für Klarheit), sollte dies begründet werden, und die Versionen müssen zu den transitiven Versionen kompatibel sein.

## Scope und PRD-Abgleich

Kein separates PRD vorhanden. Die User Story und der Feature-Scope sind konsistent. Der in v002 hinzugekommene `deploy/`-Ordner mit Docker Compose ist eine sinnvolle Ergänzung und kein versteckter Zusatzscope, da er direkt dem Deployment-Bedürfnis des Features dient.

Die explizite Entscheidung gegen `entrypoint.sh` ist korrekt und gut begründet (stateless Server, keine DB-Abhängigkeit).

## Versionierung und Plan-Änderungshistorie

Plan-Version v002 ist korrekt gekennzeichnet. Die Änderungshistorie dokumentiert den Übergang von v001 zu v002 mit Anlass „Review Feedback" und Kurzbeschreibung. Die Änderungen (Docker-Setup an Nutzer-Konventionen angepasst) sind nachvollziehbar.

Allerdings gibt es keinen formalen Review-Datei-Verweis in der Historie – der v001→v002 Übergang scheint durch informelles Feedback im Chat entstanden zu sein, nicht durch `/review-feature-plan` und `/integrate-feature-plan-review`. Das ist kein Fehler, sollte aber im Bewusstsein bleiben.

## Implementation Plan und Task-Qualität

### Task 1: UPDATE pyproject.toml
- **Problem:** Wie oben beschrieben sind `uvicorn` und `starlette` bereits transitive Dependencies von `mcp`. Das explizite Hinzufügen ist unnötig.
- **Fehlende Abschnitte:** PATTERN, IMPORTS, GOTCHA, VALIDATE.
- **Vorschlag:** Task umwidmen zu „Verifizieren, dass die bestehenden Dependencies ausreichen" oder streichen.

### Task 2: UPDATE server.py
- **Positiv:** Die Code-Skizze ist verständlich und korrekt im Grundsatz.
- **Problem:** Das Host-Binding auf `0.0.0.0` ist als „evtl. nötig" formuliert, ist aber zwingend. Der Port sollte ebenfalls konfigurierbar sein (für den Compose-Port-Mapping). Die DNS-Rebinding-Problematik fehlt.
- **Fehlende Abschnitte:** PATTERN (z.B. bestehende `os.environ.get()`-Pattern in `_conf()`), IMPORTS (`os` ist bereits importiert – gut), GOTCHA (Host-Binding, DNS-Rebinding), VALIDATE (konkreter Curl-Befehl gegen laufenden SSE/HTTP-Server).
- **Vorschlag:** Die Konfiguration über FastMCP-native Umgebungsvariablen (`FASTMCP_HOST`, `FASTMCP_PORT`) ist sauberer als Code-Änderungen am `FastMCP()`-Konstruktor. Das hält den Code für stdio und remote gleich.

### Task 3: CREATE Dockerfile
- **Positiv:** Non-Root via UID/GID, uv-basiertes Image.
- **Problem:** Kein konkretes Dockerfile-Skelett oder Referenz-Pattern. Der Plan erwähnt „Slim/Alpine Python Image zusammen mit `uv`", aber nicht welches konkrete Base Image (z.B. `ghcr.io/astral-sh/uv:python3.11-alpine`). Auch fehlt, ob `uv sync --frozen` oder `uv pip install .` verwendet werden soll.
- **Fehlende Abschnitte:** PATTERN, GOTCHA (Alpine vs. Slim: manche Python-Packages brauchen C-Compiler auf Alpine), VALIDATE (konkreter `docker build` und `docker run` Befehl).

### Task 4: CREATE Deploy Setup
- **Positiv:** Gute Orientierung an CompACT Diary Patterns. Port-Mapping `${APP_PORT:-6274}:8000` ist sinnvoll.
- **Problem:** Der interne Port 8000 ist eine Annahme – FastMCP's Default-Port sollte verifiziert werden (oder via `FASTMCP_PORT` konfiguriert werden). Die `.env.example` sollte auch `FASTMCP_HOST=0.0.0.0` enthalten.
- **Fehlende Abschnitte:** PATTERN, GOTCHA, VALIDATE.
- **Nicht adressiert:** `COMPOSE_PROJECT_NAME` (empfehlenswert, um Namenskonflikte bei mehreren Stacks zu vermeiden, analog zum CompACT Diary Demo-Setup).

### Allgemein: Task-Reihenfolge
Die Reihenfolge ist grundsätzlich korrekt (Dependencies → Code → Docker → Compose). Allerdings ist Task 1 in der jetzigen Form überflüssig. Empfohlene Reihenfolge nach Überarbeitung:
1. Transport-Weiche in `server.py` implementieren
2. Dockerfile erstellen
3. Deploy-Setup (Compose + .env.example)
4. Manuelle End-to-End-Validierung

## Betroffene Dateien und Pflichtlektüre

- `src/altiplano/server.py` und `pyproject.toml` sind korrekt als betroffene Dateien identifiziert.
- `___TEMP/docker-compose.demo.yml` als Referenz ist hilfreich.
- **Fehlend:** `tests/test_server.py` sollte als Pflichtlektüre aufgeführt sein, da der Initialisierungstest (`test_mcp_initialization`) den `mcp.name`-Check enthält – falls sich die `FastMCP()`-Konstruktor-Argumente ändern (z.B. `host`-Parameter), könnte das Test-Auswirkungen haben.
- **Fehlend:** Referenz auf FastMCP-Dokumentation für Streamable HTTP Transport und `mcp.settings`.

## Datenmodell, Rollen und Berechtigungen

Nicht relevant. Keine Änderungen an Datenmodell oder Rollen. Die Absicherung über Reverse Proxy / Cloudflare Access ist korrekt adressiert.

## Testing und Validierung

### Bestehende Tests
Der Plan verlangt korrekt, dass `uv run pytest` weiterhin grün bleibt. Die 31 bestehenden Tests sind alle auf `stdio`-Transport ausgerichtet und sollten nicht betroffen sein, solange die `main()`-Funktion nicht im Default-Verhalten geändert wird.

### Fehlende Tests
- **Kein neuer Unit-Test geplant** für die Transport-Weiche. Ein einfacher Test, der verifiziert, dass `os.environ["MCP_TRANSPORT"]` korrekt ausgewertet wird, wäre sinnvoll.
- Die manuelle Validierung (Curl auf SSE/HTTP-Endpunkt) ist erwähnt, aber nicht als konkreter Schritt mit erwartetem Output formuliert.

### Manuelle Validierung
- Der Plan nennt `docker compose up --build -d` und `curl http://localhost:6274/sse`. Der SSE-Endpunkt-Pfad sollte verifiziert werden – bei Streamable HTTP wäre es typischerweise `/mcp` statt `/sse`.

## Risiken, Gotchas und Edge Cases

| Risiko | Schwere | Adressiert im Plan? |
|---|---|---|
| Server bindet auf `127.0.0.1` statt `0.0.0.0` im Container | Hoch | Nur als „evtl." erwähnt |
| DNS-Rebinding-Schutz blockt Reverse-Proxy-Zugriffe | Hoch | Nicht adressiert |
| SSE ist deprecated, Clients könnten es nicht mehr unterstützen | Mittel | Nicht adressiert |
| Alpine-Image und C-Extension-Kompatibilität | Niedrig | Nicht adressiert |
| Port-Konflikt wenn `FASTMCP_PORT` nicht gesetzt | Niedrig | Teilweise (Port-Mapping in Compose) |
| `uv.lock` Änderungen bei unnötigem Dependency-Add | Niedrig | Nicht adressiert |

## Übergabereife für Execute

Der Plan ist **noch nicht** `/execute`-reif. Ein frischer Umsetzungsagent müsste:
1. Selbst recherchieren, ob `uvicorn`/`starlette` schon installiert sind (Finding: ja).
2. Selbst entscheiden, ob SSE oder Streamable HTTP verwendet wird.
3. Selbst herausfinden, wie Host-Binding und DNS-Rebinding konfiguriert werden.
4. Fehlende Task-Abschnitte (PATTERN, GOTCHA, VALIDATE) selbst ergänzen.

Nach Behebung der kritischen Findings wäre der Plan umsetzungsreif.

## Verbesserungsvorschläge nach Priorität

### Muss vor `/execute` geklärt werden

- **Transport-Protokoll entscheiden:** SSE (deprecated) oder Streamable HTTP (empfohlen)? Oder beide unterstützen? Konkret: welchen Wert soll `MCP_TRANSPORT` im Remote-Fall haben und welcher Curl-Endpunkt wird für die Validierung genutzt?
- **Host-Binding zwingend adressieren:** Im Dockerfile oder docker-compose.yml `FASTMCP_HOST=0.0.0.0` setzen. Im Plan als expliziten Schritt dokumentieren, nicht als „evtl.".
- **DNS-Rebinding-Schutz klären:** Recherchieren, ob `FastMCP` in v1.27+ einen `allowed_hosts`-Parameter oder ein `stateless_http`-Flag hat, und die korrekte Konfiguration im Plan dokumentieren.
- **Task 1 überarbeiten oder streichen:** `uvicorn` und `starlette` sind bereits transitive Dependencies von `mcp`. Explizites Hinzufügen ist nur sinnvoll, wenn es bewusst als Pin gewünscht ist – dann mit Begründung.

### Sollte verbessert werden

- **Tasks mit PATTERN, GOTCHA, VALIDATE ergänzen:** Gemäss Plan-Template-Standard. Insbesondere VALIDATE mit konkreten Curl-Befehlen und erwartetem Output.
- **Konkretes Dockerfile-Skelett einfügen:** Mindestens Base-Image, User-Setup-Befehle und CMD als Pseudo-Code im Task.
- **Port-Konfiguration explizit machen:** `FASTMCP_PORT` in `.env.example` aufnehmen und im Compose-Port-Mapping korrekt referenzieren (interner Port = `FASTMCP_PORT`, externer Port = `APP_PORT`).
- **`COMPOSE_PROJECT_NAME` in `.env.example` aufnehmen:** Analog zum CompACT Diary Pattern, um Namenskonflikte zu vermeiden.
- **Unit-Test für Transport-Weiche:** Einfachen Test ergänzen, der verifiziert, dass `main()` mit verschiedenen `MCP_TRANSPORT`-Werten korrekt reagiert.

### Optional

- **Streamable HTTP und SSE parallel unterstützen:** `MCP_TRANSPORT` akzeptiert `stdio` (Default), `sse` (Legacy) und `streamable-http` (Modern). Gibt maximale Kompatibilität.
- **Health-Check im Dockerfile:** Ein einfacher `HEALTHCHECK` für den HTTP-Endpunkt wäre für Docker-Monitoring nützlich.
- **`.dockerignore` erstellen:** Um `.venv`, `.git`, `___TEMP`, `tests/` etc. aus dem Build-Kontext auszuschliessen und Build-Zeiten zu reduzieren.

## Offene Fragen für die Integration

- Soll der Plan primär auf **Streamable HTTP** umgestellt werden (empfohlen), oder soll SSE beibehalten werden (Legacy-Kompatibilität)?
- Soll Task 1 (Dependencies) komplett gestrichen werden, oder gibt es einen Grund, `uvicorn`/`starlette` trotz transitiver Verfügbarkeit explizit zu pinnen?
- Welcher interne Standard-Port soll verwendet werden? FastMCP Default (8000) oder ein eigener?
- Soll eine `.dockerignore`-Datei Teil des Plans werden?

## Nächster Schritt

Gehe zurück in die Autor-Session, in der der Feature-Plan erstellt wurde. Führe dort aus:

```text
/integrate-feature-plan-review docs/project/features/remote-http-mcp/plan-v002.md docs/project/features/remote-http-mcp/plan-reviews/plan-v002-r01-review.md
```

## Qualitätscheck vor Abschluss

- [x] Das Review ändert den Feature-Plan nicht.
- [x] Kritische Findings sind konkret und handlungsorientiert.
- [x] Architektur, Task-Reihenfolge, betroffene Dateien, Tests und Validierung wurden geprüft.
- [x] PRD-Abgleich und Scope-Grenzen wurden betrachtet.
- [x] Plan-Version und Plan-Änderungshistorie wurden geprüft.
- [x] Verbesserungsvorschläge sind so formuliert, dass `/integrate-feature-plan-review` sie einzeln bewerten kann.
- [x] Der nächste Schritt verweist zurück in die Autor-Session mit `/integrate-feature-plan-review`.
