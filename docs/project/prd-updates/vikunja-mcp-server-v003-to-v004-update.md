# PRD Update: vikunja-mcp-server v003 -> v004

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v003.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v004.md` |
| Ausgangsversion | `v003` |
| Zielversion | `v004` |
| Anlass | `Neues Feature / Cloudflare Access Support` |
| Datum | `2026-06-24` |
| Auslöser | `Menschlich angestossen` |

## Kurzfazit

Es wurde die Unterstützung von Cloudflare Service Tokens (`CF-Access-Client-Id` und `CF-Access-Client-Secret` HTTP-Headers) in den Scope des MVP aufgenommen, um die Vikunja-Instanz hinter Cloudflare Zero Trust / Cloudflare Access abzusichern und dennoch lokalen/remoten MCP-Zugriff zu ermöglichen.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| MVP Scope | Cloudflare Access Support hinzugefügt | Ermöglicht Betrieb hinter Cloudflare Access | MCP-Server kann die Sperre per Service Token umgehen |
| Security | Cloudflare Access Header-Authentifizierung | Erhöht die Sicherheit und beschreibt den Header-Fluss | Sichere API-Kommunikation |

## Änderungen in der neuen PRD-Version

- Executive Summary (v004) um Cloudflare Access Support im MVP ergänzt.
- Änderungshistorie um Eintrag zu v004 ergänzt.
- Scope und Ausbaustufen (MVP) um Cloudflare Access Support erweitert.
- Neue User Story US-8 (Cloudflare Access Service Token Authentifizierung) hinzugefügt.
- Kernfunktionen um "Cloudflare Access" erweitert (Prio: Must).
- Schnittstellen und Umsysteme um "Cloudflare Access Gateway" (ausgehend, optional) erweitert.
- Security-Abschnitt um "Cloudflare Access Authentication" ergänzt.
- Feature-Kandidaten um "Cloudflare Access Support" (Priorität 1b) ergänzt.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Die anderen MVP/Medium/Extended Features wurden unverändert gelassen, um den Scope nicht unnötig zu vergrößern.

## Offene Fragen und Annahmen

- Keine.

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/testing-api-mocks/plan-v001.md` | nein | Der Test-Mock-Plan befasst sich nur mit dem Mocking-Setup und ist von der HTTP-Header-Erweiterung unberührt. | Kein Schritt nötig. |

## Empfehlung für den nächsten Schritt

Die neue PRD-Version v004 ist hiermit angelegt. Wir erstellen nun den Feature-Plan `docs/project/features/cloudflare-service-token/plan-v001.md` und setzen die Implementierung um.
