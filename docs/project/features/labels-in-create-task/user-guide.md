# User Guide: Labels in create_task

## Überblick

Das Feature ermöglicht die direkte Zuweisung von Labels beim Erstellen einer Aufgabe über den MCP-Server. Anstatt nach dem Erstellen einer Aufgabe für jedes Label ein separates Tool (`add_label`) aufzurufen, kann dem `create_task`-Tool nun direkt eine Liste von Label-IDs übergeben werden. Dies spart Netzwerk-Roundtrips, vereinfacht LLM-Workflows und reduziert Token-Kosten.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `create_task` | Erstellt eine neue Aufgabe in einem Projekt. Unterstützt die direkte Label-Zuweisung. | `project_id: int` (Pflicht)<br>`title: str` (Pflicht)<br>`description: str \| None` (Optional)<br>`priority: int \| None` (Optional)<br>`due_date: str \| None` (Optional)<br>`start_date: str \| None` (Optional)<br>`end_date: str \| None` (Optional)<br>`label_ids: list[int] \| None` (Optional) | Ein `dict` mit den Details der neu erstellten Aufgabe. Enthält bei Fehlern bei der Label-Zuweisung das Feld `label_errors: list[str]`. |

## Voraussetzungen

- Gültige Vikunja-API-Verbindung (`VIKUNJA_URL` und `VIKUNJA_API_TOKEN`).
- Die in `label_ids` übergebenen Labels müssen bereits in Vikunja existieren (ihre IDs können mit dem Tool `list_labels` ermittelt werden).

## Schritt-für-Schritt Demo

1. Starte den MCP Inspector für den Altiplano-Server:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. Finde das Tool `create_task` in der Liste der Tools.
3. Führe das Tool mit folgenden Beispielparametern aus:
   - `project_id`: `1` (bzw. eine existierende Projekt-ID)
   - `title`: `"Neue Aufgabe mit Labels"`
   - `label_ids`: `[1, 2]` (bzw. IDs existierender Labels)
4. Überprüfe die Response. Sie sollte die Details der neu erstellten Aufgabe enthalten, z.B.:
   ```json
   {
     "id": 123,
     "title": "Neue Aufgabe mit Labels",
     "priority": 0,
     "done": false,
     "identifier": "PROJ-123"
   }
   ```
5. Prüfe in der Vikunja Web-Oberfläche, ob die Aufgabe im entsprechenden Projekt existiert und ob ihr die Labels mit den IDs `1` und `2` zugewiesen wurden.
6. Führe einen Test mit einer ungültigen Label-ID aus (z. B. `99999`). Das Tool sollte die Aufgabe dennoch erstellen, jedoch im Antwort-Dict eine Liste `label_errors` enthalten:
   ```json
   {
     "id": 124,
     "title": "Aufgabe mit Label-Fehler",
     "priority": 0,
     "done": false,
     "identifier": "PROJ-124",
     "label_errors": [
       "Vikunja API error 404 on PUT /tasks/124/labels: {'code': 404, 'message': '...'}"
     ]
   }
   ```

## Bekannte Einschränkungen

- **Nur Label-IDs**: Die Zuweisung erfolgt ausschließlich über die ganzzahligen IDs der Labels (`label_ids`). Eine Zuweisung per Freitext oder Label-Namen (z. B. `["@online"]`) wird aktuell nicht direkt in `create_task` unterstützt.
