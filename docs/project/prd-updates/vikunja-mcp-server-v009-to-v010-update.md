# PRD Update: vikunja-mcp-server v009 -> v010

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v009.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v010.md` |
| Ausgangsversion | `v009` |
| Zielversion | `v010` |
| Anlass | Neues Feature (Project Identifier) |
| Datum | 2026-06-29 |
| Auslöser | Menschlich angestossen |

## Kurzfazit

Das PRD wurde aktualisiert, um die Unterstützung für das `identifier`-Feld bei Projekten in die MCP-Server-Tools aufzunehmen (Teil des MVP-Scopes). Dadurch können Tasks in Zukunft sprechende Identifiers, wie z.B. `SHOP-12`, zugewiesen bekommen. Das Update erfasst die Tools `create_project` und `update_project`.

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| **1. Executive Summary** | Ergänzung, dass Projekte optional mit einem alphanumerischen Identifier versehen werden können. | Kurzbeschreibung muss das neue Feature (MVP) widerspiegeln. | Keine strukturellen Auswirkungen. |
| **2. Änderungshistorie** | Neuer Eintrag für `v010` (Project Identifier). | Versionierungshistorie pflegen. | Nachvollziehbarkeit. |
| **6. Scope (MVP)** | Hinzufügen von "Project Identifier in `create_project` / `update_project` (inklusive leeren des Identifiers)". | Feature ist eine Erweiterung bestehender Basis-Werkzeuge. | Tools müssen angepasst werden. |
| **7. User Stories** | Neue US-11 zum Setzen/Ändern des Identifiers. | Konkreter Anwendungsfall. | Grundlage für Tests und Validierung. |
| **8. Kernfunktionen** | "Projektverwaltung" um "inklusive Project Identifier" erweitert. | Vollständigkeit der Beschreibung. | Klarheit der Funktionalität. |
| **9. Datenmodell** | `identifier` zum Objekt `Project` hinzugefügt. | Datenmodell muss Vikunja-Realität abbilden. | Keine Auswirkung auf andere Felder. |
| **14. Risiken/Annahmen** | Annahme dokumentiert, dass Validierung (z.B. keine Leerzeichen) durch Vikunja-API erfolgt. | Doppelte Validierung vermeiden. | Fehler müssen aus der API transparent weitergereicht werden. |

## Änderungen in der neuen PRD-Version

- Versionsnummer auf `v010` angehoben und Änderungshistorie ergänzt.
- **Executive Summary:** Erwähnung des Project Identifiers.
- **Scope (MVP):** Punkt `[x] Project Identifier: Support in create_project und update_project (inklusive leeren des Identifiers).` hinzugefügt.
- **User Stories:** `US-11` ergänzt.
- **Kernfunktionen:** Bei der Projektverwaltung explizit auf den Project Identifier hingewiesen.
- **Daten und Statusmodell:** Das Feld `identifier` bei `Project` ergänzt.
- **Demo-Szenarien:** Hinweis hinzugefügt, dass `update_project` die anderen Felder nicht überschreiben darf.
- **Risiken/Annahmen:** Fehlervalidierung an Vikunja delegiert.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Nicht relevant, alle vom User eingebrachten Punkte wurden im PRD festgehalten.

## Offene Fragen und Annahmen

- Keine offenen Fragen. Die Annahme zur Validierungs-Delegation (an die Vikunja API) ist im PRD verankert.

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| Nicht relevant | nein | Es gibt derzeit keine laufenden Feature-Pläne, da gemäss `TASKS.md` alle bisherigen Features archiviert/fertiggestellt wurden. | Neues Feature via `/plan-feature` planen. |

## Empfehlung für den nächsten Schritt

Neue PRD-Version fachlich bestätigen und via Git committen. Danach kann der Feature-Plan für das Feature "Project Identifier" mithilfe von `/plan-feature Project Identifier` angelegt werden.
