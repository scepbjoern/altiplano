# Feature Plan Review: OAuth 2.1 Authentifizierung via Cloudflare MCP Server Portal v002 Runde 01

## Metadaten

| Feld | Wert |
|---|---|
| Feature-Plan | `docs/project/features/oauth-authentication/plan-v002.md` |
| Logische Plan-Version | `v002` |
| Review-Runde | `r01` |
| Reviewer-Kontext | Frische Session nach `/prime` bestätigt: ja |
| Vorherige Review-/Integration-Datei | Nicht relevant |
| Referenziertes PRD | `docs/project/prds/vikunja-mcp-server-v007.md` |

## Kurzfazit

Der Plan trifft eine fachlich nachvollziehbare Architekturkorrektur: Altiplano soll nicht selbst Authorization Server werden, sondern Cloudflare soll den OAuth-Flow übernehmen. Das passt gut zur Projektleitplanke "Sicherheit vor Feature-Vollständigkeit" und vermeidet sicherheitskritischen Eigenbau-Code.

Vor `/execute` ist der Plan aber noch nicht übergabereif. Die wichtigsten Risiken liegen nicht im Python-Code, sondern in der Ausführbarkeit: Mehrere Tasks sind manuelle Cloudflare-/Web-Client-Schritte, die ein Execute-Agent nicht selbst erledigen kann; zudem sind zentrale Annahmen zur Portal-zu-Upstream-Authentifizierung, zur Portal-URL, zu Code Mode und zur Tool-Exponierung nicht präzise genug abgesichert.

Der Plan ist als Entscheidungsdokument stark, als ausführbarer PIV-Plan aber noch zu unscharf. Für eine nächste Version sollte er klar zwischen Human-Runbook, Agent-Dokumentationsarbeit und Stop-/Fallback-Entscheidungen trennen.

## Stärken

- Der Plan erkennt die technische Blockade aus `plan-v001.md` transparent und dokumentiert den Architektur-Pivot statt stillschweigend weiterzubauen.
- Der gewählte Ansatz reduziert eigenen Auth-Code und damit Security-Risiko deutlich.
- Bekannte Risiken zu Claude Web und Cloudflare Open Beta sind explizit benannt.
- Die bestehende headerbasierte Nutzung für Claude Desktop und Codex CLI bleibt bewusst erhalten.
- Die Dokumentationsziele sind realistisch auf `docs/project/operations/docker-operations.md` und `docs/project/operations/llm-client-setup.md` fokussiert.

## Kritische Findings

Findings, die vor `/execute` geklärt oder im Plan verbessert werden sollten.

