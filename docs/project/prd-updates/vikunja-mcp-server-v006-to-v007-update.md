# PRD Update: vikunja-mcp-server v006 -> v007

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v006.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v007.md` |
| Ausgangsversion | `v006` |
| Zielversion | `v007` |
| Anlass | Neues Feature |
| Datum | `2026-06-25` |
| Auslöser | Menschlich angestossen |

## Kurzfazit

Die Entscheidung wurde getroffen, den Remote HTTP MCP-Endpunkt mit OAuth 2.1-Authentifizierung abzusichern, damit Web-LLM-Clients (ChatGPT Web, Claude Web, Gemini u. a.) den Server nutzen können. Diese Clients unterstützen ausschliesslich OAuth 2.1 (Authorization Code + PKCE) und können keine statischen HTTP-Header wie Cloudflare Service Tokens injizieren. OAuth 2.1 wird als eigenständiger Feature-Kandidat `oauth-authentication` im PRD aufgenommen. Implementierungsansatz: FastMCP `OAuthProvider` mit Custom SQLite-Token-Store. Die Rolle von Cloudflare Service Tokens wurde präzisiert: Sie gelten ausschliesslich für ausgehende Requests zu Vikunja, nicht für eingehende MCP-Client-Verbindungen.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| Kap. 1 – Executive Summary | Ausbaustufen: „Remote HTTP für ChatGPT Web" → „Remote HTTP MCP mit OAuth 2.1 für Web-LLM-Clients (ChatGPT Web, Claude Web, Gemini u. a.)" | Alle grossen Web-LLM-Clients erfordern OAuth 2.1 | Scope breiter, keine reine ChatGPT-Fixierung |
| Kap. 5 – Problemstellung | Problem-Beschreibung um OAuth 2.1-Einschränkung der Web-Clients ergänzt | Erklärt, warum Cloudflare Service Tokens als Eingangs-Auth nicht ausreichen | Fachliche Fundierung |
| Kap. 6 – Medium-Version | Remote HTTP MCP: OAuth 2.1 als explizite Voraussetzung. Neues Medium-Feature: OAuth 2.1 Authentifizierung (FastMCP OAuthProvider + SQLite-Token-Store). | Web-Clients brauchen OAuth, kein anderer Mechanismus kompatibel | Neue Zeile in Medium-Scope |
| Kap. 6 – Out of Scope | Externer IdP (Auth0, Casdoor usw.) explizit als Out of Scope markiert | Single-User-Betrieb, SQLite-Token-Store ausreichend | Klar abgegrenzt |
| Kap. 7 – User Stories | Neue US-9: Web-Client OAuth Login | Neue Nutzeranforderung für Medium-Version | Neue Zeile |
| Kap. 8 – Kernfunktionen | Neue Funktion „OAuth 2.1 Authentifizierung" (Medium, Must). „Cloudflare Access" zu „Cloudflare Access (ausgehend)" präzisiert. Remote HTTP MCP: Abhängigkeit von OAuth ergänzt. | Klare Trennung der beiden Auth-Ebenen | Neue Zeile, zwei angepasste Zeilen |
| Kap. 9 – Datenmodell | Neue Objekte: „OAuth Client" und „OAuth Token" für SQLite-Token-Store | Vollständiges Datenmodell inkl. Auth-Ebene | Zwei neue Zeilen |
| Kap. 10 – Schnittstellen | MCP-Client aufgeteilt in „lokal" (stdio, kein Auth) und „remote" (HTTP SSE, OAuth 2.1). OAuth Discovery Endpunkte als neue Schnittstelle. | Präzisere Schnittstellendokumentation | Zwei neue/angepasste Zeilen |
| Kap. 11 – Architektur | SQLite als geplanter Baustein für Medium-Version ergänzt | Vollständige Inventarliste | Eine neue Zeile |
| Kap. 12 – Security | Neuer Unterabschnitt: OAuth 2.1 Remote-Authentifizierung mit Sicherheitspflichten. Cloudflare Access klar als „ausgehend zu Vikunja" deklariert. | Sicherheitsrelevante Entscheidungen gehören ins PRD | Wesentlich erweiterter Security-Abschnitt |
| Kap. 13 – Demo-Szenarien | Neues Szenario: „Web-Client OAuth Login" | Neues Erfolgsszenario für Medium-Version | Neue Zeile |
| Kap. 14 – Risiken | Zwei neue Risiken (OAuthProvider-Komplexität, Redirect-URI-Varianz) und eine neue offene Frage (Redirect URIs je Client) | Sicherheitsrisiken frühzeitig dokumentieren | Vier neue Zeilen |
| Kap. 15 – Feature-Kandidaten | Neuer Kandidat: `oauth-authentication` (Prio 7b). Eintrag „Remote HTTP MCP": `oauth-authentication` als Abhängigkeit ergänzt. | Eigenständige Planbarkeit; klare Reihenfolge | Eine neue, eine angepasste Zeile |
| Kap. 16 – Appendix | FastMCP OAuthProvider Referenz-Notiz ergänzt | Wichtige Einschränkung für Implementierer | Neue Notiz |

## Änderungen in der neuen PRD-Version

- Kap. 1: Scope der Ausbaustufen auf alle Web-LLM-Clients (nicht nur ChatGPT Web) ausgeweitet.
- Kap. 5: Fachliche Begründung für OAuth 2.1 als Pflicht-Auth-Protokoll für Web-Clients ergänzt.
- Kap. 6: OAuth 2.1 Authentifizierung als eigenständiges Medium-Feature aufgenommen; Externer IdP als Out of Scope markiert.
- Kap. 7: Neue User Story US-9 (Web-Client OAuth Login).
- Kap. 8: Neue Kernfunktion „OAuth 2.1 Authentifizierung"; Cloudflare Access als ausgehend präzisiert; Remote HTTP MCP mit OAuth-Abhängigkeit.
- Kap. 9: Datenmodell um OAuth Client und OAuth Token erweitert.
- Kap. 10: MCP-Client-Schnittstelle in lokal/remote aufgeteilt; OAuth Discovery als neue Schnittstelle.
- Kap. 11: SQLite als geplanter Stack-Baustein erfasst.
- Kap. 12: Ausführlicher Security-Abschnitt für OAuth 2.1, inkl. Sicherheitspflichten bei der Implementierung.
- Kap. 13: Neues Demo-Szenario „Web-Client OAuth Login".
- Kap. 14: Zwei neue Risiken (OAuthProvider-Komplexität, Redirect-URI-Varianz) und eine neue offene Frage.
- Kap. 15: Neuer Feature-Kandidat `oauth-authentication` (Prio 7b); Remote HTTP MCP mit OAuth-Abhängigkeit.
- Kap. 16: FastMCP OAuthProvider Referenz-Notiz.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Alle bestehenden MVP-Features und deren Implementierungsstatus bleiben unverändert.
- Kein Rückbau von vorhandenen Features (Assignees, Reminder, etc.).
- Keine Änderungen an Extended-Features (Allgemeines Löschen, Task-Beziehungen).
- Die Cloudflare Tunnel-Infrastruktur (Remote HTTP MCP) bleibt als Transport-Layer erhalten und wird durch OAuth ergänzt, nicht ersetzt.

## Offene Fragen und Annahmen

- **Redirect URIs je Web-LLM-Client:** Müssen vor dem Feature-Plan `oauth-authentication` recherchiert und dokumentiert werden. Bekannt: ChatGPT Web verwendet voraussichtlich `https://chatgpt.com/aip/mcp/oauth/callback`; Claude Web und Gemini gemäss jeweiliger Anbieter-Dokumentation. → Klärung im Rahmen von `/plan-feature oauth-authentication`.
- **Annahme:** FastMCP `OAuthProvider` in der verwendeten FastMCP-Version unterstützt den vollständigen Authorization Code + PKCE Flow ohne externe Abhängigkeiten. Wird beim Feature-Plan validiert.
- **Annahme:** SQLite ist als Token-Store für Single-User-Betrieb ausreichend performant und sicher (bei korrektem Token-Hashing).

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/remote-http-mcp/plan-v003.md` | Ja | Plan als „done" abgeschlossen, behandelte Cloudflare Service Tokens als Eingangs-Auth für den MCP-Endpunkt. PRD definiert jetzt OAuth 2.1 als Pflicht für Web-Client-Kompatibilität. Der Plan ist veraltet bezüglich der Authentifizierungsschicht. | `/update-feature-plan docs/project/features/remote-http-mcp/plan-v003.md` ausführen, sobald der neue `oauth-authentication`-Feature-Plan vorliegt. |

## Empfehlung für den nächsten Schritt

1. Neue PRD-Version `v007` fachlich bestätigen.
2. `v007` und diese Update-Datei committen (`/commit`).
3. Neuen Feature-Plan `oauth-authentication` erstellen: `/plan-feature oauth-authentication` – mit Fokus auf FastMCP `OAuthProvider`, SQLite-Token-Store, Discovery-Endpunkte und Redirect-URI-Whitelist je Web-LLM-Client.
4. Danach: Feature-Plan `remote-http-mcp` mit `/update-feature-plan` nachziehen, um die OAuth 2.1-Abhängigkeit zu dokumentieren.

## Qualitätscheck vor Abschluss

- [x] Ausgangs-PRD, neue PRD-Version, Ausgangsversion und Zielversion sind korrekt dokumentiert.
- [x] Der Änderungsanlass ist klar beschrieben.
- [x] Die neue PRD-Version bleibt von der Ausgangsversion unterscheidbar.
- [x] Die Änderungshistorie im neuen PRD enthält einen Eintrag für die neue Version.
- [x] Auswirkungen auf vorhandene Feature-Pläne wurden geprüft.
- [x] Betroffene Feature-Pläne wurden nicht automatisch geändert.
- [x] Offene Fragen enthalten einen konkreten nächsten Klärungsschritt.
- [x] Die Empfehlung für den nächsten Schritt nennt Commit und `/plan-feature oauth-authentication`.
