# Plan: OAuth 2.1 Authentifizierung via Cloudflare MCP Server Portal

## Status

**Feature-Status:** planned
**Erstellt:** 2026-06-25
**Plan-Version:** v003
**Quelle:** Review-Integration von `plan-v002.md` (Review: `plan-reviews/plan-v002-r01-review.md`)
**Confidence Score:** 7/10 – PRD-Abgleich über `/update-prd` gelöst (PRD v008), Tasks in Human-Runbook/Agent-Task getrennt, Preflight-Verifikation für die zentrale Cloudflare-Annahme ergänzt. Verbleibende Unsicherheit: Live-Verifikation von Portal-Upstream-Auth und Code-Mode-Verhalten steht noch aus, Claude-Web-Bug weiterhin ungelöst.

> **Verhältnis zu `plan-v001.md`/`plan-v002.md`:** Dieser Plan ersetzt **nicht** `plan-v001.md`. `plan-v001.md` bleibt vollständig erhalten als Fallback-Referenz für einen Eigenbau-Authorization-Server (native `mcp`-SDK-API), falls sich dieser Plan als nicht tragfähig erweist. `plan-v002.md` war der initiale Architektur-Pivot-Entwurf; `plan-v003.md` integriert die erste reguläre Review-Runde dazu.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability (überwiegend Infrastruktur/Konfiguration, kein neuer Auth-Code-Kern) |
| Plan-Version | v003 |
| Komplexität | Medium (wenig Code, aber neue externe Abhängigkeit von einem Open-Beta-Cloudflare-Feature) |
| Primär betroffene Systeme | Cloudflare Zero Trust Dashboard (Access Application, MCP Server Portal), `docs/project/operations/*` |
| Abhängigkeiten | Bestehende Cloudflare Tunnel + Access Application (Feature `cloudflare-service-token`, done); Remote HTTP MCP Transport (Feature `remote-http-mcp`, done); PRD `vikunja-mcp-server-v008.md` |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v002 | 2026-06-25 | Architektur-Pivot | Ersetzt den in `plan-v001.md` als technisch nicht umsetzbar identifizierten Eigenbau-Ansatz (`fastmcp.OAuthProvider`) durch das Cloudflare MCP Server Portal (Managed OAuth) als Authorization Server. Altiplano bleibt Resource Server ohne eigene Token-/Client-Verwaltung. `plan-v001.md` bleibt als Fallback-Referenz erhalten. |
| v003 | 2026-06-25 | Review-Integration r01 | Review `plan-v002-r01-review.md` integriert: PRD-Abgleich über `/update-prd` aufgelöst (siehe `docs/project/prds/vikunja-mcp-server-v008.md`); Tasks in Human-Runbook (1–5) und Agent-Task (6) getrennt; Preflight-Task für Portal-Upstream-Authentifizierung ergänzt; drei URL-Rollen getrennt dokumentiert; Code-Mode- und Tool-Allowlist-Entscheidung als Verifikationsschritt ergänzt; Validation-Evidence-Abschnitt hinzugefügt; optionaler TokenVerifier-Task (v002 Task 6) aus dem MVP entfernt und als Future-Feature vermerkt; Rollen/Berechtigungen präzisiert; Pflichtlektüre erweitert. **Hinweis:** `v002` selbst entstand als Fork nach einem technischen Execute-Stopp aus `plan-v001.md`, nicht als reguläre Review-Integration von `v001` – `v003` ist die erste reguläre PIV-Review-Integration in dieser Plan-Linie. |

## Feature Description

