# Developer Notes: Project Identifier

## Überblick

Dieses Feature ermöglicht das Setzen und Aktualisieren des `identifier` Feldes für Vikunja-Projekte. Der Project Identifier ist ein kurzes Kürzel, mit dem Vikunja automatisch lesbare und eindeutige IDs für Tasks dieses Projekts (z. B. `KÜRZEL-1`) generiert.

## Referenzen

- Plan: [plan-v001.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/project-identifier/plan-v001.md)
- PRD: [vikunja-mcp-server-v010.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/prds/vikunja-mcp-server-v010.md)
- Relevante Guides: `Nicht relevant`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| [server.py](file:///e:/bjoer/Documents/repos/altiplano/src/altiplano/server.py) | **create_project**: Optionale Unterstützung für `identifier` hinzugefügt und an die Vikunja-API via `PUT /projects` übermittelt.<br>**update_project**: Optionale Unterstützung für `identifier` hinzugefügt. Der bestehende Wert wird beim GET-Request eingelesen und im vollständigen `POST`-Payload mitgeführt, um Datenverlust zu vermeiden. |
| [test_server.py](file:///e:/bjoer/Documents/repos/altiplano/tests/test_server.py) | Ergänzung des Tests `test_tool_create_project_with_identifier` zur Validierung des Payloads beim Erstellen.<br>Anpassung von `test_tool_update_project` (Erwartung des Standard-Werts `""` für den Identifier).<br>Ergänzung des Tests `test_tool_update_project_identifier` (Testszenarien für das Setzen, Beibehalten und Löschen des Project Identifiers). |

## Architektur und Datenfluss

1. **Client-Aufruf:** Der Client ruft `create_project` oder `update_project` über MCP mit dem optionalen Parameter `identifier` auf.
2. **API-Request:**
   - **create_project:** Das Argument wird direkt an die Vikunja-API im Payload des `PUT /projects` Requests gereicht.
   - **update_project:** Da Vikunja für Projekt-Updates einen vollständigen Payload via `POST /projects/{id}` verlangt, wird zuerst das aktuelle Projekt via `GET` abgefragt. Der existierende Identifier wird hierbei ermittelt (`project.get("identifier", "")`) und mit den vom Nutzer übermittelten Änderungen gemergt, bevor der `POST`-Request gesendet wird.
3. **API-Response:** Vikunja gibt das aktualisierte Projekt-Objekt inklusive `identifier` zurück, welches dem Benutzer präsentiert wird.

## Datenmodell und API-Mapping

Die Vikunja-API erwartet und liefert das Feld `identifier` als String. 
- In der API-Antwort von `GET /projects` wird das Feld unter dem Schlüssel `"identifier"` zurückgegeben und in `list_projects` transparent gemappt.
- In `PUT /projects` und `POST /projects/{id}` wird `"identifier"` im JSON-Payload übergeben. Wenn der Identifier entfernt werden soll, wird ein leerer String `""` gesendet.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `test_tool_create_project_with_identifier` | **Erfolgreich.** Prüft, ob `identifier="SHOP"` im `PUT`-Body für die Projekterstellung gesendet wird. |
| `test_tool_update_project` | **Erfolgreich.** Bestätigt die Abwärtskompatibilität, indem standardmässig ein leerer String gesendet wird, wenn kein Identifier existierte. |
| `test_tool_update_project_identifier` | **Erfolgreich.** Verifiziert das Verhalten beim Ändern des Identifiers (`identifier="NEWSHOP"`), beim Beibehalten des bestehenden Identifiers während anderer Updates (z. B. der Farbe) sowie beim Leeren (`identifier=""`). |

Ausführen der Tests via:
```bash
uv run pytest
```

## Betriebs- und Setup-Hinweise

- `Nicht relevant` (keine neuen Umgebungsvariablen oder Konfigurationsdateien erforderlich).

## Wartungshinweise

- **Payload-Overlay in `update_project`:** Falls Vikunja zukünftig weitere Pflichtfelder einführt, müssen diese analog zu `title`, `description`, `hex_color`, `parent_project_id` und `identifier` in `update_project` via `project.get(...)` ausgelesen und im POST-Body wieder mitgesendet werden.

## Bekannte Einschränkungen

- **Clientseitige Validierung:** Keine Regex-Prüfungen auf dem MCP-Server (z. B. Großbuchstaben-Zwang). Alle Validierungen überlassen wir der Vikunja-API, da deren Fehlermeldungen bereits sauber an den MCP-Client durchgereicht werden.
