# Feature Plan Update: Remote HTTP MCP v003 → v004

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangsplan | `docs/project/features/remote-http-mcp/plan-v003.md` |
| Neue Plan-Version | `docs/project/features/remote-http-mcp/plan-v004.md` |
| Ausgangsversion | v003 |
| Zielversion | v004 |
| Anlass | Abhängigkeits-Dokumentation: OAuth 2.1 Feature wird später Integration mit Remote-HTTP-Transport erfordern |
| Datum | 2026-06-25 |
| Auslöser | Menschlich angestossen – neues OAuth-Feature (oauth-authentication/plan-v001.md) erkannt |
| Bisherige PRD-Referenz | vikunja-mcp-server-v007.md (unverändert) |
| Neue PRD-Referenz | vikunja-mcp-server-v007.md (unverändert) |

## Kurzfazit

Der Remote-HTTP-MCP-Plan v003 wird unverändert in seinen Implementierungsdetails belassen. Eine neue "Feature-Abhängigkeiten"-Sektion dokumentiert jedoch, dass das zukünftige OAuth 2.1 Feature eine Integration mit der `main()`-Funktion in `server.py` erfordern wird. Der Plan markiert diese Abhängigkeit transparent, ohne die aktuelle Implementierung zu verändern. Der Feature-Status wird von `planned` (fehlend im v003) zu `done` korrigiert.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| **Feature-Status** | Korrektur: `done` statt `planned` | Alle 5 Tasks sind implementiert und validiert; Status war fehlerhaft | Klarheit über tatsächlichen Abschluss |
| **Feature Metadata** | Abhängigkeitshinweis: "OAuth 2.1 Feature (später, siehe 'Feature-Abhängigkeiten')" | Transparenz über zukünftige Arbeit | Keine Code-Änderung |
| **Neuer Abschnitt** | "Feature-Abhängigkeiten" mit Unterabschnitt "Abhängigkeit zum OAuth 2.1 Feature" | Dokumentation der Schnittstelle zwischen den Features ohne Code-Vermischung | Wartbarkeit, klare Abhängigkeits-Matrix |
| **Nicht im Scope** | Zusatz: "OAuth 2.1 Integration (siehe 'Feature-Abhängigkeiten')" | Explizit ausschliessen, dass OAuth in diesem Plan Scope hat | Klarheit über Grenzen |
| **Betroffene Dateien (bestehend)** | Hinweis in `server.py`: "Zukünftig: Wird um OAuth-Provider-Logik erweitert" | Warnung für zukünftige Maintainer, dass `main()` noch verändert wird | Risiko-Bewusstsein |
| **Offene Fragen** | Neuer Eintrag: "OAuth-Integration: Nach Abschluss des OAuth 2.1 Features..." | Explizite Nachverfolgung, dass Plan später überarbeitet werden muss | Tracking für Nacharbeit |
| **Completion Checklist** | Neuer Punkt: "Nach Abschluss des OAuth 2.1 Features: Remote HTTP MCP Plan überarbeiten..." | Explizites Reminder für Nacharbeit nach OAuth-Implementierung | Prozess-Sicherung |

## Änderungen in der neuen Plan-Version

- **Status-Korrektur:** `planned` → `done` (Abschnitt "Status").
- **Feature Metadata erweitert:** "Abhängigkeiten"-Feld ergänzt um OAuth-Hinweis.
- **Neue Sektion "Feature-Abhängigkeiten"** hinzugefügt (nach "Rollen und Berechtigungen", vor "Context References"):
  - Erklärt, warum OAuth eine Integration erfordert.
  - Nennt betroffene Dateien (`server.py`).
  - Unterstreicht: **Keine Code-Änderung jetzt.**
  - Markiert Nacharbeit als erforderlich.
- **"Nicht im Scope" erweitert:** "OAuth 2.1 Integration (siehe 'Feature-Abhängigkeiten')".
- **Task 1-Kommentar angepasst:** "Zukünftig: OAuth-Provider wird hier eingefügt" hinzugefügt.
- **Task 5 GOTCHA erweitert:** "Zukünftig: OAuth-Variablen müssen hinzugefügt werden".
- **"Offene Fragen" überarbeitet:** Konkrete Dokumentation der OAuth-Nacharbeit.
- **"Completion Checklist" ergänzt:** Nachverfolgungspunkt für OAuth-Integration.

