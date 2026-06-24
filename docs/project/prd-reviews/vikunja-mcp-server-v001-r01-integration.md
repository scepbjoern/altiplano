# PRD Review Integration: vikunja-mcp-server v001 Runde r01

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v001.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v002.md` |
| Review | `docs/project/prd-reviews/vikunja-mcp-server-v001-r01-review.md` |
| Ausgangsversion | `v001` |
| Zielversion | `v002` |
| Review-Runde | `r01` |
| Integrationskontext | Autor-Session bestätigt |

## Kurzfazit

Das PRD wurde in Version v002 geschärft. Insbesondere das Datenmodell wurde an den bestehenden Basiscode angepasst (Felder wie `identifier`, `is_archived`, `reminders`). Die Fehlerbehandlungsstrategie und Logging-Vorgaben wurden definiert. Die Abgrenzung der Sicherheits-Tools (`complete_task` als Convenience-Wrapper) wurde präzisiert. Archivierung von Projekten wurde durch den Autor explizit vom MVP ausgeschlossen.

## Entscheidungen

| ID | Review-Punkt | Entscheidung | Begründung | Änderung in neuer PRD-Version |
|---|---|---|---|---|
| R-01 | Abgrenzung `complete_task` zu `update_task(done=True)` klären | übernehmen | Ein dediziertes Tool hilft der KI bei der Intent-Erkennung und dient als sicherer Wrapper. | Klarstellung in Abs. 8 und 15. |
| R-02 | Machbarkeit `move_task_to_project` klären | übernehmen | Wichtig für Implementierung (POST vs dedizierter Move-Endpoint). | In Abs. 14 als Annahme/Risiko ergänzt. |
| R-03 | Datenmodell unvollständig | übernehmen | Der bestehende Basiscode nutzt Felder wie `identifier` und `reminders` bereits. | Abs. 9 um die Felder erweitert. |
| R-04 | Fehlerbehandlungsstrategie fehlt | übernehmen | Wichtig, damit LLMs auf Fehler reagieren können statt abzustürzen. | Ergänzung in Abs. 12 (strukturierte Fehlertexte). |
| R-05 | `list_projects` Rückgabe um `description` erweitern? | teilweise übernehmen | Wir ergänzen primär die Farbe, belassen die Rückgabe aber schlank, um Kontext-Token zu sparen. | Präzisierung in Abs. 6. |
| R-06 | Soll `update_project` archivieren (`is_archived`) können? | ablehnen | Vom User explizit für das MVP abgelehnt. | Expliziter Ausschluss im Scope (Abs. 6). |
| R-07 | Echte Domain anonymisieren? | ablehnen | Lokaler Server für Eigennutzung, echte Domain ist sicher und gewünscht. | Keine Änderung in Abs. 10. |
| R-08 | Bulk-Limits präzisieren | übernehmen | Limits ergeben nur bei Schreib-Aktionen Sinn, nicht bei Lesevorgängen. | Klarstellung in Abs. 6 (Medium-Version). |
| R-09 | Appendix, Demo-Daten, Logging, Infrastruktur-Risiko, Token-Rechte. | übernehmen | Wertvolle qualitative Ergänzungen für den PIV-Prozess. | In Abs. 10, 12, 14 und 16 eingearbeitet. |

## Übernommene Änderungen an der neuen PRD-Version

- **Abschnitt 6:** Bulk-Limits präzisiert (nur Schreib-Aktionen).
- **Abschnitt 8 / 15:** Zweck von `complete_task` und Machbarkeitsprüfung für `move_task_to_project` geklärt.
- **Abschnitt 9:** Datenmodell um Felder wie `identifier`, `is_archived`, `reminders` ergänzt. Hinweis ergänzt, dass mit echten Produktivdaten getestet wird.
- **Abschnitt 12:** Fehlerbehandlungsstrategie hinzugefügt (API-Fehler als strukturierte Rückgabe ans LLM abfangen), Logging- und Token-Rechte dokumentiert.
- **Abschnitt 14:** Risiken bzgl. Infrastruktur für HTTP Remote MCP und Annahmen bzgl. der Vikunja-API (`move_task`) ergänzt.
- **Abschnitt 16:** Neuer Appendix erstellt mit Verweis auf Vikunja-Version und Endpoint-Konventionen (z. B. PUT vs. POST).

## Änderungshistorie im PRD

Folgender Eintrag wurde hinzugefügt:
`| v002 | 2026-06-24 | Review Integration | Erkenntnisse aus r01 eingearbeitet (Datenmodell, Fehlerbehandlung, Tool-Abgrenzung) |`

## Teilweise übernommene Punkte

- `list_projects` Ergänzungen (R-05): Wir beschränken uns im MVP auf die Rückgabe von `hex_color` und fügen keine unnötigen Textfelder wie `description` in die Standard-Liste ein.

## Abgelehnte Punkte

- Archivierung via `update_project` (R-06): Wurde vom Anwender verworfen und wird im MVP nicht umgesetzt.
- Domain anonymisieren (R-07): Die echte Domain bleibt erhalten, da Eigennutzung.

## Offene Punkte

- Nicht relevant. Alle angesprochenen Punkte konnten durch den Autor in dieser Session geklärt werden.

## Empfehlung für den nächsten Schritt

Das PRD v002 ist fachlich bestätigt und bereit zur Umsetzung. Der nächste Schritt ist der Commit von `v002` und dieser Integrationsdatei. Anschliessend kann zur Bereinigung `/adapt-to-project docs/project/prds/vikunja-mcp-server-v002.md` aufgerufen werden.

## Qualitätscheck vor Abschluss

- [x] Ausgangs-PRD, Review-Datei, Ausgangsversion, Zielversion und Review-Runde sind korrekt dokumentiert.
- [x] Jede relevante Review-Empfehlung ist als übernommen, teilweise übernommen, abgelehnt oder offen dokumentiert.
- [x] Ablehnungen sind nachvollziehbar begründet, insbesondere wenn Autor-Session-Kontext eine Rolle spielt.
- [x] Die neue PRD-Version ist genannt und bleibt von der Ausgangsversion unterscheidbar.
- [x] Die Änderungshistorie der neue PRD-Version enthält einen Eintrag für die Review-Integration.
- [x] Offene Punkte enthalten einen konkreten nächsten Klärungsschritt.
- [x] Die Empfehlung für den nächsten Schritt nennt `/adapt-to-project`.