| Bereich | Finding | Warum relevant | Konkreter Verbesserungsvorschlag |
|---|---|---|---|
| PRD-Abgleich | `plan-v002.md` weicht wesentlich von PRD v007 ab: Das PRD beschreibt FastMCP `OAuthProvider` plus SQLite-Token-Store und schliesst externe Identity Provider explizit aus; der Plan nutzt Cloudflare als Managed Authorization Server. | Ohne dokumentierte PRD-Abweichung arbeitet `/execute` gegen eine fachliche Grundlage, die den neuen Ansatz noch nicht trägt. | Vor `/execute` entweder `/update-prd docs/project/prds/vikunja-mcp-server-v007.md` ausführen oder im Plan eine explizit genehmigte PRD-Abweichung samt Begründung und betroffenen PRD-Kapiteln dokumentieren. |
| Ausführbarkeit | Tasks 1-4 sind manuelle Dashboard- und Web-Client-Schritte. Ein `/execute`-Agent kann sie nicht vollständig ausführen oder validieren. | Der Execute-Workflow soll taskweise umsetzen und Status aktualisieren. Hier würde er sofort auf menschliche Eingriffe warten. | Tasks 1-4 als `needs_human`-Runbook mit klaren Eingabe-/Ausgabe-Artefakten formulieren; Agent-Tasks erst danach starten, z.B. "Validation Evidence eintragen" und "Doku anhand bestätigter Ergebnisse aktualisieren". |
| Cloudflare-Annahme | Die Annahme "Portal -> Altiplano via Custom Headers / Service Token" ist im Plan zentral, aber nicht ausreichend belegt. Aktuelle Cloudflare-Doku beschreibt Portals, OAuth-upstream/Auth und Service-Token-Zugriff auf das Portal; sie bestätigt diese konkrete Upstream-Custom-Header-Konfiguration im Plan nicht eindeutig. | Wenn das Portal keine statischen `CF-Access-*` Header an den upstream Access-Endpunkt senden kann, scheitert die Architektur trotz richtiger OAuth-Idee. | Vor Task 2 einen Preflight-Task ergänzen: Cloudflare-Doku/Dashboard/API live verifizieren, ob ein Upstream-Server mit Admin Credential oder Custom Headers gegen eine Access-geschützte App konfiguriert werden kann. Bei Fehlschlag Plan auf `needs_human` und Fallback-Entscheid verlangen. |
| Endpoint-Details | Der Plan vermischt direkte Upstream-URLs (`/sse`, ggf. `/mcp`) und Portal-Client-URL. Cloudflare-Portals werden für Clients typischerweise über `https://<subdomain>.<domain>/mcp` genutzt. | Falsche URL in ChatGPT/Claude führt zu irreführenden OAuth- oder Transportfehlern. | Im Plan drei URLs getrennt dokumentieren: direkte Altiplano-Upstream-URL, Cloudflare Access Application URL und Portal-URL für LLM-Clients. Für Task 3/4 explizit die Portal-URL mit `/mcp` verwenden. |
| Code Mode | Cloudflare MCP Server Portals haben Code Mode aktuell standardmässig aktiv. Der Plan erwartet aber, dass ChatGPT Web die Altiplano-Tools direkt sieht und `list_projects` aufrufen kann. | Bei aktivem Code Mode sieht der Client nicht zwingend einzelne Upstream-Tools, sondern ein Code-Tool; Acceptance Criteria und Doku wären dann falsch. | Im Plan entscheiden: Code Mode deaktivieren für klassische Tool-Sicht oder bewusst mit Code Mode validieren. Acceptance Criteria und Doku entsprechend anpassen. |
| Tool-Exposure / Security | Der Plan fordert keine Portal-Tool-Kuration. Der bestehende Server enthält auch destruktive Tools wie `delete_task`, `delete_comment`, `delete_bucket` mit `confirm`, plus Attachment-Upload. | Web-Clients bekommen potentiell eine breitere Tool-Oberfläche als für den OAuth-Test nötig. Bei Managed Portals ist Tool-Auswahl ein Sicherheits- und UX-Hebel. | In Task 2 eine explizite Tool-Allowlist/Portal-Konfiguration ergänzen, mindestens für die erste Validierung nur sichere Lesetools wie `list_projects`/`list_tasks`; danach bewusst entscheiden, welche Schreib-/Delete-Tools freigegeben werden. |
| Optionaler TokenVerifier | Task 6 ist für diese Plan-Version zu unpräzise und wahrscheinlich nicht direkt umsetzbar: `mcp = FastMCP("altiplano")` wird global beim Import erzeugt; ein `token_verifier` kann nicht einfach im bestehenden `main()` nachgerüstet werden. Zusätzlich ist unklar, ob das Portal dem Upstream überhaupt ein Cloudflare-User-JWT als Bearer-Token liefert. | Als optionaler Task kann er trotzdem `/execute` verwirren und zu einem unnötigen Refactor führen. | Task 6 aus dem MVP-Plan entfernen oder als separates Future-Feature ausplanen. Falls behalten: vorher SDK-API, Portal-Header, benötigte JWT/JWKS-Library und FastMCP-Initialisierung konkretisieren. |
| Validation Evidence | Task 3/4 verweisen auf "Plan-Validation-Evidence", aber der Plan enthält keinen eigenen Evidence-Abschnitt mit Feldern für Datum, Portal-URL, Client, Ergebnis, Fehlerbild und Screenshots/Logs. | Spätere Dokumentation und `/document` brauchen nachvollziehbare Belege, besonders weil Cloudflare/Claude zeitabhängig sind. | Einen Abschnitt "Validation Evidence" mit Tabelle ergänzen und die Tasks so ändern, dass Ergebnisse dort eingetragen werden. |
| Scope | PRD v007 nennt ChatGPT Web, Claude Web und Gemini als Web-LLM-Clients. `plan-v002.md` validiert ChatGPT und Claude, aber nicht Gemini. | Das kann akzeptabel sein, muss aber als bewusste MVP-Einschränkung stehen. | Gemini entweder in den Scope/Validation aufnehmen oder explizit als "später, nicht Teil dieser Plan-Version" ausgrenzen und PRD-Abweichung dokumentieren. |

