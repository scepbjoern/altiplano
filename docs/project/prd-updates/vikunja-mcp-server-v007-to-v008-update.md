# PRD Update: vikunja-mcp-server v007 -> v008

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v007.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v008.md` |
| Ausgangsversion | `v007` |
| Zielversion | `v008` |
| Anlass | Fehlerkorrektur / Architektur-Widerspruch |
| Datum | 2026-06-25 |
| Auslöser | Beim `/execute`-Versuch von `plan-v001.md` erkannter technischer Widerspruch |

## Kurzfazit

PRD v007 beschreibt die OAuth-2.1-Authentifizierung als Eigenbau-Authorization-Server (FastMCP `OAuthProvider` + custom SQLite-Token-Store) und schliesst externe Identity Provider explizit aus. Beim `/execute`-Versuch von `plan-v001.md` wurde festgestellt, dass die angenommene Klasse `fastmcp.server.auth.OAuthProvider` im installierten, nicht verhandelbaren `mcp`-SDK nicht existiert. Eine Folge-Recherche ergab: Das offizielle `mcp`-SDK hat zwar eine eigene, technisch nutzbare native Auth-API (`OAuthAuthorizationServerProvider`/`TokenVerifier`), aber sowohl das offizielle SDK als auch das Drittanbieter-Framework raten unabhängig voneinander vom Eigenbau eines vollständigen Authorization Servers ab. Als Alternative wurde das **Cloudflare MCP Server Portal (Managed OAuth)** identifiziert, das die Authorization-Server-Rolle vollständig übernimmt und im Free-Tier verfügbar ist.

v008 korrigiert das PRD entsprechend: Cloudflare übernimmt die OAuth-2.1-Authorization-Server-Rolle; Altiplano bleibt Resource Server ohne eigenen Token-Store. Die Eigenbau-Variante bleibt als dokumentierte Fallback-Option erhalten (verweist auf `plan-v001.md`). Ein bekanntes, ungelöstes Risiko bei Claude Web (GitHub Issue #410) ist dokumentiert; Gemini-Validierung ist als offen markiert, ohne Scope-Entzug.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| Kap. 2 Änderungshistorie | Neue Zeile `v008` mit Anlass und Kurzbeschreibung | Pflichtabschnitt | Nachvollziehbarkeit |
| Kap. 1 Executive Summary, Kap. 6 Scope (Medium-Version) | OAuth-Beschreibung von Eigenbau auf Cloudflare-Portal-Ansatz umgestellt | Kernkorrektur | Architektur-Erwartung korrekt |
| Kap. 7 US-9 | Erfolgskriterium präzisiert (Cloudflare-Login statt Altiplano-eigene Login-Seite); Status-Zusatz zu ChatGPT/Claude/Gemini | Erwartungsmanagement, Gemini-Frage | Kein Scope-Verlust, nur Status-Klarheit |
| Kap. 8 Kernfunktionen | OAuth-Zeile umgestellt; Hinweis auf Fallback-Option ergänzt | Kernkorrektur | - |
| Kap. 9 Datenmodell | Entitäten „OAuth Client" / „OAuth Token" entfernt, Hinweis auf Fallback-Spezifikation in `plan-v001.md` ergänzt | Direkte Korrektur des Widerspruchs | Datenmodell schlanker |
| Kap. 10 Schnittstellen | „MCP Client (remote)"-Zeile und „OAuth Discovery Endpunkte"-Zeile korrigiert; neue Zeile „Cloudflare MCP Server Portal" | Architektur-Korrektur | - |
| Kap. 11 Starter Kit Nutzung | SQLite-Zeile entfernt | Kein Token-Store mehr nötig | - |
| Kap. 12 Security | OAuth-2.1-Absatz neu geschrieben (Cloudflare als AS, Altiplano als RS, Issue #410, Fallback-Verweis) | Kernkorrektur | - |
| Kap. 13 Demo-Szenarien | „Web-Client OAuth Login"-Zeile präzisiert (Cloudflare-Login, ChatGPT/Claude/Gemini-Status) | Konsistenz | - |
| Kap. 14 Risiken | Eigenbau-Risiko entfernt; neue Risiken „Cloudflare Open Beta", „Claude Web Bug #410", „Portal-Upstream-Authentifizierung unverifiziert"; neue offene Frage „Gemini-Validierung ausstehend" | Aktualität | - |
| Kap. 15 Feature-Kandidaten | OAuth-Zeile auf Cloudflare-Portal-Ansatz umgestellt | Konsistenz | - |
| Kap. 16 Appendix | FastMCP-`OAuthProvider`-Referenz ersetzt durch Cloudflare-Portal-Referenz + native `mcp`-SDK-Fallback-Referenz | Vollständigkeit | - |
| Out of Scope | Ausschlussklausel zu externen Identity Providern präzisiert: klassische IdPs (Auth0 etc.) bleiben ausgeschlossen, Cloudflare als bereits genutzte Infrastruktur ist davon nicht betroffen | Löst den Kern-Widerspruch auf | Ermöglicht Cloudflare-Ansatz ohne PRD-Bruch |

## Änderungen in der neuen PRD-Version

- OAuth-2.1-Strategie vollständig auf Cloudflare MCP Server Portal (Managed OAuth) als Authorization Server umgestellt; Altiplano bleibt Resource Server.
- Eigenbau-Datenmodell (OAuth Client/Token) entfernt, native `mcp`-SDK-Fallback-Option referenziert.
- Bekanntes Claude-Web-Risiko (GitHub Issue #410) in Security- und Risiken-Kapitel dokumentiert.
- Out-of-Scope-Klausel zu externen Identity Providern präzisiert, um den Widerspruch zum gewählten Ansatz aufzulösen.
- Gemini-Validierung als offene Frage markiert, ohne Scope-Entzug aus US-9.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Alle MVP-Inhalte (Kapitel 6, MVP-Abschnitt) bleiben unverändert – die Korrektur betrifft ausschliesslich die Medium-Version-OAuth-Strategie.
- Rollen, Zielgruppen (Kapitel 4) und Produktprinzipien (Kapitel 5) bleiben inhaltlich gleich, da der Architektur-Pivot keine fachlichen Rollen ändert.
- Demo-Szenarien zu MVP-Features (Projekte, Tasks, Kommentare) bleiben unverändert.

## Offene Fragen und Annahmen

- **Gemini-Validierung:** Noch nicht durchgeführt. Nächster Klärungsschritt: Bei Umsetzung des Feature-Plans (`plan-v003.md` o.ä.) entscheiden, ob Gemini in den aktuellen Validierungsumfang aufgenommen oder explizit zurückgestellt wird.
- **Portal-Upstream-Authentifizierung:** Noch nicht live im Cloudflare-Dashboard verifiziert, ob die bestehenden Service-Token-Credentials tatsächlich für die Portal→Altiplano-Verbindung nutzbar sind. Nächster Klärungsschritt: Preflight-Prüfung im Feature-Plan vor der eigentlichen Portal-Konfiguration.
- **Claude-Web-Status:** Kann sich ändern, falls Anthropic oder Cloudflare das zugrunde liegende Problem beheben. Nächster Klärungsschritt: Bei Umsetzung erneut prüfen und Ergebnis dokumentieren.

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/oauth-authentication/plan-v001.md` | ja (bereits dokumentiert) | War Ursache für die Erkenntnis, die zu diesem PRD-Update führte; bleibt unverändert als Fallback-Referenz | Keine Änderung nötig, bleibt wie dokumentiert |
| `docs/project/features/oauth-authentication/plan-v002.md` | ja | Befindet sich aktuell in `/integrate-feature-plan-review` (R-01 „PRD-Abgleich" war dort offener Punkt); dieses PRD-Update löst R-01 auf | `/integrate-feature-plan-review` in der Autor-Session fortsetzen, R-01 jetzt als „gelöst durch PRD v008" markieren |
| `docs/project/features/remote-http-mcp/plan-v004.md` | möglich | Dokumentiert eine generische Abhängigkeit zum OAuth-Feature (`main()`-Integration), ohne die spezifische Cloudflare-Portal-Architektur zu kennen | Bei Bedarf separat mit `/update-feature-plan` nachziehen, sobald die OAuth-Umsetzung selbst abgeschlossen ist |

## Empfehlung für den nächsten Schritt

Neue PRD-Version `v008` fachlich bestätigen und zusammen mit dieser Update-Datei committen. Danach in die unterbrochene `/integrate-feature-plan-review`-Session für `plan-v002.md` zurückkehren und R-01 dort unter Verweis auf `vikunja-mcp-server-v008.md` als gelöst dokumentieren.
