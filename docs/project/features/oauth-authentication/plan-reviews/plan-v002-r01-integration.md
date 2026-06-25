# Feature Plan Review Integration: OAuth 2.1 Authentifizierung v002 Runde 01

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangsplan | `docs/project/features/oauth-authentication/plan-v002.md` |
| Neue Plan-Version | `docs/project/features/oauth-authentication/plan-v003.md` |
| Review | `docs/project/features/oauth-authentication/plan-reviews/plan-v002-r01-review.md` |
| Ausgangsversion | `v002` |
| Zielversion | `v003` |
| Review-Runde | `r01` |
| Integrationskontext | Autor-Session bestätigt |
| Aktualisierter TASKS.md-Eintrag | ja |

## Kurzfazit

Das Review bewertet den Architektur-Pivot (Cloudflare MCP Server Portal statt Eigenbau-OAuth) als fachlich sinnvoll, stuft `plan-v002.md` aber als noch nicht übergabereif für `/execute` ein. Die kritischsten Punkte waren: ein ungelöster PRD-Widerspruch, fehlende Trennung zwischen manuellen Dashboard-Schritten und Agent-Arbeit, eine zentrale, unbelegte Architekturannahme (Portal→Altiplano-Authentifizierung), vermischte URL-Rollen, ein unverifiziertes „Code Mode"-Verhalten, fehlende Tool-Kuration und ein technisch unpräziser optionaler Hardening-Task.

