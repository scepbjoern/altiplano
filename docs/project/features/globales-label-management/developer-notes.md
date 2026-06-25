# Developer Notes: Globales Label Management

## Überblick

Dieses Feature implementiert die globale Verwaltung von Labels (Erstellen, Aktualisieren, Löschen) im MCP-Server. Die Schnittstellen nutzen direkt die Vikunja-API-Endpunkte `/labels`.

## Referenzen

- Plan: [plan-v001.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/globales-label-management/plan-v001.md)
- PRD: [vikunja-mcp-server-v009.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/prds/vikunja-mcp-server-v009.md)

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| `src/altiplano/server.py` | Implementierung der MCP-Tools `create_label`, `update_label` und `delete_label`. |
| `tests/test_server.py` | Tests für die neuen MCP-Tools mit Mocks für die Vikunja-API. |

## Architektur und Datenfluss

Die neu hinzugefügten MCP-Tools verwenden die interne Hilfsfunktion `_request` in `server.py`, um HTTP-Anfragen an die Vikunja-API zu senden. 
Da die Vikunja-API bei Updates (`POST /labels/{id}`) alle Pflichtfelder erwartet, holt `update_label` zuerst den aktuellen Zustand des Labels via `GET /labels/{id}` und überschreibt diesen mit den übergebenen Parametern (Overlay-Pattern), bevor es per `POST` an Vikunja gesendet wird.

## Datenmodell und API-Mapping

- `create_label` -> `PUT /labels`
- `update_label` -> `GET /labels/{id}` gefolgt von `POST /labels/{id}` (Overlay-Pattern)
- `delete_label` -> `DELETE /labels/{id}` (geschützt durch `confirm=True` Abfrage im Server-Code)

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `pytest` | 36 Tests erfolgreich durchgeführt (`uv run pytest`). |
| `test_mcp_initialization` | Prüft, dass die neuen Tools registriert sind. |
| `test_tool_create_label` | Verifiziert den `PUT`-Request und Payload. |
| `test_tool_update_label` | Verifiziert das GET-then-POST Overlay-Pattern bei Teil-Updates. |
| `test_tool_update_label_no_fields` | Verifiziert den `ValueError` bei leeren Updates. |
| `test_tool_delete_label` | Verifiziert, dass ein Löschen ohne `confirm=True` mit einem Fehler abbricht, und mit `confirm=True` den `DELETE`-Request absetzt. |

## Betriebs- und Setup-Hinweise

Keine neuen Umgebungsvariablen erforderlich. Nutzt die bestehenden Konfigurationen für `VIKUNJA_URL` und `VIKUNJA_API_TOKEN`.

## Wartungshinweise

- Sollte Vikunja in künftigen API-Versionen ein echtes `PATCH` für Labels unterstützen, kann das GET-then-POST Pattern in `update_label` durch ein direktes `PATCH` ersetzt werden.
- Das `confirm`-Pattern in `delete_label` schützt vor unabsichtlichem Datenverlust und muss bei allen destruktiven Tools konsistent angewendet werden.
