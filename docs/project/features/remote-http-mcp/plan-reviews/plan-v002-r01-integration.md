# Feature Plan Review Integration: Remote HTTP MCP v002 Runde r01

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangsplan | `docs/project/features/remote-http-mcp/plan-v002.md` |
| Neue Plan-Version | `docs/project/features/remote-http-mcp/plan-v003.md` |
| Review | `docs/project/features/remote-http-mcp/plan-reviews/plan-v002-r01-review.md` |
| Ausgangsversion | `v002` |
| Zielversion | `v003` |
| Review-Runde | `r01` |
| Integrationskontext | Autor-Session bestätigt |
| Aktualisierter TASKS.md-Eintrag | ja (Link aktualisiert auf v003) |

## Kurzfazit

Die Review hat wichtige architektonische Lücken bezüglich Docker-Deployment (Host-Binding `0.0.0.0`) und FastMCP-Besonderheiten (DNS-Rebinding, transitive Dependencies) aufgedeckt. Diese wurden alle adressiert. Der Plan wurde zudem um Testing-Schritte und Docker Best-Practices (.dockerignore, Healthcheck) erweitert und liegt nun in `v003` übergabereif vor.

## Entscheidungen

| ID | Review-Punkt | Entscheidung | Begründung | Änderung in neuer Plan-Version |
|---|---|---|---|---|
| R-01 | **Dependencies**: `uvicorn`/`starlette` sind bereits transitive Abhängigkeiten. | übernehmen | Reduziert Wartungsaufwand und vermeidet Versionskonflikte. | Task 1 (UPDATE pyproject.toml) gestrichen/ersetzt. |
| R-02 | **Transportprotokoll**: SSE ist deprecated, `streamable-http` ist der Standard. | teilweise übernehmen | Um maximale Kompatibilität mit Clients (z.B. ChatGPT Remote) zu wahren, aber zukunftssicher zu sein. | Transport-Weiche in `server.py` unterstützt nun `sse` und `streamable-http`. |
| R-03 | **Host-Binding**: Server muss auf `0.0.0.0` binden. | übernehmen | Zwingende Voraussetzung für Docker-Erreichbarkeit. | ENV `FASTMCP_HOST=0.0.0.0` in Tasks (Dockerfile & Compose) fixiert. |
| R-04 | **DNS-Rebinding-Schutz**: MCP blockt evtl. Reverse-Proxy-Requests (SDK >= 1.27). | übernehmen | Zwingend für den im Scope erwähnten Cloudflare Access Einsatz. | Task 1 enthält Prüfung/Evaluierung für FastMCP-Konfiguration bzgl. DNS-Rebinding. |
| R-05 | **Task-Template**: Tasks fehlen PATTERN, IMPORTS, GOTCHA, VALIDATE. | übernehmen | Entspricht dem Plan-Template-Standard für `/execute`. | Alle Tasks um diese Abschnitte und konkrete Curl-Befehle ergänzt. |
| R-06 | **Port & Compose Config**: `FASTMCP_PORT` und `COMPOSE_PROJECT_NAME` fehlen. | übernehmen | Best Practice analog zum referenzierten CompACT Diary Pattern. | Variablen in Compose-Task und `.env.example` aufgenommen. |
| R-07 | **Testing**: Unit-Test für die Transport-Weiche fehlt. | übernehmen | Qualitätssicherung der `main()` Methode. | Task 2 (UPDATE test_server.py) neu hinzugefügt. |
| R-08 | **Docker Best-Practices**: `.dockerignore` und `HEALTHCHECK` (optional). | übernehmen | Verbessert Build-Performance und Container-Monitoring. | Task 3 (CREATE .dockerignore) ergänzt und Healthcheck in Dockerfile-Task aufgenommen. |
| R-09 | **Betroffene Dateien**: Fehlende Referenzen (Tests, FastMCP Docs). | übernehmen | Hilft dem execute-Agenten bei der Umsetzung. | `tests/test_server.py` und FastMCP Docs unter "Pflichtlektüre" ergänzt. |

## Übernommene Änderungen an der neuen Plan-Version

- **Task 1** aktualisiert auf die Transport-Weiche für `sse` und `streamable-http` und um Metadaten ergänzt.
- **Task 2** (Unit Test für Weiche) neu hinzugefügt.
- **Task 3** (.dockerignore) neu hinzugefügt.
- **Task 4** (Dockerfile) um Healthcheck und Best-Practices (non-root) ergänzt.
- **Task 5** (Compose Setup) um Variablen wie `FASTMCP_HOST`, `FASTMCP_PORT` und `COMPOSE_PROJECT_NAME` angereichert.
- Scope und Architektur-Kapitel (inkl. Lektüre-Referenzen) aktualisiert.

## Plan-Änderungshistorie

Folgende Zeile wurde in der neuen Plan-Version `v003` ergänzt:
`| v003 | 2026-06-25 | Review Integration | Parallele Unterstützung von sse & streamable-http, DNS-Rebinding-Schutz, Host-Binding via FASTMCP_HOST, Tasks gemäss Template aktualisiert, Unit Tests & .dockerignore hinzugefügt. |`

## Teilweise übernommene Punkte

- **Transportprotokoll (R-02):** Wir wechseln nicht vollständig auf `streamable-http`, sondern belassen `sse` explizit als Option, um die gewünschte Legacy-Kompatibilität zu wahren.

## Abgelehnte Punkte

- Keine.

## Offene Punkte

- Keine.

## Empfehlung für den nächsten Schritt

Der Plan ist jetzt detailliert und alle Risiken sind angesprochen. Er ist bereit für die fachliche Bestätigung und anschliessend für die Ausführung via `/execute docs/project/features/remote-http-mcp/plan-v003.md`.

## Qualitätscheck vor Abschluss

- [x] Ausgangsplan, Review-Datei, Ausgangsversion, Zielversion und Review-Runde sind korrekt dokumentiert.
- [x] Jede relevante Review-Empfehlung ist als übernommen, teilweise übernommen, abgelehnt oder offen dokumentiert.
- [x] Ablehnungen sind nachvollziehbar begründet.
- [x] Die neue Plan-Version ist genannt und bleibt von der Ausgangsversion unterscheidbar.
- [x] Die Plan-Änderungshistorie der neuen Plan-Version enthält einen Eintrag für die Review-Integration.
- [x] `TASKS.md` zeigt auf die neue Plan-Version.
- [x] Offene Punkte enthalten einen konkreten nächsten Klärungsschritt (keine vorhanden).
- [x] Die Empfehlung für den nächsten Schritt nennt `/execute`.