Statt einen eigenen OAuth-2.1-Authorization-Server in Altiplano zu implementieren (siehe `plan-v001.md`, dort als nicht ohne Weiteres umsetzbar identifiziert und von beiden relevanten Ökosystemen – offizielles `mcp`-SDK und Drittanbieter `fastmcp` – ohnehin als „advanced pattern, das die meisten vermeiden sollten" eingestuft), übernimmt **Cloudflare** über das Produkt-Feature **„MCP Server Portal"** (Open Beta, Teil von Cloudflare Zero Trust/Access) die komplette Authorization-Server-Rolle: Login, Dynamic Client Registration, PKCE, Discovery-Endpunkte, Token-Ausstellung.

Altiplano selbst bleibt ein reiner **Resource Server** und benötigt im MVP **keinen neuen Python-Code**. Die bestehende Cloudflare-Access-Absicherung (Service Token, Feature `cloudflare-service-token`) bleibt für die Verbindung Portal → Altiplano bestehen; sie wird nur nicht mehr direkt vom LLM-Client, sondern vom Portal verwendet.

Dieser Ansatz ist seit PRD `v008` die offizielle, dokumentierte Strategie (siehe `docs/project/prds/vikunja-mcp-server-v008.md`, Kapitel 6/8/12) – die in `plan-v002.md` noch offene PRD-Abweichung ist damit aufgelöst.

## User Story

```text
Als Web-LLM-Client-Nutzer (primär ChatGPT Web; Claude Web mit bekanntem Risiko)
möchte ich mich via Cloudflare-verwaltetem OAuth-Login am MCP-Server autorisieren,
ohne dass ich (oder der Client) selbst HTTP-Header injizieren muss,
damit ich alle MCP-Tools direkt im Web-Client nutzen kann.
```

## Problem Statement

Identisch zu `plan-v001.md`/PRD-Kapitel 5: Web-LLM-Clients (ChatGPT Web, Claude Web, Gemini) können keine statischen HTTP-Header (Cloudflare Service Token) injizieren. Der aktuell dokumentierte Workaround (`docs/project/operations/llm-client-setup.md`, Abschnitte 2 und 3) ist, stattdessen Claude Desktop oder Codex CLI zu nutzen – das ist für reine Web-Nutzung unbefriedigend.

## Solution Statement

1. In der bestehenden Cloudflare Access Application für `mcp-tasks.melbjo.win` wird **„Managed OAuth"** aktiviert (Access Application → Additional Settings).
2. Vor der eigentlichen Portal-Konfiguration wird **live verifiziert**, dass das Portal den Altiplano-Upstream über die bestehenden Service-Token-Credentials erreichen kann (Preflight, adressiert die zentrale, bisher nur aus Doku-Prosa abgeleitete Annahme).
3. Ein **MCP Server Portal** wird angelegt, das Altiplano als Upstream-MCP-Server registriert, inkl. bewusster Entscheidung zu Tool-Allowlist und Code-Mode-Verhalten.
4. Web-LLM-Clients verbinden sich künftig mit der **Portal-Client-URL** (nicht mehr direkt mit `mcp-tasks.melbjo.win`); Cloudflare übernimmt dort den OAuth-2.1-Flow inkl. Login.
5. ChatGPT Web wird als primäres Zielsystem manuell validiert, inkl. Prüfung der von OpenAI dokumentierten Auth-Anforderungen (RFC-8707-`resource`-Parameter, Redirect-URL).
6. Claude Web wird ebenfalls getestet, aber mit dokumentiertem Risiko eines bekannten, von Anthropic als „not planned" geschlossenen Bugs (siehe `plan-v001.md`, Befund 4, [Issue #410](https://github.com/anthropics/claude-ai-mcp/issues/410)).
7. Gemini wird in dieser Plan-Version **nicht** validiert (siehe PRD v008, offene Frage) – kein Scope-Entzug, nur zeitliche Priorisierung.

**Entfernt gegenüber `plan-v002.md`:** Der optionale Task 6 (`TokenVerifier`) wurde aus dem MVP entfernt – siehe „Notes and Trade-offs" für die Begründung und den Verweis auf ein mögliches Future Feature.

## URL-Übersicht

Drei unterschiedliche URLs sind in diesem Feature relevant und dürfen nicht verwechselt werden:

| # | URL-Rolle | Wert / Format | Verwendet von |
|---|---|---|---|
| 1 | Direkte Altiplano-Upstream-URL | `https://mcp-tasks.melbjo.win/sse` (bzw. `/mcp` für Streamable HTTP) | Header-basierte Clients (Claude Desktop, Codex CLI) – bleibt unverändert in Betrieb |
| 2 | Cloudflare Access Application URL | Identisch zu #1 (Access sitzt auf demselben Hostname) – wird durch Managed OAuth ergänzt, nicht ersetzt | Cloudflare-interne Konfiguration |
| 3 | Cloudflare MCP Server Portal Client-URL | Separate, vom Portal vergebene URL (Cloudflare-Konvention: `https://<subdomain>.<domain>/mcp`) – wird erst in Task 3 erzeugt | ChatGPT Web / Claude Web (Task 4/5) |

**Wichtig:** In Task 4/5 wird ausschliesslich URL #3 in die Web-Clients eingetragen, niemals URL #1.

## Scope

### Im Scope

- Cloudflare Dashboard: Access Application auf „Managed OAuth" umstellen bzw. ergänzen (Task 1, Human-Runbook).
- Preflight-Verifikation der Portal→Altiplano-Upstream-Authentifizierung (Task 2, Human-Runbook).
- Cloudflare Dashboard: MCP Server Portal anlegen, Altiplano als Upstream registrieren, Tool-Allowlist und Code-Mode-Verhalten bewusst entscheiden (Task 3, Human-Runbook).
- Manuelle Validierung: ChatGPT Web Connector über Portal-URL einrichten und mindestens einen Tool-Call erfolgreich ausführen, inkl. Prüfung der OpenAI-Auth-Anforderungen (Task 4, Human-Runbook).
- Manuelle Validierung: Claude Web Connector-Versuch über Portal-URL, Ergebnis dokumentieren (Task 5, Human-Runbook).
- Dokumentation aktualisieren: `docs/project/operations/docker-operations.md` und `docs/project/operations/llm-client-setup.md` (Task 6, Agent-Task, basiert auf den Validation-Evidence-Einträgen aus Task 4/5).

### Nicht im Scope

- Kein SQLite-Token-Store, keine eigene Login-Seite, kein DCR-Code, keine PKCE-Validierung im eigenen Code (das übernimmt Cloudflare).
- Keine Lösung des Claude-Web-Bugs selbst – der liegt bei Anthropic und/oder Cloudflare und ist von hier aus nicht behebbar.
- Keine Migration von Claude Desktop/Codex CLI auf den neuen Portal-Weg – diese funktionieren bereits header-basiert und müssen nicht umgestellt werden.
- **Gemini-Validierung** – laut PRD v008 explizit als offene Frage zurückgestellt, kein Bestandteil dieser Plan-Version.
- **Leichtgewichtiger `TokenVerifier` (Defense-in-Depth)** – aus diesem MVP entfernt (siehe Notes and Trade-offs); die globale `mcp = FastMCP("altiplano")`-Instanz wird beim Modul-Import erzeugt, `auth_server_provider`/`token_verifier`/`auth` sind aber Konstruktor-only-Parameter von `FastMCP.__init__` – eine Nachrüstung in `main()` ohne Instanz-Neuanlage ist nicht möglich. Das wäre eine Architekturänderung an der Server-Initialisierung, kein kleiner Zusatz, und gehört in ein eigenes, separat geplantes Feature.

## Rollen und Berechtigungen

Vier unterschiedliche Identitäts-/Credential-Ebenen sind beteiligt und werden hier bewusst getrennt:

| Ebene | Was | Wer/Was nutzt sie |
|---|---|---|
| Cloudflare Access User | Login-Identität des Eigennutzers (z.B. One-Time-PIN am Identity Provider) | Mensch, beim erstmaligen Connector-Setup in ChatGPT/Claude Web |
| Portal Session / OAuth Token | Vom Cloudflare MCP Server Portal ausgestelltes OAuth-2.1-Token nach erfolgreichem Login | Web-LLM-Client (ChatGPT Web, Claude Web) bei jedem Tool-Call |
| Upstream Service Token | Bestehender Cloudflare-Access-Service-Token (`CF-Access-Client-Id`/`-Secret`) | Cloudflare-Portal-Infrastruktur, um Altiplano als Upstream zu erreichen (nicht der Endnutzer direkt) |
| Vikunja API Token | Bestehender `VIKUNJA_API_TOKEN` in Altiplanos Konfiguration | Altiplano-Server selbst, für alle ausgehenden Requests zu Vikunja |

**Explizite Sicherheitsannahme:** Da die Portal→Altiplano-Verbindung einen einzigen, gemeinsamen Upstream Service Token nutzt, teilen sich **alle** über das Portal angemeldeten Nutzer (bzw. alle deren Web-Clients) faktisch denselben Vikunja-API-Token im Altiplano-Server. Für das im PRD beschriebene Single-User-Modell (Eigennutzung, optional Partnerin in der Medium-Version über separate Assignee-Funktionalität, nicht über separate OAuth-Identitäten) ist das akzeptabel und entspricht der bestehenden Architektur. Es ist **kein** Multi-Tenant-Modell mit getrennten Vikunja-Zugängen pro Web-Client.

## Context References

### Pflichtlektüre vor Umsetzung

- `docs/project/prds/vikunja-mcp-server-v008.md` – Kapitel 6, 8, 9, 10, 12, 14, 16: aktuelle, PRD-offizielle Beschreibung des Cloudflare-Portal-Ansatzes inkl. Out-of-Scope-Klausel und dokumentierter Risiken.
- `docs/project/features/oauth-authentication/plan-v001.md` – Abschnitt „Offene Fragen" (Befunde 1–5) für die vollständige Recherche-Historie und den Grund des ursprünglichen Forks.
- `docs/project/features/oauth-authentication/plan-reviews/plan-v002-r01-review.md` – Vollständiges Review, dessen Punkte in diese Version integriert wurden.
- `docs/project/operations/docker-operations.md` – aktuelle Cloudflare-Access-Konfiguration (Service Token, Tunnel-Route), die als Basis für die Portal-Anbindung dient.
- `docs/project/operations/llm-client-setup.md` – aktuelle Client-Konfigurationen, insbesondere Abschnitte 2 (Claude Web) und 3 (ChatGPT Web), die durch den Portal-Workflow ersetzt/ergänzt werden.

### Relevante Dokumentation

- [Cloudflare MCP Server Portals](https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/) – Funktionsweise, Upstream-Authentifizierung via Custom Headers/Service Token, Code Mode, Tool-Kuration.
- [Cloudflare Zero Trust Free Plan](https://developers.cloudflare.com/cloudflare-one/account-limits/) – Bestätigung 50-Nutzer-Limit, dauerhaft kostenlos.
- [GitHub Issue #410 – claude.ai Web OAuth fails against Cloudflare Access Managed OAuth](https://github.com/anthropics/claude-ai-mcp/issues/410) – vollständiger Thread mit Root-Cause-Analyse (RFC 8707 `resource`-Parameter), Status `closed/not_planned`. **Hinweis:** Bei Umsetzung erneut nach aktuelleren, verwandten Issues suchen – das Review verweist auf möglicherweise weitere Fälle, ohne konkrete Nummern zu nennen.
- [OpenAI Apps SDK – Auth](https://developers.openai.com/apps-sdk/build/auth) – Bestätigung, dass ChatGPT den RFC-8707-`resource`-Parameter korrekt sendet; Referenz für Task 4 Acceptance Criteria.

## Codebase Intelligence

### Projektstruktur und Architektur

Für diesen Plan ändert sich an `src/altiplano/` **nichts**. Die gesamte Umsetzung erfolgt im Cloudflare-Dashboard und in `docs/project/operations/`.

### Patterns to Follow

- `_conf()` aus `server.py` (L55–56) – falls das zurückgestellte TokenVerifier-Future-Feature je aufgegriffen wird, als Pattern für ENV-Variablen-Zugriff relevant.
- Bestehendes Transport-Weichen-Pattern in `main()` (`server.py` L669–692): bleibt für diesen Plan unberührt.

### Anti-Patterns to Avoid

- Kein eigener Token-Store, keine eigene Client-Registrierung – das würde `plan-v001.md` wiederholen, dessen Komplexität hier bewusst vermieden wird.
- Keine Annahmen über exakte Cloudflare-Dashboard-Menüpfade ohne Live-Verifikation übernehmen (war der Kernfehler in `plan-v001.md` und ein zentraler Review-Punkt zu `plan-v002.md`).
- Keine unverifizierten Tatsachenbehauptungen aus Sekundärquellen (z.B. Review-Aussagen zu Cloudflare-Verhalten) ungeprüft als Fakt in Acceptance Criteria übernehmen – stattdessen als Verifikationsschritt modellieren (siehe Task 3, Code-Mode-Subtask).

### Dependency Analysis

Keine neuen Python-Dependencies. Kein Code-Task mehr in diesem Plan (Task 6 aus `plan-v002.md` entfernt).

## Architekturentscheidungen

### Gewählter Ansatz

**Cloudflare MCP Server Portal mit Managed OAuth als Authorization Server; Altiplano als reiner Resource Server.** Seit PRD v008 die offizielle, dokumentierte Strategie.

### Erwogene Alternativen

- **Eigener Authorization Server via nativer `mcp`-SDK-API** (`OAuthAuthorizationServerProvider`, siehe `plan-v001.md` Befund 2): Technisch möglich und korrekt dokumentiert, aber bewusst nicht gewählt – höherer sicherheitskritischer Wartungsaufwand, von beiden Ökosystemen (`mcp`-SDK-README, FastMCP-Doku) explizit nicht empfohlen. **Bleibt als Fallback in `plan-v001.md` dokumentiert.**
- **Drittanbieter-Package `fastmcp`:** Verworfen – widerspricht der nicht verhandelbaren Tech-Stack-Vorgabe (`mcp` offizielles SDK) und erfordert einen grösseren Refactor von `server.py` ohne fachlichen Mehrwert.

### Security, Performance, Maintainability

- **Security:** Geringere Angriffsfläche als Eigenbau, da kein selbstgeschriebener Token-Store/PKCE-Code. Risiko verschiebt sich auf Vertrauen in Cloudflares Open-Beta-Implementierung.
- **Risiken (explizit):**
  - **Open Beta**, kein GA-Status.
  - **Claude Web:** Bestätigter, ungelöster Bug (Issue #410, von Anthropic „not planned" geschlossen). Realistisches Risiko: Claude Web funktioniert beim Start dieses Features evtl. nicht.
  - **ChatGPT Web:** Kein bestätigter Bug, aber auch keine bestätigte Erfolgsmeldung – Validierung in Task 4 ist die erste echte Probe.
  - **Portal-Upstream-Authentifizierung:** Zentrale Architekturannahme (Custom Headers/Service Token gegen Access-geschützten Upstream) bisher nur aus Doku-Prosa abgeleitet, nicht selbst im Dashboard verifiziert – deshalb eigener Preflight-Task (Task 2).
  - **Code Mode:** Laut Review standardmässig aktiv bei Cloudflare MCP Server Portals; würde die erwartete direkte Tool-Sicht verändern. Von mir nicht selbst verifiziert – deshalb als Verifikationsschritt in Task 3 modelliert, nicht als vorab behauptete Tatsache.
- **Maintainability:** Deutlich weniger eigener Code als `plan-v001.md`; Wartungsaufwand verschiebt sich zu Cloudflare-Konfigurationspflege.

## Datenmodell und API-Mapping

Kein eigenes Datenmodell – Cloudflare verwaltet Clients, Tokens und Sessions selbst (siehe PRD v008, Kapitel 9: OAuth-Entitäten aus v007 entfernt).

## Betroffene Dateien

### Bestehende Dateien

- `docs/project/operations/docker-operations.md` – UPDATE: Abschnitt zur Cloudflare-Konfiguration um Managed-OAuth/Portal-Setup ergänzen.
- `docs/project/operations/llm-client-setup.md` – UPDATE: Abschnitte 2 (Claude Web) und 3 (ChatGPT Web) durch Portal-URL-Workflow ersetzen/ergänzen, inkl. dokumentiertem Claude-Web-Risiko.

### Neue Dateien

Keine.

## Implementation Plan

### Phase 1: Cloudflare-Konfiguration (manuell, Human-Runbook)

Access Application auf Managed OAuth umstellen, Preflight-Verifikation, MCP Server Portal anlegen, Altiplano als Upstream registrieren.

### Phase 2: Manuelle Validierung (Human-Runbook)

ChatGPT Web und Claude Web gegen die neue Portal-URL testen, Ergebnisse in Validation Evidence dokumentieren.

### Phase 3: Dokumentation (Agent-Task)

Operations-Guides aktualisieren, basierend auf den dokumentierten Validierungsergebnissen.

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Tasks 1–5 sind **Human-Runbook**-Tasks (manuelle Dashboard-/Client-Schritte, kein Agent-Self-Service) – ein `/execute`-Agent kann sie nicht eigenständig ausführen, sondern muss sie an dich übergeben und auf dokumentierte Evidence warten. Task 6 ist ein **Agent-Task**.

### Task 1: Cloudflare Access Application auf Managed OAuth umstellen

**Status:** planned
**Art:** Human-Runbook
**Ziel:** Die bestehende Access Application für `mcp-tasks.melbjo.win` so konfigurieren, dass sie als OAuth-2.1-Authorization-Server für MCP-Clients agiert.

**Vorbedingungen:** Zugriff auf das Cloudflare Zero Trust Dashboard mit Admin-Rechten für die bestehende Access Application.

**IMPLEMENT (manuell im Cloudflare Zero Trust Dashboard):**
1. Zero Trust Dashboard → Access → Applications → bestehende Application für `mcp-tasks.melbjo.win` öffnen.
2. Unter „Additional settings" die Option **„Managed OAuth"** aktivieren.
3. Bestehende Identity-Provider-Policy (z.B. One-Time-PIN) unverändert lassen – sie gilt weiterhin für den menschlichen Login-Schritt.
4. Bestehenden Service Token (aus Feature `cloudflare-service-token`) **nicht löschen** – er wird in Task 2 für die Portal→Altiplano-Verbindung weiterverwendet.

**GOTCHA:** Der exakte Menüpfad/Name der Einstellung wurde aus Cloudflare-Dokumentationstext abgeleitet, nicht selbst im Dashboard nachvollzogen (Stand der Planung). **Vor Umsetzung live im Dashboard verifizieren und Abweichungen hier nachtragen.**

**Mensch liefert:** Bestätigung, dass Managed OAuth aktiv ist; ggf. Korrektur des Menüpfads für die Plan-Dokumentation.
**Agent danach:** Trägt das Ergebnis in die Validation-Evidence-Tabelle ein.

**ACCEPTANCE CRITERIA:**
- [ ] Managed OAuth ist für die Application aktiv.
- [ ] Bestehender Service Token funktioniert weiterhin unverändert für Header-basierte Clients (Claude Desktop, Codex CLI) – keine Regression.

**VALIDATE:**
- Manuell: `curl -i -H "CF-Access-Client-Id: <id>" -H "CF-Access-Client-Secret: <secret>" https://mcp-tasks.melbjo.win/sse` liefert weiterhin `200 OK` (Regressionstest für bestehende Clients).

---

### Task 2: Preflight – Portal-Upstream-Authentifizierung verifizieren

**Status:** planned
**Art:** Human-Runbook (NEU in v003, adressiert Review-Punkt zur zentralen, bisher unbelegten Architekturannahme)
**Ziel:** Vor der eigentlichen Portal-Konfiguration klären, ob ein MCP Server Portal den Altiplano-Upstream tatsächlich über die bestehenden Service-Token-Credentials (Custom Headers) erreichen kann – oder ob ein anderer Mechanismus (z.B. OAuth Admin Credential) nötig ist.

**Vorbedingungen:** Task 1 abgeschlossen.

**IMPLEMENT (manuell im Cloudflare Zero Trust Dashboard):**
1. Zero Trust Dashboard → Access Controls → AI Controls → MCP Server Portals → Erstellungsdialog für ein neues Portal öffnen (noch nicht final anlegen).
2. Prüfen, welche Authentifizierungsoptionen für den Upstream-Server tatsächlich angeboten werden (z.B. „Custom Headers", „Service Token", „OAuth Admin Credential", „Bearer Token").
3. Dokumentieren, welche Option für einen via Cloudflare Access (Service Token Policy) geschützten Upstream wie Altiplano tatsächlich funktioniert.

**GOTCHA:** Falls „Custom Headers" nicht verfügbar ist oder nicht mit der bestehenden Access-Service-Token-Policy zusammenspielt: Task auf `needs_human` setzen, **nicht** improvisieren. Siehe „Entscheidungskriterien bei Fehlschlag".

**Mensch liefert:** Konkrete, im Dashboard bestätigte Antwort, welcher Authentifizierungsmechanismus für die Portal→Altiplano-Verbindung funktioniert.
**Agent danach:** Trägt das Ergebnis in Validation Evidence ein; passt bei Bedarf Task 3 an die tatsächlich verfügbare Option an.

**ACCEPTANCE CRITERIA:**
- [ ] Es ist eindeutig dokumentiert, mit welchem Mechanismus das Portal den Altiplano-Upstream authentifiziert erreicht.

**VALIDATE:**
- Manuell: Dashboard-Screenshot/Notiz der verfügbaren Upstream-Auth-Optionen als Validation Evidence.

---

### Task 3: MCP Server Portal anlegen und Altiplano als Upstream registrieren

**Status:** planned
**Art:** Human-Runbook
**Ziel:** Ein Cloudflare MCP Server Portal erstellen, das Altiplano über den in Task 2 bestätigten Mechanismus als Upstream-MCP-Server einbindet, mit bewusster Tool-Allowlist- und Code-Mode-Entscheidung.

**Vorbedingungen:** Task 2 abgeschlossen, Authentifizierungsmechanismus bestätigt.

**IMPLEMENT (manuell im Cloudflare Zero Trust Dashboard):**
1. Portal anlegen, Altiplano als Upstream-MCP-Server hinzufügen: direkte Upstream-URL (siehe „URL-Übersicht" #1).
2. Authentifizierung gemäss Task-2-Ergebnis konfigurieren.
3. **Tool-Allowlist:** Für die erste Validierung nur sichere Lesetools freigeben (`list_projects`, `list_tasks`, `get_task`, `list_labels`, `list_comments`). Schreib-/Delete-Tools (`create_task`, `update_task`, `delete_task`, `delete_comment`, `delete_bucket`, Attachment-Upload etc.) erst nach erfolgreicher Erstvalidierung bewusst freigeben.
4. **Code Mode prüfen:** Im Dashboard kontrollieren, ob „Code Mode" für dieses Portal aktiv ist. Falls ja: bewusst entscheiden, ob deaktiviert wird (damit Clients einzelne Tools direkt sehen) oder ob mit aktivem Code Mode validiert wird (dann Acceptance Criteria in Task 4/5 entsprechend anpassen).
5. Portal-Client-URL notieren (siehe „URL-Übersicht" #3, wird in Task 4/5 benötigt).

**GOTCHA:** Exakte UI-Bezeichnungen laut Cloudflare-Doku, nicht selbst verifiziert. Code-Mode-Standardverhalten ist eine Review-Aussage, von mir nicht selbst geprüft – hier live verifizieren, nicht als Tatsache übernehmen.

**Mensch liefert:** Portal-Client-URL, Bestätigung der Tool-Allowlist, dokumentierte Code-Mode-Entscheidung.
**Agent danach:** Trägt Ergebnisse in Validation Evidence ein; passt Task 4/5 Acceptance Criteria an, falls Code Mode aktiv bleibt.

**ACCEPTANCE CRITERIA:**
- [ ] Portal ist angelegt und zeigt Altiplano als verbundenen Upstream-Server.
- [ ] Tool-Allowlist ist auf sichere Lesetools beschränkt (Erstvalidierung).
- [ ] Code-Mode-Status ist geprüft und die Entscheidung (aktiv/deaktiviert) ist dokumentiert.
- [ ] Portal kann die Tool-Liste von Altiplano erfolgreich abrufen.

**VALIDATE:**
- Dashboard zeigt Status „Connected" / Tool-Liste für den registrierten Altiplano-Upstream.

---

### Task 4: ChatGPT Web Connector über Portal-URL einrichten und validieren

**Status:** planned
**Art:** Human-Runbook
**Ziel:** Nachweisen, dass ChatGPT Web sich ohne Header-Injection über das Portal verbinden und mindestens ein Tool erfolgreich aufrufen kann.

**Vorbedingungen:** Task 3 abgeschlossen, Portal-Client-URL vorhanden.

**IMPLEMENT (manuell):**
1. ChatGPT → Settings → Connectors → Developer Mode aktivieren.
2. Custom Connector mit der **Portal-Client-URL** (URL-Übersicht #3, **nicht** #1) anlegen, Authentication: OAuth (wird durch Cloudflare automatisch erkannt/angeboten).
3. Login-Flow durchlaufen (Cloudflare Access Login, z.B. One-Time-PIN).
4. Ein einfaches Tool aufrufen (z.B. `list_projects`) und Ergebnis prüfen.
5. Plausibilitätsprüfung gegen [OpenAI Apps SDK Auth-Doku](https://developers.openai.com/apps-sdk/build/auth): Falls der Flow fehlschlägt, prüfen, ob ein `invalid_target`/`resource`-Parameter-Fehler auftritt (Vergleich mit dem in Issue #410 dokumentierten Claude-Web-Fehlerbild).

**Mensch liefert:** Ergebnis des Connector-Versuchs (Erfolg/Fehlschlag), bei Fehlschlag das genaue Fehlerbild.
**Agent danach:** Trägt Ergebnis mit Datum in Validation Evidence ein.

**ACCEPTANCE CRITERIA:**
- [ ] ChatGPT Web zeigt die Altiplano-Tools nach erfolgreichem Login an (ggf. als Code-Mode-Tool, falls Task 3 das so entschieden hat).
- [ ] Mindestens ein Tool-Call liefert ein korrektes Ergebnis (z.B. echte Projektliste aus Vikunja).

**VALIDATE:**
- Manueller Test in ChatGPT Web, Ergebnis in Validation Evidence dokumentieren.

**Falls fehlschlägt:** Siehe „Entscheidungskriterien bei Fehlschlag".

---

### Task 5: Claude Web Connector-Versuch über Portal-URL (dokumentiertes Risiko)

**Status:** planned
**Art:** Human-Runbook
**Ziel:** Aktuellen Status von Claude Web gegen das Portal feststellen und dokumentieren – Erfolg wäre positiv überraschend, Fehlschlag ist der erwartete, dokumentierte Fall (Issue #410).

**Vorbedingungen:** Task 3 abgeschlossen, Portal-Client-URL vorhanden.

**IMPLEMENT (manuell):**
1. claude.ai → Settings → Integrations → Add Integration mit der **Portal-Client-URL**.
2. Login-Flow durchlaufen.
3. Ergebnis dokumentieren: Tools sichtbar? Tool-Call erfolgreich?
4. Falls bei der Umsetzung bereits weitere/aktuellere Issues zum selben Fehlerbild bekannt sind (über #410 hinaus), diese hier referenzieren.

**Mensch liefert:** Ergebnis (Erfolg/Fehlschlag) mit Datum.
**Agent danach:** Trägt Ergebnis in Validation Evidence ein; vergleicht Fehlerbild mit Issue #410.

**ACCEPTANCE CRITERIA:**
- [ ] Ergebnis (Erfolg oder Fehlschlag) ist in der Validation-Evidence-Tabelle dokumentiert, inkl. Datum (relevant, da der Bug zwischenzeitlich gefixt sein könnte).

**VALIDATE:**
- Falls Fehlschlag: Fehlerbild mit Issue #410 vergleichen (z.B. „Connector stays at 0 tools" oder Redirect-Loop). Falls abweichendes Fehlerbild: separat dokumentieren, ggf. neues Issue.
- Falls Erfolg: Issue #410 könnte zwischenzeitlich gefixt worden sein – in `plan-v001.md` Befund 4 nachtragen.

---

### Task 6: Operations-Dokumentation aktualisieren

**Status:** planned
**Art:** Agent-Task
**Ziel:** `docker-operations.md` und `llm-client-setup.md` um den neuen Portal-Workflow ergänzen – **erst nachdem** Task 4/5 echte Validation-Evidence-Einträge geliefert haben.

**Vorbedingungen:** Task 4 und Task 5 abgeschlossen (Status `done` oder `needs_human` mit dokumentiertem Ergebnis).

**IMPLEMENT:**
- `docker-operations.md`: Neuer Unterabschnitt „MCP Server Portal (Managed OAuth) für Web-Clients" nach dem bestehenden Cloudflare-Abschnitt, mit Verweis auf Task 1–3.
- `llm-client-setup.md`: Abschnitte 2 (Claude Web) und 3 (ChatGPT Web) überarbeiten:
  - ChatGPT Web: Portal-URL-Workflow als primäre Methode (ersetzt die bisherige „nicht direkt möglich"-Einschränkung) – **nur falls Task 4 erfolgreich war**.
  - Claude Web: Portal-URL-Workflow dokumentieren, aber mit explizitem Hinweis auf den bekannten Bug (Issue #410) gemäss Task-5-Ergebnis; Empfehlung, weiterhin Claude Desktop zu nutzen, falls Task 5 fehlschlug.

**GOTCHA:** Keine Doku-Behauptung schreiben, die nicht durch einen Validation-Evidence-Eintrag aus Task 4/5 gedeckt ist.

**ACCEPTANCE CRITERIA:**
- [ ] Beide Dateien spiegeln den tatsächlichen, in Task 4/5 validierten Stand wider (keine ungeprüften Behauptungen).

**VALIDATE:**
- Review: Dokumentation stimmt mit den Validation-Evidence-Einträgen aus Task 4/5 überein.
- `uv run pytest` (Regression, da reine Doku-Änderung – Safety Net, keine inhaltliche Prüfung).

## Validation Evidence

Wird während der Umsetzung befüllt. Zusätzliche optionale Quelle: Cloudflare Access/Gateway Logs im Dashboard (zeigen erfolgreiche/abgelehnte Requests gegen die Access Application).

| Task | Datum | Client/Tool | URL (# aus URL-Übersicht) | Ergebnis | Fehlerbild | Artefakt/Log |
|---|---|---|---|---|---|---|
| (auszufüllen) | | | | | | |

## Testing Strategy

### Unit / Integration Tests

- Kein neuer Python-Code in diesem Plan → keine neuen Unit-Tests erforderlich.
- `uv run pytest` muss nach Abschluss weiterhin vollständig grün bleiben (Regressionstest, da keine Code-Änderung erwartet wird).

### Regression Tests

- Bestehende Header-basierte Clients (Claude Desktop via `mcp-remote`, Codex CLI) müssen nach Task 1 weiterhin funktionieren (siehe Validate-Schritt in Task 1).

### Edge Cases

- Claude Web schlägt fehl (erwarteter Fall, siehe Task 5).
- Cloudflare-Portal-Synchronisation (laut Doku ca. alle 2h) zeigt Tools verzögert an – bei Tests ggf. manuellen Sync-Trigger im Dashboard suchen.
- Code Mode aktiv → Tool-Sicht in ChatGPT/Claude unterscheidet sich von der direkten Tool-Liste; Acceptance Criteria in Task 4/5 entsprechend lesen.

## Validation Commands

### Level 1: Regression

```bash
uv run pytest
```

### Level 2: Manuelle Validierung

1. Bestehender Service-Token-Zugriff (Regressionstest nach Task 1), URL #1:
   ```bash
   curl -i -H "CF-Access-Client-Id: <id>" -H "CF-Access-Client-Secret: <secret>" https://mcp-tasks.melbjo.win/sse
   ```
2. ChatGPT Web Connector-Test (Task 4), URL #3: Tool-Call `list_projects` über die UI ausführen.
3. Claude Web Connector-Test (Task 5), URL #3: Verbindungsversuch über die UI, Ergebnis dokumentieren.

## Acceptance Criteria

- [ ] ChatGPT Web kann sich über das Cloudflare MCP Server Portal verbinden und Tools nutzen, ohne dass der Nutzer HTTP-Header manuell konfiguriert.
- [ ] Falls der ChatGPT-Web-Flow fehlschlägt: Fehlerbild ist gegen die OpenAI-Auth-Doku (`resource`-Parameter, Redirect-URL) geprüft und dokumentiert.
- [ ] Claude-Web-Status (Erfolg oder Fehlschlag) ist dokumentiert, mit Bezug auf Issue #410.
- [ ] Bestehende Header-basierte Clients (Claude Desktop, Codex CLI) funktionieren unverändert weiter (keine Regression).
- [ ] Code-Mode-Verhalten ist geprüft und in den Acceptance Criteria von Task 4/5 korrekt berücksichtigt.
- [ ] `uv run pytest` bleibt grün.
- [ ] `docker-operations.md` und `llm-client-setup.md` spiegeln den validierten Stand wider.
- [ ] Gemini wird **nicht** validiert (PRD v008, offene Frage) – kein Acceptance-Kriterium für diese Plan-Version.

## Completion Checklist

- [ ] Tasks 1–6 sind umgesetzt und validiert (oder mit dokumentiertem `needs_human`-Ergebnis abgeschlossen).
- [ ] Validierungsergebnisse (insb. Task 4/5) sind mit Datum in Validation Evidence dokumentiert.
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt (insbesondere falls Claude Web entgegen Erwartung doch funktioniert oder ChatGPT Web entgegen Erwartung doch fehlschlägt).
- [ ] Feature ist bereit für `/document` und `/commit`.

## Documentation Notes

Nach Abschluss erstellt `/document`:
- **User Guide:** Wie verbindet man ChatGPT Web (und ggf. Claude Web) über das Cloudflare MCP Server Portal – inkl. dokumentiertem Claude-Web-Risiko.
- **Developer Notes:** Architektur-Entscheidung (Cloudflare als AS statt Eigenbau), Verweis auf `plan-v001.md` als Fallback-Referenz, Verweis auf PRD v008.
- **Operations Update:** `docker-operations.md` und `llm-client-setup.md` final abgleichen mit tatsächlichem Validierungsstand.

## Notes and Trade-offs

- **Hauptkompromiss:** Höheres Vertrauen in eine Open-Beta-Drittanbieter-Infrastruktur (Cloudflare), dafür praktisch kein eigener sicherheitskritischer Auth-Code – bewusst im Sinne von „Security vor Feature-Vollständigkeit" (PRD-Prinzip) gewählt.
- **Risiko Open Beta:** Das Feature kann sich ändern oder instabil sein. Falls dies während der Umsetzung zum Problem wird, ist `plan-v001.md` (korrigierte Eigenbau-Variante) der dokumentierte Fallback.
- **Claude Web bewusst nicht blockierend:** Der Plan gilt auch dann als erfolgreich abschliessbar, wenn nur ChatGPT Web funktioniert – Claude Web wird getestet und dokumentiert, ist aber kein Hard-Requirement für den Feature-Abschluss, da der Bug ausserhalb der Kontrolle dieses Projekts liegt.
- **Future Feature „TokenVerifier-Hardening":** Der in `plan-v002.md` enthaltene optionale Task 6 (leichtgewichtige JWT-Verifikation in `server.py` als Defense-in-Depth) wurde entfernt, weil die globale `mcp = FastMCP("altiplano")`-Instanz beim Modul-Import erzeugt wird und `auth_server_provider`/`token_verifier`/`auth` Konstruktor-only-Parameter sind (siehe `plan-v001.md` Befund 2 für die vollständige native-API-Dokumentation). Eine Nachrüstung wäre eine Architekturänderung an der Server-Initialisierung, kein kleiner Zusatz, und sollte – falls gewünscht – als eigenständiges, separat geplantes Feature mit eigenem Plan behandelt werden, nicht als Unterpunkt dieses Plans.

## Entscheidungskriterien bei Fehlschlag

- **ChatGPT Web funktioniert (Task 4) UND Claude Web schlägt fehl (Task 5, erwarteter Fall):** Feature gilt als erfolgreich abschliessbar; Claude-Web-Status bleibt dokumentiert, kein Blocker.
- **ChatGPT Web schlägt ebenfalls fehl (Task 4):** Task auf `needs_human`; Fehlerbild dokumentieren und mit Issue #410/RFC-8707-`resource`-Parameter vergleichen; Rückkehr zu `plan-v001.md` (native `mcp`-SDK-Eigenbau) als Fallback in Betracht ziehen.
- **Preflight (Task 2) zeigt, dass das Portal nicht über die bestehenden Service-Token-Credentials mit Altiplano sprechen kann:** Task auf `needs_human`; Plan-Abweichung dokumentieren, ggf. `/update-feature-plan` für eine alternative Portal-Konfiguration (z.B. OAuth Admin Credential statt Custom Headers) anstossen.
- **Cloudflare-Dashboard zeigt, dass „Managed OAuth" oder „MCP Server Portal" für den Free-Tier-Account doch nicht verfügbar ist:** Task 1 auf `needs_human`; sofortige Rückkehr zu `plan-v001.md` als einzig verbleibende Option prüfen.

## Offene Fragen

- Der exakte Cloudflare-Dashboard-Klickpfad (Menübezeichnungen, genaue Reihenfolge) wurde aus Dokumentationstext abgeleitet, nicht selbst nachvollzogen. Wird in Task 1–3 live verifiziert.
- Ob für die Portal→Altiplano-Verbindung tatsächlich „Custom Headers" zur Verfügung steht, ist die zentrale Frage von Task 2 (Preflight) – bewusst als eigener Task modelliert statt als stille Annahme.
- Ob „Code Mode" für dieses Portal standardmässig aktiv ist (Review-Aussage, von mir nicht selbst verifiziert), wird in Task 3 geprüft.
- Unklar, ob der Claude-Web-Bug (Issue #410) zum Zeitpunkt der tatsächlichen Umsetzung noch besteht und ob es zwischenzeitlich weitere, aktuellere verwandte Issues gibt – muss in Task 5 neu geprüft werden.
- Gemini-Validierung ist laut PRD v008 als offene Frage zurückgestellt; kein Bestandteil dieser Plan-Version.

## Plan Review Notes

**Review-Runde r01** (`plan-reviews/plan-v002-r01-review.md`) wurde vollständig integriert. Kernaussage des Reviews: Der Architektur-Pivot ist fachlich sinnvoll, der Plan war aber vor `/execute` noch nicht übergabereif – v003 adressiert alle als „Muss vor `/execute` geklärt werden" markierten Punkte:

- PRD-Abgleich → gelöst über `/update-prd` (PRD v008).
- Human-Runbook-Trennung → Tasks 1–5 explizit als manuelle Schritte mit Vorbedingungen/Mensch-liefert/Agent-danach modelliert.
- Preflight für Cloudflare-Annahme → neuer Task 2.
- URL-Vermischung → eigene „URL-Übersicht"-Sektion.
- Code Mode → Verifikationsschritt in Task 3 statt unverifizierter Annahme.
- Tool-Exposure/Allowlist → Bestandteil von Task 3.

„Sollte verbessert werden"-Punkte (Validation Evidence, OpenAI-Auth-Bindung, Fallback-Entscheidungskriterien) und Rollen/Berechtigungs-Präzisierung sind ebenfalls eingearbeitet. Der optionale TokenVerifier-Task wurde wie empfohlen aus dem MVP entfernt. Details und Begründungen je Punkt: siehe `plan-reviews/plan-v003-r01-integration.md`.

Eine weitere Review-Runde wird nicht als zwingend erforderlich eingeschätzt, da keine kritischen Punkte offen geblieben sind und keine grossen Plan-Abschnitte neu geschrieben (nur ergänzt/präzisiert) wurden. Die verbleibende Unsicherheit (Live-Dashboard-Verhalten) ist strukturell durch Human-Runbook-Tasks und `needs_human`-Pfade abgefangen, nicht durch weitere Planungsarbeit lösbar.
