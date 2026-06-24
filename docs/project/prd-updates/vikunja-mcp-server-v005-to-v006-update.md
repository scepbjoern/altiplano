# PRD Update: vikunja-mcp-server v005 -> v006

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v004.md` (Dateiname; Inhalt ist bereits "Dokumentversion v005", siehe Hinweis unten) |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v006.md` |
| Ausgangsversion | `v005` (inhaltlich, gemäss "Dokumentversion" im Ausgangs-PRD) |
| Zielversion | `v006` |
| Anlass | `Fehlerkorrektur / Widerspruch` (mit kleiner Scope-Ergänzung fehlender Felder) |
| Datum | `2026-06-24` |
| Auslöser | `Menschlich angestossen (Implementierungsplan "Fix: update_task Payload, Fehlende Felder in Projekt-Tools")` |

## Hinweis zur Versionierung

Der Commit `31eaf34` ("docs(optimistic-locking): add feature plan and update prd to v005") hat `vikunja-mcp-server-v004.md` direkt auf "Dokumentversion v005" angehoben, ohne eine neue Datei `v005.md` und ohne Update-Datei zu erzeugen — ein Abweichen vom `/update-prd`-Workflow. Diese Inkonsistenz (Dateiname `v004.md`, Inhalt `v005`) wurde für dieses Update nicht rückwirkend korrigiert, um die bestehende Commit-Historie nicht zu verändern. Die neue Version wird konsequent als `v006` fortgeführt. Eine spätere Bereinigung (`git mv` zu `v005.md`) ist optional und wurde dem Menschen zur Entscheidung überlassen.

## Kurzfazit

Eine Code-Analyse von `server.py` hat zwei zusammenhängende Probleme aufgedeckt: (1) `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` senden kein Pflichtfeld `title` im Update-Payload, was vermutlich zu einem Vikunja-Fehler `2002 title: non zero value required` führt, sobald nur andere Felder geändert werden — analog zu einem bereits in `update_project` gelösten Problem. (2) `list_projects` gibt `description` und `identifier` nicht zurück, und `create_project` bietet keinen `hex_color`-Parameter. Beide Punkte werden als neues Feature "Task- & Projekt-Tool-Fixes" in den MVP-Scope aufgenommen.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| Executive Summary | MVP-Ziel-Satz um vollständige Pflichtfeld-Payloads ergänzt | Sichtbarmachen des Fixes im Gesamtbild | Kleine Textänderung |
| Änderungshistorie | Eintrag `v006` ergänzt | Nachvollziehbarkeit | - |
| Scope (MVP) | Neuer Punkt "Tool-Payload-Korrektheit" sowie Ergänzung `description`/`identifier` (`list_projects`) und `hex_color` (`create_project`) | Schliesst dokumentierte Code-Lücke | MVP-Scope um Korrektheits-Fix erweitert |
| Out of Scope | Klarstellung ergänzt: `identifier` bleibt read-only, kein Eingabeparameter | Macht bereits getroffene Architekturentscheidung explizit | Keine Codeänderung, nur Dokumentation |
| User Stories | US-1 (Projektliste) und US-4 (Task pflegen) Erfolgskriterien erweitert | Decken die neuen Felder/den Bugfix ab | Kleine Ergänzung |
| Kernfunktionen | Hinweise bei "Projektverwaltung" und "Taskverwaltung" ergänzt | Dokumentiert den Fix | - |
| Risiken (Abschnitt 14) | Neuer Risiko-Eintrag zu fehlendem `title` bei Task-Updates; neue Zeile "Offene Frage" zu `is_archived` in `update_project` | Macht Annahmen und Folgerisiken sichtbar | - |
| Feature-Kandidaten (Abschnitt 15) | Neue Zeile "Task- & Projekt-Tool-Fixes", Priorität `1d` | Verlinkt neuen Feature-Plan | - |

## Änderungen in der neuen PRD-Version

- Executive Summary (v006) um Hinweis auf vollständige Pflichtfeld-Payloads bei Update-Tools ergänzt.
- Änderungshistorie um Eintrag zu v006 ergänzt.
- Scope und Ausbaustufen (MVP): Checkliste "Bereits implementiert" um die zwischenzeitlich fertiggestellten Punkte (`update_project`, `hex_color`-Rückgabe, Task-Sicherheits-Tools, Optimistic Locking) nachgeführt, die im Ausgangsdokument noch unter "Neu zu implementieren" standen; neuer Punkt "Tool-Payload-Korrektheit" sowie konkretisierte Punkte zu `list_projects`/`create_project` ergänzt.
- Out of Scope um Klarstellung zu `identifier` als read-only Feld ergänzt.
- US-1 Erfolgskriterium um `description`/`identifier` erweitert; US-4 um die Anforderung "kein Scheitern an fehlendem Pflichtfeld" ergänzt.
- Kernfunktionen "Projektverwaltung" und "Taskverwaltung" um konkretisierte Hinweise ergänzt.
- Abschnitt 14 (Risiken) um einen neuen Risiko-Eintrag zum fehlenden `title`-Feld bei Task-Updates und eine "Offene Frage" zu `is_archived` in `update_project` ergänzt.
- Feature-Kandidaten um "Task- & Projekt-Tool-Fixes" (Priorität 1d) ergänzt.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Die Korrektur für `is_archived` in `update_project` wurde **nicht** in den Scope dieses Fixes aufgenommen, sondern nur als offene Frage/Risiko dokumentiert (Abschnitt 14), da sie nicht Teil des eingereichten Implementierungsplans war und eine eigene Bestätigung benötigt.
- Die Dateiname/Inhalt-Inkonsistenz aus `v004.md` (siehe Hinweis oben) wurde nicht rückwirkend bereinigt.
- Andere MVP/Medium/Extended-Punkte wurden unverändert gelassen.