## Architektur und Codebase-Fit

Der MVP-Ansatz ohne Python-Code passt gut zur aktuellen Codebase: [server.py](/E:/bjoer/Documents/repos/altiplano/src/altiplano/server.py) ist ein schlanker FastMCP-Server mit globaler `mcp`-Instanz, Tool-Definitionen und Transport-Auswahl in `main()`. Keine Code-Änderung für Task 1-5 vermeidet unnötigen Refactor.

Der optionale Task 6 passt dagegen noch nicht sauber zur Codebase. Die bestehende globale FastMCP-Instanz wird beim Import erzeugt, während `token_verifier` und `AuthSettings` typischerweise beim Konstruktor gesetzt werden müssten. Das wäre keine kleine Ergänzung im `main()`-Block, sondern eine Architekturänderung an der Server-Initialisierung. Aus Reviewer-Sicht sollte Task 6 aus diesem Plan herausgelöst werden.

Cloudflare-Doku bestätigt den Grundansatz von MCP Server Portals: Clients verbinden sich zur Portal-URL, Cloudflare Access authentifiziert per OAuth und das Portal proxyt Tool-Aufrufe an Upstream-Server. Sie bestätigt auch, dass Portals Streamable HTTP und SSE upstream erkennen. Kritisch bleibt die konkrete Annahme, dass das Portal statische Cloudflare-Service-Token-Header zum upstream Access-Endpunkt senden kann.

## Scope und PRD-Abgleich

Der Plan erfüllt das Problem aus PRD v007 grundsätzlich: Web-LLM-Clients sollen ohne manuelle Header-Injection auf Altiplano zugreifen können. Er widerspricht aber der im PRD dokumentierten technischen Lösung. PRD v007 beschreibt einen selbstgebauten OAuth-Flow via FastMCP `OAuthProvider` und SQLite-Token-Store, während `plan-v002.md` Cloudflare als externen Authorization Server nutzt.

Dieser Widerspruch ist fachlich wahrscheinlich sinnvoll, aber noch nicht sauber integriert. Da `/plan-feature` bei PRD-Widersprüchen eigentlich stoppen oder eine PRD-Aktualisierung verlangen soll, sollte diese Plan-Version nicht direkt als autoritative Execute-Grundlage dienen, bevor der PRD-Pivot dokumentiert ist.

Nicht relevant sind Vikunja-Datenmodell und API-Mapping für Tasks/Projekte, weil das MVP des Plans keine Vikunja-Tool-Logik ändert.

## Versionierung und Plan-Änderungshistorie

Die Plan-Version `v002` ist klar benannt und die Änderungshistorie erklärt den Pivot. Positiv ist, dass `plan-v001.md` als Fallback erhalten bleibt.

Unsauber ist, dass `plan-v002.md` kein Review-/Integrationsergebnis aus `plan-v001` darstellt, sondern ein Fork nach einem Execute-Befund. Das ist nachvollziehbar, sollte aber stärker mit PIV-Begriffen abgegrenzt werden: `plan-v002` ist faktisch ein neuer Architekturplan nach technischem Stopp, nicht nur eine normale Review-Integration.

## Implementation Plan und Task-Qualität

Die grobe Reihenfolge ist richtig: Cloudflare konfigurieren, Portal verbinden, Web-Clients validieren, dann Doku aktualisieren. Die Task-Qualität leidet aber daran, dass manuelle und agentisch ausführbare Arbeit vermischt werden.

Task 1 und 2 brauchen menschlichen Dashboard-Zugriff und Secret-Werte. Task 3 und 4 brauchen ChatGPT-/Claude-Web-Zugriff und echte UI-Validierung. Ein Execute-Agent kann nur unterstützen, dokumentieren und auf Evidence prüfen. Deshalb sollten diese Tasks als Human Runbook mit klaren Statusübergängen modelliert werden.

