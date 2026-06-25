# Plan: OAuth 2.1 Authentifizierung via Cloudflare MCP Server Portal

## Status

**Feature-Status:** planned
**Erstellt:** 2026-06-25
**Plan-Version:** v002
**Quelle:** Architektur-Pivot nach `/execute`-Versuch von `plan-v001.md` (technische Blockade) und Folge-Recherche im User-Dialog
**Confidence Score:** 6/10 – Architektur und Free-Tier-Verfügbarkeit sind durch Dokumentation und GitHub-Issue-Recherche belegt; der exakte Cloudflare-Dashboard-Klickpfad wurde nicht selbst durchgeklickt, und für Claude Web besteht ein bestätigter, ungelöster Bug (siehe „Offene Fragen" in `plan-v001.md`, Befund 4)

> **Verhältnis zu `plan-v001.md`:** Dieser Plan ersetzt **nicht** `plan-v001.md`, sondern ist eine bewusste Abzweigung (Fork). `plan-v001.md` bleibt vollständig erhalten als Fallback-Referenz für einen Eigenbau-Authorization-Server (mit korrigierter, tatsächlich nutzbarer API), falls sich dieser Plan als nicht tragfähig erweist.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability (überwiegend Infrastruktur/Konfiguration, kein neuer Auth-Code-Kern) |
| Plan-Version | v002 |
| Komplexität | Medium (wenig Code, aber neue externe Abhängigkeit von einem Open-Beta-Cloudflare-Feature) |
| Primär betroffene Systeme | Cloudflare Zero Trust Dashboard (Access Application, MCP Server Portal), `docs/project/operations/*`, optional `src/altiplano/server.py` (nur bei optionaler JWT-Verifikation, siehe Task 6) |
| Abhängigkeiten | Bestehende Cloudflare Tunnel + Access Application (Feature `cloudflare-service-token`, done); Remote HTTP MCP Transport (Feature `remote-http-mcp`, done) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v002 | 2026-06-25 | Architektur-Pivot | Ersetzt den in `plan-v001.md` als technisch nicht umsetzbar identifizierten Eigenbau-Ansatz (`fastmcp.OAuthProvider`) durch das Cloudflare MCP Server Portal (Managed OAuth) als Authorization Server. Altiplano bleibt Resource Server ohne eigene Token-/Client-Verwaltung. `plan-v001.md` bleibt als Fallback-Referenz erhalten. |

## Feature Description

Statt einen eigenen OAuth-2.1-Authorization-Server in Altiplano zu implementieren (siehe `plan-v001.md`, dort als nicht ohne Weiteres umsetzbar identifiziert und von beiden relevanten Ökosystemen – offizielles `mcp`-SDK und Drittanbieter `fastmcp` – ohnehin als „advanced pattern, das die meisten vermeiden sollten" eingestuft), übernimmt **Cloudflare** über das Produkt-Feature **„MCP Server Portal"** (Open Beta, Teil von Cloudflare Zero Trust/Access) die komplette Authorization-Server-Rolle: Login, Dynamic Client Registration, PKCE, Discovery-Endpunkte, Token-Ausstellung.

Altiplano selbst bleibt ein reiner **Resource Server** und benötigt im MVP **keinen neuen Python-Code**. Die bestehende Cloudflare-Access-Absicherung (Service Token, Feature `cloudflare-service-token`) bleibt für die Verbindung Portal → Altiplano bestehen; sie wird nur nicht mehr direkt vom LLM-Client, sondern vom Portal verwendet.

## User Story

```text
Als Web-LLM-Client-Nutzer (primär ChatGPT Web; Claude Web mit bekanntem Risiko)
möchte ich mich via Cloudflare-verwaltetem OAuth-Login am MCP-Server autorisieren,
ohne dass ich (oder der Client) selbst HTTP-Header injizieren muss,
damit ich alle MCP-Tools direkt im Web-Client nutzen kann.
```

## Problem Statement

Identisch zu `plan-v001.md`: Web-LLM-Clients (ChatGPT Web, Claude Web) können keine statischen HTTP-Header (Cloudflare Service Token) injizieren. Der aktuell dokumentierte Workaround (`docs/project/operations/llm-client-setup.md`, Abschnitte 2 und 3) ist, stattdessen Claude Desktop oder Codex CLI zu nutzen – das ist für reine Web-Nutzung unbefriedigend.

## Solution Statement

1. In der bestehenden Cloudflare Access Application für `mcp-tasks.melbjo.win` wird **„Managed OAuth"** aktiviert (Access Application → Additional Settings).
2. Ein **MCP Server Portal** wird angelegt, das Altiplano als Upstream-MCP-Server registriert. Die Verbindung Portal → Altiplano nutzt die **bereits vorhandenen** Service-Token-Credentials (`CF-Access-Client-Id`/`CF-Access-Client-Secret`) – keine Änderung an `server.py` nötig.
3. Web-LLM-Clients verbinden sich künftig mit der **Portal-URL** (nicht mehr direkt mit `mcp-tasks.melbjo.win`); Cloudflare übernimmt dort den OAuth-2.1-Flow inkl. Login.
4. ChatGPT Web wird als primäres Zielsystem manuell validiert (siehe Befund 5 in `plan-v001.md`: kein bestätigter Bug, RFC-8707-konform laut OpenAI-Doku).
5. Claude Web wird ebenfalls getestet, aber mit dokumentiertem Risiko eines bekannten, von Anthropic als „not planned" geschlossenen Bugs (siehe `plan-v001.md`, Befund 4, [Issue #410](https://github.com/anthropics/claude-ai-mcp/issues/410)).
6. **Optional** (nicht MVP-blockierend): Eine schlanke `TokenVerifier`-Implementierung in `server.py` (native `mcp`-SDK-Klasse, siehe `plan-v001.md` Befund 2) zur zusätzlichen Prüfung des von Cloudflare ausgestellten JWT (`Cf-Access-Jwt-Assertion`) als Defense-in-Depth.

## Scope

### Im Scope

- Cloudflare Dashboard: Access Application auf „Managed OAuth" umstellen bzw. ergänzen.
- Cloudflare Dashboard: MCP Server Portal anlegen, Altiplano als Upstream registrieren (Wiederverwendung bestehender Service-Token-Credentials).
- Manuelle Validierung: ChatGPT Web Connector über Portal-URL einrichten und mindestens einen Tool-Call erfolgreich ausführen.
- Manuelle Validierung: Claude Web Connector-Versuch über Portal-URL, Ergebnis dokumentieren (Erfolg oder – erwartet – Fehlschlag mit Verweis auf Issue #410).
- Dokumentation aktualisieren: `docs/project/operations/docker-operations.md` und `docs/project/operations/llm-client-setup.md` (Portal-URL-Workflow für Web-Clients ergänzen; bestehende Header-basierte Anleitungen für Claude Desktop/Codex CLI bleiben unverändert, da diese weiterhin funktionieren).

### Optional (nicht MVP-blockierend)

- Task 6: Leichtgewichtiger `TokenVerifier` in `server.py` zur Prüfung des Cloudflare-JWT, als zusätzliche Absicherung auf Anwendungsebene (Defense-in-Depth, kein eigener Authorization Server).

### Nicht im Scope

- Kein SQLite-Token-Store, keine eigene Login-Seite, kein DCR-Code, keine PKCE-Validierung im eigenen Code (das übernimmt Cloudflare).
- Keine Lösung des Claude-Web-Bugs selbst – der liegt bei Anthropic und/oder Cloudflare und ist von hier aus nicht behebbar.
- Keine Migration von Claude Desktop/Codex CLI auf den neuen Portal-Weg – diese funktionieren bereits header-basiert und müssen nicht umgestellt werden.

## Rollen und Berechtigungen

- **Single User (Eigennutzer):** Login erfolgt über die in Cloudflare Access bereits konfigurierte Identity-Provider-Methode (z.B. One-Time-PIN), nicht über neue Credentials in Altiplano.
- **Web-LLM-Client:** Authentifiziert sich über das von Cloudflare verwaltete OAuth (DCR automatisch über das Portal).

## Context References

### Pflichtlektüre vor Umsetzung

- `docs/project/features/oauth-authentication/plan-v001.md` – Abschnitt „Offene Fragen" (Befunde 1–5) für die vollständige Recherche-Historie und den Grund dieses Forks.
- `docs/project/operations/docker-operations.md` – aktuelle Cloudflare-Access-Konfiguration (Service Token, Tunnel-Route), die als Basis für die Portal-Anbindung dient.
- `docs/project/operations/llm-client-setup.md` – aktuelle Client-Konfigurationen, insbesondere Abschnitte 2 (Claude Web) und 3 (ChatGPT Web), die durch den Portal-Workflow ersetzt/ergänzt werden.
- `src/altiplano/server.py` (L41–80, `_headers()`/`_conf()`) – Pattern für ENV-Variablen-Zugriff, relevant falls Task 6 (optionaler `TokenVerifier`) umgesetzt wird.

### Relevante Dokumentation

- [Cloudflare MCP Server Portals](https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/) – Funktionsweise, Upstream-Authentifizierung via Custom Headers/Service Token.
- [Cloudflare Zero Trust Free Plan](https://developers.cloudflare.com/cloudflare-one/account-limits/) – Bestätigung 50-Nutzer-Limit, dauerhaft kostenlos.
- [GitHub Issue #410 – claude.ai Web OAuth fails against Cloudflare Access Managed OAuth](https://github.com/anthropics/claude-ai-mcp/issues/410) – vollständiger Thread mit Root-Cause-Analyse (RFC 8707 `resource`-Parameter), Status `closed/not_planned`.
- [OpenAI Apps SDK – Auth](https://developers.openai.com/apps-sdk/build/auth) – Bestätigung, dass ChatGPT den RFC-8707-`resource`-Parameter korrekt sendet.

## Codebase Intelligence

### Projektstruktur und Architektur

Für das MVP dieses Plans ändert sich an `src/altiplano/` **nichts**. Die gesamte Umsetzung erfolgt im Cloudflare-Dashboard und in `docs/project/operations/`.

Falls Task 6 (optional) umgesetzt wird:

```
src/
└── altiplano/
    └── server.py   # UPDATE (optional): TokenVerifier-Subklasse + AuthSettings im main()-Block für Remote-Transport
```

### Patterns to Follow

- `_conf()` aus `server.py` (L55–56) für künftige ENV-Variablen (z.B. erwarteter Issuer/Audience-Wert für die optionale JWT-Prüfung).
- Bestehendes Transport-Weichen-Pattern in `main()` (`server.py` L669–692): Erweiterungen nur innerhalb `if transport in ("sse", "streamable-http")`, `stdio`-Betrieb bleibt unberührt.

### Anti-Patterns to Avoid

- Kein eigener Token-Store, keine eigene Client-Registrierung – das würde `plan-v001.md` wiederholen, dessen Komplexität hier bewusst vermieden wird.
- Keine Annahmen über exakte Cloudflare-Dashboard-Menüpfade ohne Live-Verifikation übernehmen (siehe „Offene Fragen" unten – das war der Fehler in `plan-v001.md`).

### Dependency Analysis

Keine neuen Python-Dependencies im MVP. Für Task 6 (optional) genügt die bereits installierte `mcp`-SDK-Klasse `mcp.server.auth.provider.TokenVerifier` – keine zusätzliche Dependency nötig.

## Architekturentscheidungen

### Gewählter Ansatz

**Cloudflare MCP Server Portal mit Managed OAuth als Authorization Server; Altiplano als reiner Resource Server.**

### Erwogene Alternativen

- **Eigener Authorization Server via nativer `mcp`-SDK-API** (`OAuthAuthorizationServerProvider`, siehe `plan-v001.md` Befund 2): Technisch möglich und korrekt dokumentiert, aber bewusst nicht gewählt – höherer sicherheitskritischer Wartungsaufwand, von beiden Ökosystemen (`mcp`-SDK-README, FastMCP-Doku) explizit nicht empfohlen. **Bleibt als Fallback in `plan-v001.md` dokumentiert.**
- **Drittanbieter-Package `fastmcp`:** Verworfen – widerspricht der nicht verhandelbaren Tech-Stack-Vorgabe (`mcp` offizielles SDK) und erfordert einen grösseren Refactor von `server.py` ohne fachlichen Mehrwert.

### Security, Performance, Maintainability

- **Security:** Geringere Angriffsfläche als Eigenbau, da kein selbstgeschriebener Token-Store/PKCE-Code. Risiko verschiebt sich auf Vertrauen in Cloudflares Open-Beta-Implementierung.
- **Risiken (explizit, siehe `plan-v001.md` Befunde 3–5):**
  - **Open Beta**, kein GA-Status.
  - **Claude Web:** Bestätigter, ungelöster Bug (Issue #410, von Anthropic „not planned" geschlossen). Realistisches Risiko: Claude Web funktioniert beim Start dieses Features evtl. nicht.
  - **ChatGPT Web:** Kein bestätigter Bug, aber auch keine bestätigte Erfolgsmeldung – Validierung in Task 3 ist die erste echte Probe.
- **Maintainability:** Deutlich weniger eigener Code als `plan-v001.md`; Wartungsaufwand verschiebt sich zu Cloudflare-Konfigurationspflege.

## Datenmodell und API-Mapping

Kein eigenes Datenmodell – Cloudflare verwaltet Clients, Tokens und Sessions selbst. Optionale Erweiterung (Task 6) prüft nur eingehende JWTs, persistiert nichts.

## Betroffene Dateien

### Bestehende Dateien

- `docs/project/operations/docker-operations.md` – UPDATE: Abschnitt zur Cloudflare-Konfiguration um Managed-OAuth/Portal-Setup ergänzen.
- `docs/project/operations/llm-client-setup.md` – UPDATE: Abschnitte 2 (Claude Web) und 3 (ChatGPT Web) durch Portal-URL-Workflow ersetzen/ergänzen, inkl. dokumentiertem Claude-Web-Risiko.
- `src/altiplano/server.py` – UPDATE (nur falls Task 6 umgesetzt wird): optionaler `TokenVerifier`.

### Neue Dateien

- Keine im MVP. Falls Task 6 umgesetzt wird: ggf. `tests/test_token_verifier.py` für den optionalen JWT-Check.

## Implementation Plan

### Phase 1: Cloudflare-Konfiguration (manuell, nicht automatisierbar)

Access Application auf Managed OAuth umstellen, MCP Server Portal anlegen, Altiplano als Upstream registrieren.

### Phase 2: Manuelle Validierung

ChatGPT Web und Claude Web gegen die neue Portal-URL testen, Ergebnisse dokumentieren.

### Phase 3: Dokumentation

Operations-Guides aktualisieren.

### Phase 4 (optional): Defense-in-Depth

Leichtgewichtige JWT-Verifikation in `server.py`.

## Step-by-Step Tasks

### Task 1: Cloudflare Access Application auf Managed OAuth umstellen

**Status:** planned
**Ziel:** Die bestehende Access Application für `mcp-tasks.melbjo.win` so konfigurieren, dass sie als OAuth-2.1-Authorization-Server für MCP-Clients agiert.

**IMPLEMENT (manuell im Cloudflare Zero Trust Dashboard):**
1. Zero Trust Dashboard → Access → Applications → bestehende Application für `mcp-tasks.melbjo.win` öffnen.
2. Unter „Additional settings" die Option **„Managed OAuth"** aktivieren.
3. Bestehende Identity-Provider-Policy (z.B. One-Time-PIN) unverändert lassen – sie gilt weiterhin für den menschlichen Login-Schritt.
4. Bestehenden Service Token (aus Feature `cloudflare-service-token`) **nicht löschen** – er wird in Task 2 für die Portal→Altiplano-Verbindung weiterverwendet.

**GOTCHA:** Der exakte Menüpfad/Name der Einstellung wurde aus Cloudflare-Dokumentationstext abgeleitet, nicht selbst im Dashboard nachvollzogen (Stand der Planung). **Vor Umsetzung live im Dashboard verifizieren und Abweichungen hier nachtragen.**

**ACCEPTANCE CRITERIA:**
- [ ] Managed OAuth ist für die Application aktiv.
- [ ] Bestehender Service Token funktioniert weiterhin unverändert für Header-basierte Clients (Claude Desktop, Codex CLI) – keine Regression.

**VALIDATE:**
- Manuell: `curl -i -H "CF-Access-Client-Id: <id>" -H "CF-Access-Client-Secret: <secret>" https://mcp-tasks.melbjo.win/sse` liefert weiterhin `200 OK` (Regressionstest für bestehende Clients).

---

### Task 2: MCP Server Portal anlegen und Altiplano als Upstream registrieren

**Status:** planned
**Ziel:** Ein Cloudflare MCP Server Portal erstellen, das Altiplano über die bestehenden Service-Token-Credentials als Upstream-MCP-Server einbindet.

**IMPLEMENT (manuell im Cloudflare Zero Trust Dashboard):**
1. Zero Trust Dashboard → Access Controls → AI Controls → MCP Server Portals → neues Portal anlegen.
2. Altiplano als Upstream-MCP-Server hinzufügen: URL `https://mcp-tasks.melbjo.win/sse` (bzw. `/mcp` für Streamable HTTP).
3. Authentifizierungsmethode für die Portal→Altiplano-Verbindung: **Custom Headers / Static Credentials**, mit den bestehenden Werten `CF-Access-Client-Id`/`CF-Access-Client-Secret`.
4. Portal-URL notieren (wird in Task 3/4 für die Client-Konfiguration benötigt).

**GOTCHA:** Exakte UI-Bezeichnungen laut Cloudflare-Doku, nicht selbst verifiziert. Falls „Custom Headers" als Option nicht verfügbar ist, alternativ „OAuth mit Admin-Credential" prüfen (dann wäre ggf. doch eine Code-Anpassung nötig – in diesem Fall Task als `needs_human` markieren und Plan aktualisieren).

**ACCEPTANCE CRITERIA:**
- [ ] Portal ist angelegt und zeigt Altiplano als verbundenen Upstream-Server.
- [ ] Portal kann die Tool-Liste von Altiplano erfolgreich abrufen (im Dashboard sichtbar, laut Doku synchronisiert Cloudflare alle ~2h, kann aber meist manuell angestossen werden).

**VALIDATE:**
- Dashboard zeigt Status „Connected" / Tool-Liste für den registrierten Altiplano-Upstream.

---

### Task 3: ChatGPT Web Connector über Portal-URL einrichten und validieren

**Status:** planned
**Ziel:** Nachweisen, dass ChatGPT Web sich ohne Header-Injection über das Portal verbinden und mindestens ein Tool erfolgreich aufrufen kann.

**IMPLEMENT (manuell):**
1. ChatGPT → Settings → Connectors → Developer Mode aktivieren.
2. Custom Connector mit der Portal-URL (aus Task 2) anlegen, Authentication: OAuth (wird durch Cloudflare automatisch erkannt/angeboten).
3. Login-Flow durchlaufen (Cloudflare Access Login, z.B. One-Time-PIN).
4. Ein einfaches Tool aufrufen (z.B. `list_projects`) und Ergebnis prüfen.

**ACCEPTANCE CRITERIA:**
- [ ] ChatGPT Web zeigt die Altiplano-Tools nach erfolgreichem Login an.
- [ ] Mindestens ein Tool-Call liefert ein korrektes Ergebnis (z.B. echte Projektliste aus Vikunja).

**VALIDATE:**
- Manueller Test in ChatGPT Web, Ergebnis-Screenshot/Log in Plan-Validation-Evidence dokumentieren.

**Falls fehlschlägt:** Fehlerbild (insbesondere ob ähnlich zu Issue #410) dokumentieren, Task auf `needs_human` setzen, ggf. Rückkehr zu `plan-v001.md` (Fallback) erwägen.

---

### Task 4: Claude Web Connector-Versuch über Portal-URL (dokumentiertes Risiko)

**Status:** planned
**Ziel:** Aktuellen Status von Claude Web gegen das Portal feststellen und dokumentieren – Erfolg wäre positiv überraschend, Fehlschlag ist der erwartete, dokumentierte Fall (Issue #410).

**IMPLEMENT (manuell):**
1. claude.ai → Settings → Integrations → Add Integration mit der Portal-URL.
2. Login-Flow durchlaufen.
3. Ergebnis dokumentieren: Tools sichtbar? Tool-Call erfolgreich?

**ACCEPTANCE CRITERIA:**
- [ ] Ergebnis (Erfolg oder Fehlschlag) ist in der Plan-Validation-Evidence dokumentiert, inkl. Datum (relevant, da der Bug zwischenzeitlich gefixt sein könnte).

**VALIDATE:**
- Falls Fehlschlag: Fehlerbild mit Issue #410 vergleichen (z.B. „Connector stays at 0 tools" oder Redirect-Loop). Falls abweichendes Fehlerbild: separat dokumentieren, ggf. neues Issue.
- Falls Erfolg: Issue #410 könnte zwischenzeitlich gefixt worden sein – in `plan-v001.md` Befund 4 nachtragen.

---

### Task 5: Operations-Dokumentation aktualisieren

**Status:** planned
**Ziel:** `docker-operations.md` und `llm-client-setup.md` um den neuen Portal-Workflow ergänzen.

**IMPLEMENT:**
- `docker-operations.md`: Neuer Unterabschnitt „MCP Server Portal (Managed OAuth) für Web-Clients" nach dem bestehenden Cloudflare-Abschnitt, mit Verweis auf Task 1/2.
- `llm-client-setup.md`: Abschnitte 2 (Claude Web) und 3 (ChatGPT Web) überarbeiten:
  - ChatGPT Web: Portal-URL-Workflow als primäre Methode (ersetzt die bisherige „nicht direkt möglich"-Einschränkung).
  - Claude Web: Portal-URL-Workflow dokumentieren, aber mit explizitem Hinweis auf den bekannten, ungelösten Bug (Issue #410) und Empfehlung, weiterhin Claude Desktop zu nutzen, bis der Bug behoben ist.

**ACCEPTANCE CRITERIA:**
- [ ] Beide Dateien spiegeln den tatsächlichen, in Task 3/4 validierten Stand wider (keine ungeprüften Behauptungen).

**VALIDATE:**
- Review: Dokumentation stimmt mit den Validation-Evidence-Einträgen aus Task 3/4 überein.

---

### Task 6 (Optional, nicht MVP-blockierend): Leichtgewichtiger `TokenVerifier` für Defense-in-Depth

**Status:** planned
**Ziel:** Zusätzliche Prüfung des von Cloudflare ausgestellten JWT (`Cf-Access-Jwt-Assertion`-Header) direkt in Altiplano, als zweite Verteidigungslinie unabhängig vom Edge-Vertrauen.

**IMPLEMENT:**
Nutzung der nativen, bereits installierten Klasse `mcp.server.auth.provider.TokenVerifier` (siehe `plan-v001.md` Befund 2 für die vollständige API-Bestätigung):
```python
from mcp.server.auth.provider import TokenVerifier, AccessToken

class CloudflareAccessTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        # JWT gegen Cloudflare Access Public Keys (JWKS) verifizieren
        ...
```
Integration in `main()` (nur für Remote-Transport) via `FastMCP(..., token_verifier=..., auth=AuthSettings(issuer_url=...))`.

**PATTERN:** `_conf()` für ENV-Variablen (z.B. `CF_ACCESS_TEAM_DOMAIN` für den JWKS-Endpunkt).

**GOTCHA:** Dies ist **kein** Ersatz für Task 1–5, sondern eine zusätzliche Härtung. Ohne diesen Task funktioniert das Feature bereits vollständig, da Cloudflare die Prüfung am Edge übernimmt.

**ACCEPTANCE CRITERIA:**
- [ ] `uv run pytest` bleibt grün (neuer Unit-Test mit Mock-JWT).
- [ ] Ungültige/abgelaufene Tokens werden serverseitig zusätzlich abgelehnt.

**VALIDATE:**
- `uv run pytest tests/test_token_verifier.py`

## Testing Strategy

### Unit / Integration Tests

- Kein neuer Python-Code im MVP (Task 1–5) → keine neuen Unit-Tests erforderlich.
- `uv run pytest` muss nach Abschluss weiterhin vollständig grün bleiben (Regressionstest, da keine Code-Änderung erwartet wird).
- Nur falls Task 6 umgesetzt wird: Unit-Test für `CloudflareAccessTokenVerifier` mit gemocktem JWT (gültig/abgelaufen/falsche Signatur).

### Regression Tests

- Bestehende Header-basierte Clients (Claude Desktop via `mcp-remote`, Codex CLI) müssen nach Task 1 weiterhin funktionieren (siehe Validate-Schritt in Task 1).

### Edge Cases

- Claude Web schlägt fehl (erwarteter Fall, siehe Task 4).
- Cloudflare-Portal-Synchronisation (laut Doku ca. alle 2h) zeigt Tools verzögert an – bei Tests ggf. manuellen Sync-Trigger im Dashboard suchen.

## Validation Commands

### Level 1: Regression

```bash
uv run pytest
```

### Level 2: Manuelle Validierung

1. Bestehender Service-Token-Zugriff (Regressionstest nach Task 1):
   ```bash
   curl -i -H "CF-Access-Client-Id: <id>" -H "CF-Access-Client-Secret: <secret>" https://mcp-tasks.melbjo.win/sse
   ```
2. ChatGPT Web Connector-Test (Task 3): Tool-Call `list_projects` über die UI ausführen.
3. Claude Web Connector-Test (Task 4): Verbindungsversuch über die UI, Ergebnis dokumentieren.

## Acceptance Criteria

- [ ] ChatGPT Web kann sich über das Cloudflare MCP Server Portal verbinden und Tools nutzen, ohne dass der Nutzer HTTP-Header manuell konfiguriert.
- [ ] Claude-Web-Status (Erfolg oder Fehlschlag) ist dokumentiert, mit Bezug auf Issue #410.
- [ ] Bestehende Header-basierte Clients (Claude Desktop, Codex CLI) funktionieren unverändert weiter (keine Regression).
- [ ] `uv run pytest` bleibt grün.
- [ ] `docker-operations.md` und `llm-client-setup.md` spiegeln den validierten Stand wider.

## Completion Checklist

- [ ] Tasks 1–5 sind umgesetzt und validiert (Task 6 optional).
- [ ] Validierungsergebnisse (insb. Task 3/4) sind mit Datum dokumentiert.
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt (insbesondere falls Claude Web entgegen Erwartung doch funktioniert oder ChatGPT Web entgegen Erwartung doch fehlschlägt).
- [ ] Feature ist bereit für `/document` und `/commit`.

## Documentation Notes

Nach Abschluss erstellt `/document`:
- **User Guide:** Wie verbindet man ChatGPT Web (und ggf. Claude Web) über das Cloudflare MCP Server Portal – inkl. dokumentiertem Claude-Web-Risiko.
- **Developer Notes:** Architektur-Entscheidung (Cloudflare als AS statt Eigenbau), Verweis auf `plan-v001.md` als Fallback-Referenz.
- **Operations Update:** `docker-operations.md` und `llm-client-setup.md` final abgleichen mit tatsächlichem Validierungsstand.

## Notes and Trade-offs

- **Hauptkompromiss:** Höheres Vertrauen in eine Open-Beta-Drittanbieter-Infrastruktur (Cloudflare), dafür praktisch kein eigener sicherheitskritischer Auth-Code – bewusst im Sinne von „Security vor Feature-Vollständigkeit" (PRD-Prinzip) gewählt.
- **Risiko Open Beta:** Das Feature kann sich ändern oder instabil sein. Falls dies während der Umsetzung zum Problem wird, ist `plan-v001.md` (korrigierte Eigenbau-Variante) der dokumentierte Fallback.
- **Claude Web bewusst nicht blockierend:** Der Plan gilt auch dann als erfolgreich abschliessbar, wenn nur ChatGPT Web funktioniert – Claude Web wird getestet und dokumentiert, ist aber kein Hard-Requirement für den Feature-Abschluss, da der Bug ausserhalb der Kontrolle dieses Projekts liegt.

## Offene Fragen

- Der exakte Cloudflare-Dashboard-Klickpfad (Menübezeichnungen, genaue Reihenfolge) wurde aus Dokumentationstext abgeleitet, nicht selbst nachvollzogen. **Bei Task 1/2 live verifizieren und hier nachtragen, falls abweichend.**
- Unklar, ob der Claude-Web-Bug (Issue #410) zum Zeitpunkt der tatsächlichen Umsetzung noch besteht – muss in Task 4 neu geprüft werden, unabhängig vom Recherche-Stand dieser Planung (2026-06-25).
- Unklar, ob für die Portal→Altiplano-Verbindung tatsächlich „Custom Headers" als Option zur Verfügung steht oder ob Cloudflare hierfür einen anderen Mechanismus erzwingt (siehe GOTCHA in Task 2). Falls nicht: Task 2 auf `needs_human` setzen und Plan entsprechend revidieren.

## Plan Review Notes

*Wird durch `/integrate-feature-plan-review` in späteren Plan-Versionen ergänzt. Beim initialen `plan-v002.md`: Nicht relevant.*