Alle als „Muss vor `/execute` geklärt werden" markierten Punkte wurden in `plan-v003.md` adressiert. Der PRD-Widerspruch wurde nicht im Plan selbst „weggeschrieben", sondern durch einen separaten `/update-prd`-Lauf aufgelöst (neue PRD-Version `v008`). Unverifizierte Tatsachenbehauptungen aus dem Review (Code Mode, weitere Issues neben #410) wurden bewusst **nicht** unkritisch als bestätigte Fakten übernommen, sondern als Verifikationsschritte im Plan modelliert – das entspricht der bereits in `plan-v001.md` gemachten Erfahrung, dass unverifizierte Annahmen die eigentliche Ursache der ursprünglichen Execute-Blockade waren.

Offen bleibt strukturell die Live-Verifikation im Cloudflare-Dashboard selbst (Preflight-Task, Code-Mode-Check) – das ist beabsichtigt nicht durch weitere Planung lösbar, sondern durch die jetzt vorhandenen Human-Runbook-Tasks mit `needs_human`-Eskalationspfaden abgefangen.

## Entscheidungen

| ID | Review-Punkt | Entscheidung | Begründung | Änderung in neuer Plan-Version |
|---|---|---|---|---|
| R-01 | PRD-Abgleich: Plan widerspricht PRD v007 (Eigenbau-OAuthProvider + SQLite, externer IdP explizit ausgeschlossen) | übernehmen | Verifiziert anhand PRD v007 Zeile 86 und Kapitel 8/9/10/12/16: echte, substantielle Abweichung | Gelöst über separaten `/update-prd`-Lauf → PRD `v008`; `plan-v003.md` referenziert PRD v008 explizit in Feature Description, Metadata und Pflichtlektüre |
| R-02 | Tasks 1–4 sind manuelle Dashboard-/Web-Client-Schritte, kein Agent-Self-Service | übernehmen | Trifft zu; `/execute`-Agent würde sofort blockieren | Tasks 1–5 als explizites Human-Runbook mit Feldern „Vorbedingungen", „Mensch liefert", „Agent danach" modelliert; nur Task 6 ist Agent-Task |
| R-03 | Cloudflare-Annahme „Portal→Altiplano via Custom Headers/Service Token" nicht ausreichend belegt | übernehmen | Zentrale Architekturannahme, nur aus Doku-Prosa abgeleitet, nicht selbst verifiziert | Neuer Task 2 „Preflight – Portal-Upstream-Authentifizierung verifizieren" vor dem eigentlichen Portal-Setup eingefügt |
| R-04 | Direkte Upstream-URL, Access-URL und Portal-Client-URL vermischt | übernehmen | Konkret, leicht behebbar, hohes Fehlerpotenzial sonst | Neue Sektion „URL-Übersicht" mit drei getrennten, nummerierten URLs; Tasks 4/5 verweisen explizit auf „URL #3" |
| R-05 | Code Mode bei Cloudflare-Portalen laut Review standardmässig aktiv | teilweise übernehmen | Plausible, aber von mir nicht selbst verifizierte Tatsachenbehauptung – wollte keine ungeprüfte Annahme übernehmen | Verifikations-Subtask in Task 3 („Code Mode prüfen") statt vorab behaupteter Tatsache; Acceptance Criteria in Task 4/5 entsprechend bedingt formuliert |
| R-06 | Keine Tool-Allowlist; Server enthält auch destruktive Tools | übernehmen | Passt zu PRD-Prinzip „Sicherheit vor Feature-Vollständigkeit" | Task 3 enthält jetzt expliziten Allowlist-Schritt (nur Lesetools für Erstvalidierung) |
| R-07 | Optionaler Task 6 (TokenVerifier) technisch unpräzise; globale `FastMCP`-Instanz beim Import erzeugt | übernehmen | Deckt sich mit eigener Quellcode-Prüfung von `FastMCP.__init__` (Auth-Parameter sind Konstruktor-only) | Task vollständig aus dem MVP entfernt; als Future-Feature-Hinweis in „Notes and Trade-offs" dokumentiert, mit Verweis auf `plan-v001.md` Befund 2 |
| R-08 | „Validation Evidence" wird referenziert, existiert aber nicht als Abschnitt | übernehmen | Konkrete Lücke | Neue Sektion „Validation Evidence" mit Tabellenstruktur (Task, Datum, Client, URL, Ergebnis, Fehlerbild, Artefakt) |
| R-09 | PRD nennt auch Gemini, Plan validiert nur ChatGPT/Claude | teilweise übernehmen | Berechtigt, aber keine eigene Gemini-Recherche vorhanden – keine Tasks erfinden | Über PRD-Update (v008) als „offene Frage, kein Scope-Entzug" dokumentiert; `plan-v003.md` übernimmt diesen Status 1:1 in Scope/Acceptance Criteria/Offene Fragen |
| R-10 | Claude-Web-Risiko sollte um weitere, verwandte Issues über #410 hinaus erweitert werden | teilweise übernehmen | Review nennt keine konkreten Issue-Nummern; kein Fabrizieren von Quellen | Hinweis in Pflichtlektüre und Task 5: bei Umsetzung erneut nach aktuellen Issues suchen, kein fabrizierter Link ergänzt |
| R-11 | ChatGPT-Validierung stärker an OpenAI-Auth-Anforderungen binden (`resource`-Parameter, Redirect-URL) | übernehmen | Deckt sich mit eigener Recherche (OpenAI Apps SDK Auth-Doku) aus der `plan-v002`-Erstellung | Task 4 enthält Plausibilitätsprüfung gegen die OpenAI-Doku; Acceptance Criteria erweitert; Doku als Pflichtlektüre ergänzt |
| R-12 | Fallback-Entscheidung sollte konkretisiert werden (wann zurück zu v001, wann pausieren) | übernehmen | Sinnvolle, leicht umsetzbare Klarstellung | Neue Sektion „Entscheidungskriterien bei Fehlschlag" mit vier konkreten Szenarien |
| R-13 | Rollen/Berechtigungen: Cloudflare-User vs. Portal-Session vs. Service-Token vs. Vikunja-Token unklar getrennt | übernehmen | Berechtigt; Single-User-Annahme sollte explizit stehen | Abschnitt „Rollen und Berechtigungen" komplett neu geschrieben mit Tabelle der vier Ebenen und expliziter Sicherheitsannahme |
| R-14 | Pflichtlektüre: PRD, Cloudflare-Doku-Abschnitte, OpenAI-Auth-Doku fehlen | übernehmen | Bereits recherchiert, nur nicht im Plan verlinkt gewesen | Context References um PRD v008, Review-Datei und OpenAI-Doku ergänzt |
| R-15 | Cloudflare Access/Gateway Logs als zusätzliche Evidence-Quelle (optional) | übernehmen (leicht) | Geringer Aufwand, echter Mehrwert | In „Validation Evidence" als optionale Zusatzquelle erwähnt |
| R-16 | `plan-v002` ist ein Fork nach Execute-Stopp, keine reguläre Review-Integration von `v001` | übernehmen (leicht) | Reine Begriffsklärung, keine inhaltliche Änderung | Hinweis in Plan-Änderungshistorie und im einleitenden Verhältnis-Hinweis von `plan-v003.md` ergänzt |

## Übernommene Änderungen an der neuen Plan-Version

- Neuer Task 2 „Preflight – Portal-Upstream-Authentifizierung verifizieren" eingefügt (vor dem bisherigen Portal-Setup-Task).
- Alle Tasks 1–5 explizit als Human-Runbook mit „Vorbedingungen"/„Mensch liefert"/„Agent danach" gekennzeichnet; Task 6 als Agent-Task.
- Neue Sektion „URL-Übersicht" mit drei getrennten, nummerierten URL-Rollen.
- Task 3 (Portal-Setup) um Tool-Allowlist-Schritt und Code-Mode-Verifikation erweitert.
- Optionaler Task 6 aus `plan-v002.md` (TokenVerifier) vollständig entfernt; als Future-Feature-Hinweis in „Notes and Trade-offs" dokumentiert.
- Neue Sektion „Validation Evidence" mit Tabellenstruktur.
- Neue Sektion „Entscheidungskriterien bei Fehlschlag" mit vier konkreten Szenarien.
- Abschnitt „Rollen und Berechtigungen" vollständig neu geschrieben (vier Identitäts-/Credential-Ebenen, explizite Sicherheitsannahme).
- Context References um PRD v008, die Review-Datei selbst und die OpenAI Apps SDK Auth-Doku ergänzt.
- Acceptance Criteria um OpenAI-Auth-Prüfung, Code-Mode-Bedingtheit und expliziten Gemini-Ausschluss erweitert.
- Neue Sektion „Plan Review Notes" mit Zusammenfassung der Review-Integration.

## Plan-Änderungshistorie

In `plan-v003.md` wurde folgende Zeile ergänzt:

> `v003 | 2026-06-25 | Review-Integration r01 | Review plan-v002-r01-review.md integriert: PRD-Abgleich über /update-prd aufgelöst (siehe vikunja-mcp-server-v008.md); Tasks in Human-Runbook (1–5) und Agent-Task (6) getrennt; Preflight-Task für Portal-Upstream-Authentifizierung ergänzt; drei URL-Rollen getrennt dokumentiert; Code-Mode- und Tool-Allowlist-Entscheidung als Verifikationsschritt ergänzt; Validation-Evidence-Abschnitt hinzugefügt; optionaler TokenVerifier-Task (v002 Task 6) aus dem MVP entfernt und als Future-Feature vermerkt; Rollen/Berechtigungen präzisiert; Pflichtlektüre erweitert.`

Zusätzlich wurde die bestehende `v002`-Zeile um einen klarstellenden Hinweis in der `v003`-Zeile ergänzt (R-16): `v002` entstand als Fork nach technischem Execute-Stopp aus `plan-v001.md`, nicht als reguläre Review-Integration.

## Teilweise übernommene Punkte

- **R-05 (Code Mode):** Die im Review als Tatsache formulierte Aussage „Code Mode standardmässig aktiv" wurde nicht ungeprüft übernommen, sondern als Live-Verifikationsschritt in Task 3 modelliert. Begründung: Ich habe diese Cloudflare-spezifische Detailaussage in dieser Session nicht selbst gegen die Cloudflare-Dokumentation verifiziert; eine zweite unverifizierte Tatsachenbehauptung in diesem Plan zu übernehmen widerspräche der Lektion aus `plan-v001.md`.
- **R-09 (Gemini):** Nicht als neuer Validierungs-Task umgesetzt, sondern als dokumentierte, PRD-seitig abgesegnete Out-of-Scope-Entscheidung (siehe PRD v008).
- **R-10 (weitere Claude-Web-Issues):** Kein zusätzlicher Issue-Link ergänzt, da das Review keine konkrete Issue-Nummer nennt und ich keine eigene Verifikation in dieser Session nachgeliefert habe. Stattdessen ein Re-Check-Hinweis für die Umsetzungszeit.

## Abgelehnte Punkte

Keine. Alle Review-Punkte wurden als sachlich begründet eingeschätzt; wo eine vollständige Übernahme nicht möglich war (siehe oben), wurde eine vorsichtigere, nicht-spekulative Alternative gewählt statt einer Ablehnung.

## Offene Punkte

- **Live-Verifikation Cloudflare-Dashboard (Task 1–3):** Exakte Menüpfade, Verfügbarkeit von „Custom Headers" als Upstream-Auth-Option und Code-Mode-Standardverhalten sind erst bei tatsächlicher Umsetzung klärbar. Nächster Klärungsschritt: `/execute plan-v003.md`, Tasks 1–3 als Human-Runbook durchlaufen.
- **Claude-Web-Aktualitätsstatus (Task 5):** Ob Issue #410 zum Umsetzungszeitpunkt noch besteht und ob es weitere relevante Issues gibt, ist offen. Nächster Klärungsschritt: erneute Recherche bei Task-5-Durchführung.
- **Gemini-Validierung:** Bewusst zurückgestellt (PRD v008). Nächster Klärungsschritt: Eigener Feature-Plan oder Plan-Update, falls Gemini-Unterstützung priorisiert wird.

## Empfehlung für den nächsten Schritt

Keine weitere Review-Runde erforderlich: Es sind keine kritischen Punkte offen geblieben, keine grossen Plan-Abschnitte wurden grundlegend neu geschrieben (nur ergänzt/präzisiert), und die verbleibende Unsicherheit ist strukturell durch Human-Runbook-Tasks mit `needs_human`-Eskalationspfaden abgefangen statt durch weitere Planung lösbar.

**Nächster Schritt:** `plan-v003.md` fachlich bestätigen, dann committen (zusammen mit PRD `v008`, der PRD-Update-Datei, `TASKS.md` und dieser Integration-Datei). Danach in einer neuen Session `/execute docs/project/features/oauth-authentication/plan-v003.md` starten.

## Qualitätscheck vor Abschluss

- [x] Ausgangsplan, Review-Datei, Ausgangsversion, Zielversion und Review-Runde sind korrekt dokumentiert.
- [x] Jede relevante Review-Empfehlung ist als übernommen, teilweise übernommen, abgelehnt oder offen dokumentiert.
- [x] Ablehnungen sind nachvollziehbar begründet (hier: keine Ablehnungen, aber Teil-Übernahmen begründet).
- [x] Die neue Plan-Version ist genannt und bleibt von der Ausgangsversion unterscheidbar.
- [x] Die Plan-Änderungshistorie der neuen Plan-Version enthält einen Eintrag für die Review-Integration.
- [x] `TASKS.md` zeigt auf die neue Plan-Version.
- [x] Offene Punkte enthalten einen konkreten nächsten Klärungsschritt.
- [x] Die Empfehlung für den nächsten Schritt nennt `/execute` mit dem neuen Plan-Pfad.