Task 5 ist erst sinnvoll, wenn Task 3/4 echte Ergebnisse liefern. Der Plan sagt das bereits grob, sollte aber konkreter festlegen, dass keine Doku-Behauptung geschrieben wird, bevor die Evidence-Tabelle gefüllt ist.

Task 6 ist zu gross und optional zugleich. Optionalität in einem Execute-Plan ist riskant, wenn nicht klar ist, wer entscheidet, ob sie ausgeführt wird. Empfehlung: separat planen oder explizit "nicht ausführen in diesem Plan" markieren.

## Betroffene Dateien und Pflichtlektüre

Die betroffenen Dateien für das MVP sind korrekt gewählt:

- `docs/project/operations/docker-operations.md`
- `docs/project/operations/llm-client-setup.md`
- optional `src/altiplano/server.py`

Es fehlen als Pflichtlektüre bzw. konkrete Referenzen:

- PRD v007 als explizite fachliche Grundlage und Abweichungspunkt.
- Cloudflare-Dokuabschnitte zu Portal-URL, Code Mode, Tool-Kuration und upstream credentials.
- Aktuelle Anthropic Issues neben #410, insbesondere das weiterhin relevante Cloudflare-Managed-OAuth-Fehlerbild.
- OpenAI Apps SDK Auth-Doku zum `resource`-Parameter und zur ChatGPT Redirect URL.

## Datenmodell, Rollen und Berechtigungen

Kein eigenes Datenmodell ist im MVP korrekt. Rollen und Berechtigungen sind aber noch zu knapp: Es muss klarer unterschieden werden zwischen Cloudflare Access User, Portal Session, upstream Admin Credential/Service Token und Vikunja API Token im Altiplano-Server.

Besonders wichtig: Wenn das Portal mit einem Admin Credential zum upstream Altiplano verbindet, nutzen alle Portal-User faktisch denselben Vikunja-API-Token im Server. Für Single-User ist das akzeptabel, sollte aber im Plan explizit als Rollenmodell und Security-Annahme stehen.

## Testing und Validierung

`uv run pytest` als Regression ist sinnvoll, aber nicht ausreichend und bei reinen Doku-/Dashboard-Änderungen eher ein Baseline-Check.

Die wichtigsten Validierungen sind manuell und brauchen genaue Evidence:

- Direkter headerbasierter Zugriff auf Altiplano bleibt möglich.
- Portal kann die Upstream-Tools abrufen.
- ChatGPT verbindet über die Portal-URL und kann mindestens einen ungefährlichen Tool-Call ausführen.
- Claude-Web-Ergebnis ist mit Datum und Fehlerbild dokumentiert.
- Falls Code Mode aktiv bleibt, wird validiert, ob das erwartete Tool-Modell trotzdem für ChatGPT/Claude passt.

Eine zusätzliche automatisierte Prüfung wäre hilfreich: vor und nach den Doku-Änderungen `uv run pytest` ausführen, damit die Review-/Dokuphase keine unerwartete Codeänderung versteckt. Da der Plan selbst keinen Code ändert, ist das eher ein Safety Net.

## Risiken, Gotchas und Edge Cases

Gut abgedeckt sind Open-Beta-Risiko, Claude-Web-Risiko und Cloudflare-Dashboard-Pfad-Unsicherheit.

Nicht ausreichend abgedeckt sind:

- Portal-URL vs upstream URL.
- Code Mode default.
- Tool-Kuration und destruktive Tools.
- Wie lange die Portal-Tool-Synchronisation dauern darf und wann ein manueller Sync oder Retry nötig ist.
- Was genau passiert, wenn ChatGPT fehlschlägt: Fallback zu `plan-v001`, Plan-Update, PRD-Update oder Feature-Abbruch?
- Ob bestehende Access Policies durch Managed OAuth verändert werden und ob Service-Token-Zugriff danach weiterhin funktioniert.

## Übergabereife für Execute