## Korrekturen gegenüber dem eingereichten Implementierungsplan

Beim Abgleich mit dem aktuellen Code in `src/altiplano/server.py` wurden zwei Punkte des eingereichten Plans präzisiert:

- `create_project` besitzt kein explizites Response-Mapping (reiner Passthrough der `PUT /projects`-Antwort) — `identifier` ist im Response bereits automatisch enthalten. Es fehlt tatsächlich nur der `hex_color`-Parameter.
- `update_project` ist bereits mit dem GET-Overlay-Pattern (inkl. vollständigem Basis-Payload) umgesetzt und gibt `identifier` ebenfalls bereits per Passthrough zurück. Die im Implementierungsplan offene Frage ("Soll `update_project` den `identifier`-Parameter erhalten?") ist damit durch den bestehenden Code bereits im empfohlenen Sinn (nein, nur Response) beantwortet — keine weitere Codeänderung nötig.

## Offene Fragen und Annahmen

- **Annahme (unbestätigt):** Vikunja verlangt `title` auch bei Task-Updates (`POST /tasks/{id}`) als Pflichtfeld, analog zu Projekten. Dies wurde noch nicht gegen die echte Vikunja-Instanz validiert. Nächster Klärungsschritt: manuelle Validierung während `/execute` des neuen Feature-Plans (z.B. `update_task` nur mit `description` gegen die echte Instanz aufrufen).
- **Offene Frage (nicht Teil dieses Fixes):** Sendet `update_project` `is_archived` nicht im Basis-Payload mit, könnte ein Update den Archivierungsstatus zurücksetzen, falls Vikunja Full-Replace-Semantik anwendet. Nächster Klärungsschritt: gegen echte Instanz prüfen und bei Bestätigung als eigenständigen Fix einplanen.
- **Versionierungs-Hinweis:** Soll die Datei `vikunja-mcp-server-v004.md` zur Konsistenz in `vikunja-mcp-server-v005.md` umbenannt werden? Aktuell unverändert gelassen (siehe Hinweis oben).

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/optimistic-locking/plan-v001.md` | ja | Hat das GET-Pattern für `updated` eingeführt, aber die `title`-Pflichtfeld-Lücke bei Task-Updates offen gelassen. | Informativ zur Kenntnis nehmen; keine automatische Änderung. Bei Bedarf `/update-feature-plan docs/project/features/optimistic-locking/plan-v001.md`. |
| `docs/project/features/task-security-tools/plan-v001.md` | ja | `complete_task` und `move_task_to_project` werden im neuen Feature-Plan erneut angepasst (Payload-Fix). | Informativ zur Kenntnis nehmen; keine automatische Änderung. Bei Bedarf `/update-feature-plan docs/project/features/task-security-tools/plan-v001.md`. |
| `docs/project/features/list-projects-hex-color/plan-v001.md` | ja | `list_projects` erhält zusätzliche Felder (`description`, `identifier`) über das, was dieser Plan ursprünglich abdeckte. | Informativ zur Kenntnis nehmen; keine automatische Änderung. Bei Bedarf `/update-feature-plan docs/project/features/list-projects-hex-color/plan-v001.md`. |
| `docs/project/features/update-project/plan-v001.md` | nein | Keine Codeänderung an `update_project`; die dort dokumentierte Architekturentscheidung zu `identifier` (read-only) wird durch diesen Fix nur bestätigt. | Kein Schritt nötig. |

Hinweis: Anstatt einen der obigen bestehenden Pläne zu aktualisieren, wurde auf expliziten Wunsch ein neuer, eigenständiger Feature-Plan erstellt: `docs/project/features/task-project-tool-fixes/plan-v001.md`. Dieser Plan überschneidet sich inhaltlich mit den oben gelisteten Plänen; sie sollten bei zukünftiger Arbeit an denselben Tools gemeinsam betrachtet werden.

## Empfehlung für den nächsten Schritt

Die neue PRD-Version v006 ist hiermit angelegt. Bitte fachlich bestätigen und gemeinsam mit dieser Update-Datei committen (`/commit`), bevor der neue Feature-Plan `docs/project/features/task-project-tool-fixes/plan-v001.md` in einer Umsetzungs-Session (`/execute`) verwendet wird.

## Qualitätscheck vor Abschluss

- [x] Ausgangs-PRD, neue PRD-Version, Ausgangsversion und Zielversion sind korrekt dokumentiert (inkl. Versionierungs-Inkonsistenz-Hinweis).
- [x] Der Änderungsanlass ist klar beschrieben.
- [x] Die neue PRD-Version bleibt von der Ausgangsversion unterscheidbar.
- [x] Die Änderungshistorie im neuen PRD enthält einen Eintrag für die neue Version.
- [x] Auswirkungen auf vorhandene Feature-Pläne wurden geprüft.
- [x] Betroffene Feature-Pläne wurden nicht automatisch geändert.
- [x] Offene Fragen enthalten einen konkreten nächsten Klärungsschritt.
- [x] Die Empfehlung für den nächsten Schritt nennt Commit und den neuen Feature-Plan.
