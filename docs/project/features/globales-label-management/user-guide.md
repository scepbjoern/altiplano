# User Guide: Globales Label Management

## Überblick

Dieses Feature erweitert den MCP-Server um die Möglichkeit, globale Labels in der Vikunja-Instanz zu erstellen, zu aktualisieren und zu löschen. Zuvor war nur die Zuweisung existierender Labels zu Aufgaben möglich. Nun können Labels direkt über KI-Agenten verwaltet werden.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `create_label` | Erstellt ein neues globales Label. | `title` (str, Pflicht)<br>`description` (str, optional)<br>`hex_color` (str, optional, z.B. "ff0000") | Details des neu erstellten Labels (dict). |
| `update_label` | Aktualisiert ein bestehendes Label. Nur die angegebenen Felder werden geändert. | `label_id` (int, Pflicht)<br>`title` (str, optional)<br>`description` (str, optional)<br>`hex_color` (str, optional) | Details des aktualisierten Labels (dict). |
| `delete_label` | Löscht ein globales Label. Dies ist eine destruktive Operation und erfordert Bestätigung. | `label_id` (int, Pflicht)<br>`confirm` (bool, Standard: `False`) | Status-Response (z.B. `{"ok": true}`). |

## Voraussetzungen

- Gültige Verbindung zu einer Vikunja-Instanz via `VIKUNJA_URL` und `VIKUNJA_API_TOKEN`.
- Berechtigungen zum Verwalten von Labels in der Ziel-Instanz.

## Schritt-für-Schritt Demo

1. **MCP Inspector starten**:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. **Label erstellen**:
   Führe das Tool `create_label` mit folgenden Parametern aus:
   - `title`: `"Priorität: Hoch"`
   - `hex_color`: `"ff0000"`
   - `description`: `"Wichtige und dringende Tasks"`
   Dies gibt das erstellte Label inklusive einer ID zurück (z. B. `12`).

3. **Label aktualisieren**:
   Führe das Tool `update_label` mit der ermittelten ID aus:
   - `label_id`: `12`
   - `hex_color`: `"ff5500"`
   Das Label wird aktualisiert, andere Felder bleiben erhalten.

4. **Label löschen (Sicherheitsfehler)**:
   Führe `delete_label` aus:
   - `label_id`: `12`
   - `confirm`: `false`
   *Ergebnis:* Das Tool bricht mit einer Fehlermeldung ab, die auf die Notwendigkeit von `confirm=true` hinweist.

5. **Label erfolgreich löschen**:
   Führe `delete_label` aus:
   - `label_id`: `12`
   - `confirm`: `true`
   *Ergebnis:* Das Label wird in Vikunja gelöscht.

## Bekannte Einschränkungen

- Das Löschen von Labels hat direkte Auswirkungen auf alle Tasks, denen dieses Label zugewiesen ist (die Zuweisung geht verloren). Deshalb erfordert das Löschen eine explizite Bestätigung (`confirm=true`).
