# PRD Review: Vikunja MCP Server v001 Runde 01

## Metadaten

| Feld | Wert |
|---|---|
| PRD | `docs/project/prds/vikunja-mcp-server-v001.md` |
| Logische PRD-Version | `v001` |
| Review-Runde | `r01` |
| Reviewer-Kontext | Frische Session nach `/prime` bestätigt: ja |
| Vorherige Review-/Integration-Datei | Nicht relevant |

## Kurzfazit

Das PRD ist insgesamt solide aufgebaut und folgt dem Template-Aufbau konsequent. Die Aufteilung in MVP, Medium und Extended ist klar und nachvollziehbar. Besonders stark ist die explizite Sicherheitsstrategie (kein Delete im MVP) und die Brownfield-Einordnung, die den bestehenden Code respektiert und keinen unnötigen Rückbau vorsieht.

Die grössten Risiken für die spätere Feature-Planung liegen in drei Bereichen: Erstens fehlt dem PRD ein klarer Abschnitt zur Fehlerbehandlungsstrategie – wie sollen MCP-Tools mit API-Fehlern umgehen, die das LLM verwirren könnten? Zweitens sind einige MVP-Features (`complete_task`, `move_task_to_project`) funktional redundant oder unklar abgegrenzt gegenüber dem bestehenden `update_task`. Drittens fehlen im Datenmodell Felder, die der bestehende Code bereits verarbeitet (z.B. `identifier`, `is_archived`, `reminders`), was bei `/plan-feature` zu Rückfragen führen wird.

## Stärken

- Klare Trennung MVP / Medium / Extended mit nachvollziehbarer Priorisierung der Feature-Kandidaten.
- Sicherheitsstrategie (kein Delete im MVP, Token-Management über ENV) ist durchdacht und prototypengerecht.
- Brownfield-Kontext korrekt erfasst: Der bestehende Code wird beibehalten, nicht rückgebaut.
- User Stories und Demo-Szenarien sind aufeinander abgestimmt und verweisen korrekt auf die Ausbaustufen.
- Änderungshistorie ist vorhanden und korrekt für v001 angelegt.
- Feature-Kandidaten-Liste mit Priorisierung erleichtert die spätere `/plan-feature`-Reihenfolge.
- Das Starter-Kit-Nutzungs-Inventar ist vorhanden und korrekt ausgefüllt.

## Kritische Findings

Findings, die vor `/adapt-to-project` oder `/plan-feature` geklärt werden sollten.

| Bereich | Finding | Warum relevant | Konkreter Verbesserungsvorschlag |
|---|---|---|---|
| Scope / MVP | `complete_task` als dediziertes Tool ist funktional redundant zu `update_task(done=True)`. Die Begründung, warum ein separates Tool nötig ist, fehlt. | Ohne klare Abgrenzung entsteht bei `/plan-feature` Unsicherheit, ob `complete_task` ein Wrapper um `update_task` ist oder eigene Logik mitbringt. | Entweder begründen, welchen Mehrwert `complete_task` bietet (z.B. Validierung, dass der Task Pflichtfelder hat), oder es als Convenience-Alias deklarieren und die Erwartung klar dokumentieren. |
| Scope / MVP | `move_task_to_project` erfordert Klärung: Nutzt die Vikunja API ein dediziertes Move-Endpoint oder wird `project_id` über `update_task` geändert? | Die technische Machbarkeit beeinflusst, ob ein neues Tool erstellt wird oder ob `update_task` um `project_id` erweitert wird. | Vikunja-API-Dokumentation prüfen und im PRD festhalten, ob ein separater Endpoint existiert oder ob `POST /tasks/{id}` mit `project_id` im Body genügt. |
| Datenmodell | Das Datenmodell in Abschnitt 9 ist unvollständig gegenüber dem Code. Der Code gibt `identifier` (UI-sichtbare Nummer wie `#50`) und `is_archived` bei Projekten zurück. Reminders haben eine eigene Struktur (`[{reminder: ISO}]`). Diese fehlen im Datenmodell. | `/plan-feature` wird auf das Datenmodell im PRD referenzieren. Fehlende Felder führen zu Rückfragen oder zu einem Plan, der bestehende Funktionalität nicht berücksichtigt. | Abschnitt 9 um die Felder ergänzen, die der bestehende Code bereits verarbeitet: `identifier` und `is_archived` bei Project, `identifier` bei Task, Reminder-Struktur bei Task. |
| Fehlerbehandlung | Das PRD enthält keine Aussage zur Fehlerbehandlungsstrategie der MCP-Tools. Der Code nutzt `r.raise_for_status()`, aber es ist unklar, wie API-Fehler (401, 404, 500) dem LLM kommuniziert werden sollen. | LLMs reagieren unterschiedlich auf rohe HTTP-Fehlermeldungen vs. strukturierte Fehlerbeschreibungen. Ohne klare Strategie entstehen bei `/plan-feature` inkonsistente Fehlerausgaben. | Einen kurzen Absatz in Abschnitt 11 oder 5 ergänzen: Sollen API-Fehler als strukturierter Text (z.B. `{"error": "Task not found", "task_id": 123}`) oder als natürlichsprachliche Beschreibung zurückgegeben werden? |

