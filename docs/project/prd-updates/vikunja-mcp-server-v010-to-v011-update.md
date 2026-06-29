# PRD Update: vikunja-mcp-server v010 -> v011

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v010.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v011.md` |
| Ausgangsversion | `v010` |
| Zielversion | `v011` |
| Anlass | Neues Feature (Labels direkt beim `create_task`-Aufruf unterstützen) |
| Datum | 2026-06-29 |
| Auslöser | Menschlich angestossen |

## Kurzfazit

Das PRD wurde erweitert, um das direkte Zuweisen von Labels (`label_ids`) bereits bei der Erstellung von Aufgaben (`create_task`) im MVP-Scope zu fordern. Dies erspart dem MCP-Client nachträgliche, separate `add_label`-Aufrufe.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| **Metadaten / Historie** (Kap. 1 & 2) | Erhöhung auf `v011`. Eintrag in Änderungshistorie für Label-Support bei Task-Erstellung. | Standard-Vorgehen für neue PRD-Version. | Dokument bleibt aktuell. |
| **Scope / MVP** (Kap. 6) | Unter "MVP - Bereits im bestehenden Code implementiert" -> "Tasks" ergänzen: Labels (`label_ids`) beim Erstellen sofort anhängen. | Gehört funktional in den MVP-Scope der Task-Tools. | Erweitert die bestehende `create_task` Definition. |
| **User Stories** (Kap. 7) | Ergänzung/Anpassung von US-3: "Als Nutzer möchte ich gefiltert Tasks abrufen und erstellen (inklusive direkter Zuweisung von Labels)." | Reflektiert den direkten Nutzen durch Reduzierung von Tool-Aufrufen. | Klarer Demo-Bezug. |
| **Demo-Szenarien / Erfolgskriterien** (Kap. 13) | Erfolgskriterium ergänzen: `create_task` verarbeitet `label_ids`, erstellt die Aufgabe, hängt die Labels direkt an und gibt bei einem ungültigen Label einen klaren Teilfehler zurück. | Akzeptanzkriterien aus der Anforderung abbilden. | Sicherstellung der Teilfehler-Behandlung. |

## Änderungen in der neuen PRD-Version

- **Kapitel 1 & 2:** Versionsnummern aktualisiert, Historie nachgetragen.
- **Kapitel 6 (MVP-Scope):** Hinzugefügt, dass `create_task` nun die direkte Label-Zuweisung unterstützt.
- **Kapitel 7 (User Stories):** US-3 um das direkte Anhängen von Labels erweitert.
- **Kapitel 8 & 13:** Kernfunktionen und Demo-Szenarien um die Teilfehler-Rückgabe bei ungültigen Labels sowie den direkten Label-Support erweitert.
- **Kapitel 14 (Risiken/Annahmen):** Annahme dokumentiert, dass `create_task` intern erst den Task erstellt und dann Labels aufruft (sequentielle Vikunja-API Calls).
- **Kapitel 15 (Feature-Kandidaten):** Neues Feature "Labels in create_task" als Priorität 2 hinzugefügt.

## Nicht geänderte oder bewusst ausgesparte Punkte

- **`labels` Parameter (Textbasierte Labels):** Wir verzichten vorerst auf die textbasierte Zuweisung (`labels`: ["@online"]) zugunsten von `label_ids`, da dies weniger fehleranfällig ist (wie vom Nutzer empfohlen).

## Offene Fragen und Annahmen

- Keine kritischen offenen Fragen. Es wird angenommen, dass die Teilfehler-Behandlung sauber in der Python-Tool-Logik abgefangen werden kann (z.B. mittels `try-except` während der iterativen Label-Zuweisung nach der Task-Erstellung).

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/create-task-labels` (existiert noch nicht) | ja | Die Logik von `create_task` ändert sich. | /plan-feature `Labels in create_task` ausführen. |

## Empfehlung für den nächsten Schritt

Neue PRD-Version fachlich bestätigen, committen und danach mit `/plan-feature` den betroffenen Plan ("Labels in create_task") neu anlegen und umsetzen.