## TASKS.md-Aktualisierung

- `Remote HTTP MCP` Eintrag: Pfad `plan-v003.md` → `plan-v004.md`.
- Status bleibt `done`.

## Nicht geänderte oder bewusst ausgesparte Punkte

- **Kein Code in Plan eingefügt:** OAuth-Logik bleibt im eigenen OAuth-Plan. Remote-HTTP-MCP-Plan referenziert nur, ohne zu implementieren.
- **Keine Task-Restrukturierung:** Die 5 bestehenden Tasks bleiben unverändert. Neue OAuth-Tasks gehören in den OAuth-Plan.
- **PRD-Referenz unverändert:** Das Feature basiert weiterhin auf vikunja-mcp-server-v007.md. Keine neue PRD-Abhängigkeit.
- **Implementierungsstatus:** Alle 5 Tasks bleiben `done`. Nacharbeit wird erst nach OAuth-Implementierung aktuell.

## Offene Fragen und Annahmen

- **Nacharbeits-Timing:** Nach Abschluss des OAuth 2.1 Features (geplant als separates Feature) wird dieser Remote-HTTP-MCP-Plan überarbeitet, um die Integration zu dokumentieren. Eine neue Plan-Version (wahrscheinlich v005) wird erforderlich.
  - **Nächster Klärungsschritt:** Nach Abschluss von oauth-authentication, eine neue Runde `/update-feature-plan docs/project/features/remote-http-mcp/plan-v004.md` durchführen.

## Review-Empfehlung

**Keine erneute `/review-feature-plan`-Runde erforderlich.** Die Änderungen sind reine Dokumentation von Abhängigkeiten. Keine Architektur-, Scope- oder Task-Änderungen. Die neue Plan-Version ist sofort nach menschlicher Bestätigung bereit für die Akten / für zukünftige Referenz.

## Empfehlung für den nächsten Schritt

1. **Plan-Version bestätigen:** Neue v004 ist dokumentiert und bereit.
2. **Commit:** Neue Plan-Version (`plan-v004.md`), Update-Datei (`plan-v003-to-v004-update.md`) und `TASKS.md` zusammen committen.
   - Commit-Nachricht: `docs(plan): add oauth dependency note to remote-http-mcp plan-v004`
3. **Weiterarbeit:** Starten Sie mit der Implementierung des OAuth 2.1 Features (`/execute docs/project/features/oauth-authentication/plan-v001.md`).
4. **Nacharbeit planen:** Nach Abschluss des OAuth-Features diesen Remote-HTTP-MCP-Plan erneut überarbeiten.

## Qualitätscheck vor Abschluss

- [x] Ausgangsplan (`plan-v003.md`), neue Plan-Version (`plan-v004.md`), Ausgangsversion (v003) und Zielversion (v004) sind korrekt dokumentiert.
- [x] Der Änderungsanlass ist klar beschrieben (OAuth-Abhängigkeit).
- [x] Die neue Plan-Version bleibt von der Ausgangsversion unterscheidbar (Status korrigiert, Features-Abhängigkeiten-Sektion, Nacharbeits-Hinweise).
- [x] Die Plan-Änderungshistorie im neuen Plan enthält einen Eintrag für v004 mit Datum, Anlass und Kurzbeschreibung.
- [x] PRD-Referenzen sind unverändert (vikunja-mcp-server-v007.md) und bewusst dokumentiert.
- [x] `TASKS.md` verweist auf die neue Plan-Version (plan-v004.md).
- [x] Tasks bleiben atomar, ausführbar und einzeln validierbar (keine Task-Änderungen).
- [x] Offene Fragen enthalten einen konkreten nächsten Klärungsschritt (OAuth-Integration nach Abschluss).
- [x] Die Empfehlung für den nächsten Schritt nennt Commit und Nacharbeit nach OAuth-Implementierung.