## Unklare Anforderungen

| Abschnitt | Unklarheit | Rückfrage an den Menschen oder Autor-Agenten |
|---|---|---|
| Abschnitt 6, MVP | `hex_color` bei `list_projects` ergänzen – soll das nur ein zusätzliches Feld in der bestehenden Rückgabe sein, oder soll die gesamte Projektstruktur überarbeitet werden (z.B. auch `description` zurückgeben)? | Welche Felder soll `list_projects` im MVP zurückgeben? Nur `hex_color` ergänzen oder die Rückgabe generell erweitern? |
| Abschnitt 6, MVP | `update_project` – soll das Tool auch `is_archived` setzen können, um Projekte zu archivieren? | Ist Archivierung Teil des MVP oder Medium? |
| Abschnitt 10 | Die Vikunja-Instanz-URL ist als `https://tasks.melbjo.win/api/v1` konkret angegeben. Das ist eine persönliche Domain. | Soll die konkrete URL im PRD stehen oder durch einen Platzhalter ersetzt werden? Für ein Kurs-PRD könnte das als zu persönlich gelten. |
| Abschnitt 6, Medium | Bulk-Limits (max 5-10 Tasks) – auf welche Operationen beziehen sich diese? Nur auf Schreiboperationen oder auch auf Lesezugriffe mit grossen Ergebnismengen? | Welche konkreten Operationen sollen Bulk-Limits erhalten? |

## Fehlende Elemente gemäss PRD-Template

| Template-Bereich | Befund | Vorschlag |
|---|---|---|
| Abschnitt 16 (Appendix) | Fehlt komplett. | Optional, aber ein kurzer Appendix mit Link zur Vikunja-API-Dokumentation und der verwendeten Vikunja-Version (2.3.0) wäre hilfreich für `/plan-feature`. |
| Abschnitt 9 (Seed-/Demo-Daten) | Das Template empfiehlt, Seed- oder Demo-Daten zu beschreiben. Das PRD enthält keine Angaben dazu. | Da es sich um Produktivdaten handelt (persönliche Vikunja-Instanz), explizit festhalten: «Es werden echte Daten verwendet, keine Seed-Daten. Testszenarien arbeiten gegen die Produktivinstanz.» |
| Abschnitt 12 (Logging/Audit) | Security-Abschnitt erwähnt keine Logging-Strategie. | Kurz festhalten, ob der MCP-Server eigene Logs schreibt oder ob das bewusst weggelassen wird. Mindestens: «Keine eigene Logging-Strategie im MVP. Fehler werden über MCP-Protokoll an den Client weitergegeben.» |

## Versionierung und Änderungshistorie

Die Dokumentversion `v001` ist korrekt gesetzt. Die Änderungshistorie enthält einen nachvollziehbaren Eintrag für die initiale Erstellung mit Datum und Kurzbeschreibung. Das User-Feedback zur MVP/Medium-Aufteilung ist im Anlass dokumentiert. Keine Beanstandungen.

## Scope und Ausbaustufen

Die Trennung MVP / Medium / Extended / Out of Scope ist klar und konsistent. Die Checkboxen in Abschnitt 6 unterscheiden korrekt zwischen bereits implementierten (`[x]`) und noch zu implementierenden (`[ ]`) Funktionen. Das ist eine hilfreiche Transparenz gegenüber dem bestehenden Code.

Einziger Hinweis: Die Feature-Kandidaten-Tabelle (Abschnitt 15) enthält 8 Features, davon 3 im MVP. Das ist für ein MVP mit bereits funktionierendem Basiscode realistisch. Die Priorisierungsreihenfolge (erst `update_project`, dann Farbrückgabe, dann Task-Sicherheits-Tools) ist schlüssig, da `update_project` die Grundlage für das Demo-Szenario «Projekte aufräumen» bildet.