Noch nicht übergabereif. Ein frischer `/execute`-Agent kann den Plan lesen und verstehen, aber nicht ohne menschliche Dashboard-/Client-Aktionen ausführen. Er müsste sofort stoppen oder Tasks auf `needs_human` setzen.

Mit den oben genannten Anpassungen kann der Plan sehr gut ausführbar werden: Human-Schritte als Runbook, Evidence-Abschnitt, klare Portal-/Endpoint-Details, Code-Mode-Entscheid und Tool-Allowlist.

## Verbesserungsvorschläge nach Priorität

### Muss vor `/execute` geklärt werden

- PRD-Pivot dokumentieren: `/update-prd` oder explizit genehmigte Plan-Abweichung.
- Plan in Human-Runbook-Tasks und Agent-Tasks trennen; Task 1-4 nicht als rein agentisch ausführbar behandeln.
- Upstream-Authentifizierung des Portals gegen den Cloudflare-Access-geschützten Altiplano-Endpunkt verifizieren.
- Portal-URL, Upstream-URL und direkte Access-URL getrennt dokumentieren.
- Code Mode bewusst deaktivieren oder als gewähltes Verhalten in Validation und Doku aufnehmen.
- Tool-Exposure/Allowlist für die erste Web-Client-Validierung festlegen.

### Sollte verbessert werden

- `Validation Evidence`-Abschnitt mit Datum, Client, URL, Ergebnis, Fehlerbild, Artefakt/Log ergänzen.
- Claude-Web-Risiko um aktuelle verwandte Issues erweitern, damit nicht nur #410 als einzelner Beleg wirkt.
- ChatGPT-Validation stärker an OpenAI Auth-Anforderungen binden: `resource`-Parameter, Redirect URL, DCR/CIMD-Verhalten.
- Fallback-Entscheidung konkretisieren: Wann zurück zu `plan-v001`, wann neues `plan-v003`, wann Feature pausieren?

### Optional

- Gemini bewusst ausklammern oder als späteren Validierungstask planen.
- Cloudflare Gateway/Access Logs als zusätzliche Validierungsquelle aufnehmen.
- Task 6 als eigenes Hardening-Feature planen, sobald Portal-Header und FastMCP-Auth-Initialisierung geklärt sind.

## Offene Fragen für die Integration

- Soll der Cloudflare-Portal-Ansatz zuerst im PRD verankert werden, bevor dieser Plan als Execute-Grundlage gilt?
- Soll Code Mode für Altiplano deaktiviert werden, damit ChatGPT/Claude die bisherigen MCP-Tools direkt sehen?
- Welche Tools sollen im Portal initial freigegeben werden: nur Lesetools für den ersten Test oder direkt alle Tools?
- Kann das Cloudflare Portal den upstream Altiplano-Endpunkt mit `CF-Access-Client-Id` und `CF-Access-Client-Secret` erreichen, oder braucht es eine andere Access-/Portal-Architektur?
- Ist ChatGPT Web allein ein ausreichendes Erfolgskriterium für dieses Feature, oder muss Gemini ebenfalls aus PRD-Sicht geprüft werden?
- Soll Task 6 komplett in ein separates Feature verschoben werden?

## Nächster Schritt

Gehe zurück in die Autor-Session, in der der Feature-Plan erstellt wurde. Führe dort aus:

```text
/integrate-feature-plan-review docs/project/features/oauth-authentication/plan-v002.md docs/project/features/oauth-authentication/plan-reviews/plan-v002-r01-review.md
```

## Qualitätscheck vor Abschluss

- [x] Das Review ändert den Feature-Plan nicht.
- [x] Kritische Findings sind konkret und handlungsorientiert.
- [x] Architektur, Task-Reihenfolge, betroffene Dateien, Tests und Validierung wurden geprüft.
- [x] PRD-Abgleich und Scope-Grenzen wurden betrachtet.
- [x] Plan-Version und Plan-Änderungshistorie wurden geprüft.
- [x] Verbesserungsvorschläge sind so formuliert, dass `/integrate-feature-plan-review` sie einzeln bewerten kann.
- [x] Der nächste Schritt verweist zurück in die Autor-Session mit `/integrate-feature-plan-review`.
