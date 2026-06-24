# User Guide: list_projects Hex Color

## Überblick

Das Feature ermöglicht es dem MCP-Server, die benutzerdefinierten Projektfarben (Hexadezimalcodes) direkt aus Vikunja auszulesen und in der Tool-Rückgabe von `list_projects` bereitzustellen. Dadurch erhalten KI-Agenten die nötigen Metadaten, um Projekte anhand ihrer Farben visuell zu unterscheiden oder diese Farben dem Nutzer anzuzeigen.

## MCP-Tools

Das betroffene Tool ist `list_projects`.

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `list_projects` | Listet alle Projekte (Boards) auf. Das Feld `hex_color` enthält den Hex-Farbcode des Projekts. | Keine | Eine Liste von Projekt-Objekten (Dictionaries) mit den Feldern `id`, `title`, `parent_project_id`, `is_archived` und `hex_color`. |

## Voraussetzungen

- Eine lauffähige Vikunja-Instanz.
- Ein konfigurierter Vikunja-API-Token (`VIKUNJA_API_TOKEN`) und die API-URL (`VIKUNJA_URL`).
- Die Berechtigungen des Tokens müssen Lesezugriff auf Projekte umfassen (standardmäßig der Fall).

## Schritt-für-Schritt Demo

1. Starten Sie den MCP-Server lokal im Inspector:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. Klicken Sie im MCP Inspector auf das Tool `list_projects` und führen Sie es aus (`Call Tool`).
3. Betrachten Sie die JSON-Antwort. Jedes Projekt enthält nun das zusätzliche Feld `hex_color`:
   ```json
   {
     "id": 1,
     "title": "Mein tolles Projekt",
     "parent_project_id": 0,
     "is_archived": false,
     "hex_color": "00ff00"
   }
   ```
   *Hinweis: Wenn ein Projekt keine explizite Farbe zugewiesen hat, wird ein leerer String `""` zurückgegeben.*

## Bekannte Einschränkungen

- Vikunja liefert Farbwerte typischerweise als 6-stelligen Hex-Code ohne vorangestelltes `#`-Zeichen (z.B. `00ff00`). Dies wird so 1:1 durchgereicht.
- Das Setzen der Farbe ist nicht Teil dieses Features, kann aber über das `update_project` Tool vorgenommen werden.