Scope-Risiko: Die Medium-Features (Kanban Buckets, Dateianhänge, Remote HTTP MCP) sind jeweils eigenständige, nicht triviale Erweiterungen. Insbesondere «Remote HTTP MCP» (Docker, Reverse Proxy, Auth) ist architektonisch signifikant. Das ist als Medium korrekt eingestuft, aber die Abhängigkeit von externer Infrastruktur (Docker, Reverse Proxy) sollte im Risiko-Abschnitt erwähnt werden.

## Rollen, Berechtigungen und Statuslogik

Das Rollenkonzept ist für den Anwendungsfall angemessen. Die Delegierung an die Vikunja-API-Token-Berechtigungen ist korrekt dokumentiert. Die dritte Rolle «Partnerin» ist sauber als Medium-Version eingestuft.

Es fehlt eine Aussage zu folgender Frage: Was passiert, wenn das API-Token weniger Berechtigungen hat, als die MCP-Tools voraussetzen? Beispiel: Wenn das Token kein Schreibrecht auf Projekte hat, schlägt `create_project` fehl. Das PRD sollte kurz festhalten, ob der Server zur Laufzeit prüfen soll, welche Berechtigungen das Token hat, oder ob Fehler einfach durchgereicht werden.

Statuslogik für Tasks: Das PRD verweist auf `done` als Status-Toggle, aber die Vikunja-API kennt auch granularere Statuswerte (z.B. `percent_done`). Für den MVP ist `done` ausreichend, aber es wäre hilfreich, explizit zu dokumentieren, dass `percent_done` und andere Status-Felder im MVP ignoriert werden.

## Datenmodell, Schnittstellen und Mocks

**Datenmodell:** Wie unter «Kritische Findings» beschrieben, ist das Datenmodell unvollständig gegenüber dem bestehenden Code. Zusätzlich fehlt das Objekt `Reminder` als eigene Entität oder Substruktur von Task. Der Code behandelt Reminders bereits (`set_reminders`), das Datenmodell erwähnt sie nicht.

**Schnittstellen:** Abschnitt 10 ist kompakt und korrekt. Die Angabe «echt (Produktivdaten)» beim MVP-Verhalten der Vikunja-Instanz ist transparent und wichtig.

**Mocks:** Keine Mocks vorgesehen, da gegen die echte Vikunja-API gearbeitet wird. Für Tests nutzt der Code pytest mit Mocks für die Vikunja-API (laut `AGENTS.md`). Das ist im PRD nicht explizit erwähnt, aber über die `AGENTS.md`-Referenz abgedeckt.

**Endpoint-Konventionen:** Das PRD erwähnt in Abschnitt 83 der README die ungewöhnlichen Vikunja-Endpoint-Konventionen (`PUT` für Create, `POST` für Update). Das PRD selbst hält diese Information nicht fest. Für `/plan-feature` wäre ein kurzer Hinweis auf diese Konvention hilfreich.

## Demo-Szenarien und Erfolgskriterien

Die Demo-Szenarien sind gut strukturiert und verweisen korrekt auf User Stories. Die Ausbaustufen-Zuordnung ist konsistent. Erfolgskriterien sind beobachtbar formuliert («Projekte haben danach saubere Namen und Farben in Vikunja»).

Verbesserungspotential: Die Erfolgskriterien sind qualitativ formuliert, aber nicht automatisiert prüfbar. Für `/plan-feature` wäre es hilfreich, pro Demo-Szenario mindestens einen konkreten Testfall zu skizzieren (z.B. «`list_projects` enthält ein Feld `hex_color` mit einem nicht-leeren Wert»).

## Starter-Kit-Nutzung und Adapt-to-Project

Der Abschnitt «Starter Kit Nutzung» ist vorhanden und enthält eine Bausteine-Tabelle mit drei Einträgen (FastMCP, httpx, pytest). Alle drei sind als «genutzt» markiert.

Die zweite Pflichtkomponente – «Demo-Inhalte, die für dieses Projekt nicht relevant sind» – ist vorhanden und korrekt beantwortet: «Keine. Der bestehende Basiscode [...] ist funktional wertvoll und wird vollständig beibehalten.» Das ist für den Brownfield-Kontext plausibel und `/adapt-to-project` kann damit arbeiten.

Einzige Präzisierung: Die Bausteine-Tabelle enthält nur drei Einträge. Das PRD-Template listet als Beispiel auch `set_reminders` und `list_labels` als mögliche Demo-Inhalte. Da das PRD explizit sagt, dass alles behalten wird, ist das konsistent. Für `/adapt-to-project` genügt diese Information.

## Prototypen-Grenzen und sensible Daten

