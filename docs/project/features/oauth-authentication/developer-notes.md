# Developer Notes: OAuth 2.1 Authentifizierung via Cloudflare MCP Server Portal

## Überblick

Dieses Feature löst das Problem, dass Web-LLM-Clients keine benutzerdefinierten HTTP-Header für die Authentifizierung gegen einen durch Cloudflare Access geschützten MCP-Server mitsenden können. Anstatt einen eigenen OAuth-2.1-Authorization-Server in Python zu implementieren (wie in `plan-v001.md` erwogen), übernimmt das Cloudflare MCP Server Portal diese Rolle vollständig. Altiplano bleibt ein reiner Resource Server ohne eigene Token- oder Client-Verwaltung.

## Referenzen

- Plan: `docs/project/features/oauth-authentication/plan-v003.md`
- PRD: `docs/project/prds/vikunja-mcp-server-v008.md`
- Relevante Guides: `docs/project/operations/docker-operations.md` und `docs/project/operations/llm-client-setup.md`

## Betroffene Dateien

Da der Altiplano-Python-Code unverändert blieb, betrifft diese Implementierung ausschließlich Operations- und Konfigurationsdateien:

| Datei | Zweck / Änderung |
|---|---|
| `docs/project/operations/docker-operations.md` | Hinzufügen von Abschnitt 2.5 zur Konfiguration des MCP Server Portals (Managed OAuth) in Cloudflare Zero Trust. |
| `docs/project/operations/llm-client-setup.md` | Aktualisierung von Abschnitt 2 (Claude Web Einschränkungen) und Abschnitt 3 (ChatGPT Web mit Portal-URL-Konfiguration). |
| `TASKS.md` | Aktualisierung des Feature-Status (Verschiebung zu den abgeschlossenen Features). |

## Architektur und Datenfluss

Das Zusammenspiel erfolgt wie folgt:
1. **ChatGPT Web (Client)** initiiert den OAuth 2.1 Handshake mit dem **Cloudflare MCP Server Portal (Gateway / Authorization Server)** unter `https://mcp.melbjo.win/mcp`.
2. Nach erfolgreichem Login des Nutzers stellt das Portal ein OAuth-Token aus.
3. Bei nachfolgenden JSON-RPC-Anfragen leitet das Portal die Requests an den **Altiplano MCP-Server (Resource Server)** unter `https://mcp-tasks.melbjo.win/sse` weiter.
4. Für diese Weiterleitung nutzt das Portal die statischen Custom Headers (`CF-Access-Client-Id` und `CF-Access-Client-Secret`), um die vorgelagerte Cloudflare Access Application zu passieren.

## Datenmodell und API-Mapping

Es gibt kein eigenes Datenmodell im Altiplano-Server für dieses Feature. Die gesamte Client-Registrierung (Dynamic Client Registration, DCR) und das Token-Management werden vollautomatisch von Cloudflare Access verwaltet.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| Dynamic Client Registration (DCR) | Erfolgreich (ChatGPT hat die Endpunkte automatisch über Auto-Discovery aufgelöst). |
| OAuth Login Flow | Erfolgreich (User konnte sich per OTP-E-Mail authentifizieren). |
| Tool-Ausführung in ChatGPT | Erfolgreich (Aufruf von `list_projects` lieferte die korrekte Projektliste aus Vikunja). |
| Regressionstest (pytest) | Erfolgreich (`uv run pytest` blieb grün mit 32 passed). |

## Betriebs- und Setup-Hinweise

Siehe ausführliche Anleitung in [docker-operations.md](../../operations/docker-operations.md).

## Wartungshinweise

- **Code Mode**: Es wird empfohlen, den Code-Modus im Portal deaktiviert zu lassen, wenn die Tools direkt einzeln für die KI sichtbar sein sollen.
- **Portals Beta**: Da es sich um ein Beta-Feature von Cloudflare handelt, sollten zukünftige Dashboard-Änderungen oder Protokoll-Updates beobachtet werden.