Das PRD arbeitet mit echten Produktivdaten (persönliche Vikunja-Instanz). Das ist für einen persönlichen MCP-Server akzeptabel, da keine Drittpersonendaten betroffen sind (ausser bei der Medium-Version mit «Partnerin»).

Die konkrete Domain `tasks.melbjo.win` in Abschnitt 10 ist eine persönliche URL. Für ein Kurs-PRD könnte sie durch einen Platzhalter ersetzt werden. Das ist kein kritisches Problem, aber eine bewusste Entscheidung.

Token-Sicherheit ist korrekt adressiert: keine Secrets im Code, ENV-basierte Konfiguration, `chmod 600` empfohlen.

## Verbesserungsvorschläge nach Priorität

### Muss vor dem nächsten Schritt geklärt werden

- **Abgrenzung `complete_task` vs. `update_task(done=True)`:** Klären, ob `complete_task` eigene Logik mitbringt oder ein reiner Convenience-Wrapper ist. Ohne Klärung wird `/plan-feature` spekulieren müssen.
- **Technische Machbarkeit `move_task_to_project`:** Vikunja-API-Dokumentation prüfen, ob ein dedizierter Move-Endpoint existiert oder ob `project_id` über `update_task` geändert werden kann. Ergebnis im PRD festhalten.
- **Datenmodell vervollständigen:** Felder `identifier`, `is_archived`, Reminder-Struktur und `hex_color` (bei Label) ergänzen, damit `/plan-feature` auf einer konsistenten Datenbasis arbeitet.

### Sollte verbessert werden

- **Fehlerbehandlungsstrategie** kurz dokumentieren: Wie werden API-Fehler dem LLM kommuniziert?
- **Vikunja-Endpoint-Konventionen** (`PUT` für Create, `POST` für Update) im PRD oder einem referenzierten Abschnitt festhalten.
- **Logging-Strategie** im MVP kurz adressieren (auch wenn die Antwort «keine eigene Logging-Strategie» lautet).
- **Seed-/Demo-Daten-Aussage** ergänzen: Explizit festhalten, dass gegen Produktivdaten gearbeitet wird.
- **Risiko ergänzen:** Remote HTTP MCP (Medium) hat signifikante Infrastruktur-Abhängigkeiten (Docker, Reverse Proxy).

### Optional

- Appendix mit Link zur Vikunja-API-Dokumentation und Version hinzufügen.
- Erfolgskriterien um jeweils einen konkreten, automatisiert prüfbaren Testfall ergänzen.
- Konkrete Domain in Abschnitt 10 durch Platzhalter ersetzen (Datenschutzabwägung für Kurskontext).
- `percent_done` und weitere Task-Statusfelder explizit als «im MVP ignoriert» dokumentieren.

## Offene Fragen für die Integration

- Soll `complete_task` tatsächlich als separates MCP-Tool implementiert werden, oder genügt eine Ergänzung der `update_task`-Dokumentation für LLMs?
- Existiert in der Vikunja-API ein dedizierter Endpoint zum Verschieben von Tasks zwischen Projekten, oder wird `project_id` über den regulären Update-Endpoint geändert?
- Soll `list_projects` im MVP nur `hex_color` ergänzen oder die Rückgabe generell erweitern (z.B. auch `description`)?
- Ist die Archivierung von Projekten (`is_archived` setzen) Teil des MVP-Scopes von `update_project`?
- Soll die konkrete Instanz-URL `tasks.melbjo.win` im PRD bleiben oder durch einen Platzhalter ersetzt werden?

## Nächster Schritt

Gehe zurück in die Autor-Session, in der das PRD erstellt wurde. Führe dort aus:

```text
/integrate-prd-review docs/project/prds/vikunja-mcp-server-v001.md docs/project/prd-reviews/vikunja-mcp-server-v001-r01-review.md
```

## Qualitätscheck vor Abschluss

- [x] Das Review ändert das PRD nicht.
- [x] Kritische Findings sind konkret und handlungsorientiert.
- [x] Verbesserungsvorschläge sind so formuliert, dass `/integrate-prd-review` sie einzeln bewerten kann.
- [x] Dokumentversion und Änderungshistorie wurden geprüft.
- [x] MVP / Medium / Extended / Out of Scope wurden geprüft.
- [x] Rollen, Berechtigungen, Datenmodell, Schnittstellen, Demo-Szenarien und Starter-Kit-Nutzung wurden betrachtet.
- [x] Prototypen-Grenzen und sensible Daten wurden bewusst kurz geprüft oder als nicht relevant markiert.
- [x] Der nächste Schritt verweist zurück in die Autor-Session mit `/integrate-prd-review`.
