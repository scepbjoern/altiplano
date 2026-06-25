# User Guide: Dateianhänge

## Überblick

Das Feature **Dateianhänge** ermöglicht es KI-Agenten, Dateien an bestehende Vikunja-Aufgaben (Tasks) anzuhängen, Anhänge aufzulisten und zu löschen. Da in Remote- oder Homelab-Deployments der MCP-Server und das LLM kein gemeinsames Dateisystem besitzen, unterstützt dieses Feature den Direkt-Upload via Base64-Codierung (für kleine Dateien bis 2 MB) sowie den Download und Upload direkt aus einer übergebenen Web-URL. Für größere lokale Dateien kann das LLM dem Nutzer einen anklickbaren Web-Link zur Vikunja-Oberfläche generieren, damit der Upload dort manuell erfolgen kann.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `list_task_attachments` | Listet alle Anhänge einer Aufgabe auf. | `task_id: int` | Liste von Dictionaries mit Anhang-Metadaten (`id`, `name`, `size`, `created`). |
| `delete_task_attachment` | Löscht einen bestimmten Anhang von einer Aufgabe. | `task_id: int`, `attachment_id: int` | Bestätigungs-Dictionary. |
| `get_task_frontend_url` | Generiert die anklickbare Web-UI-URL für eine Aufgabe (für manuellen Upload). | `task_id: int` | URL als String. |
| `upload_task_attachment_base64` | Lädt eine Datei bis zu 2 MB per Base64-kodiertem String zu einer Aufgabe hoch. | `task_id: int`, `filename: str`, `content_base64: str` | Metadaten des erstellten Anhangs. |
| `upload_task_attachment_from_url` | Lädt eine Datei von einer öffentlichen URL herunter und hängt sie an eine Aufgabe an. | `task_id: int`, `url: str` | Metadaten des erstellten Anhangs. |

## Voraussetzungen

- **Vikunja-API-Verbindung:** Das in der Konfiguration hinterlegte API-Token muss Schreib- und Leserechte für Aufgaben und Anhänge besitzen.
- **Dateigröße:** Der Base64-Upload ist hart auf 2 MB begrenzt, um das Token-Limit des MCP-Protokolls nicht zu sprengen.
- **Internetzugriff:** Für `upload_task_attachment_from_url` muss der Server Zugriff auf das Internet haben, um die Datei von der Ziel-URL herunterzuladen.

## Schritt-für-Schritt Demo

1. **MCP Inspector starten:**
   Starten Sie den MCP Inspector lokal über:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
   Öffnen Sie die angegebene URL in Ihrem Browser.

2. **Aufgabe aufrufen und Link generieren:**
   Rufen Sie das Tool `get_task_frontend_url` mit einer existierenden `task_id` (z.B. `1`) auf. Sie erhalten den direkten Link zur Aufgabe im Vikunja Web-Interface.

3. **Datei per Base64 hochladen:**
   Rufen Sie das Tool `upload_task_attachment_base64` mit einer existierenden `task_id`, einem Dateinamen (z.B. `test.txt`) und einem Base64-Inhalt auf (z.B. `SGVsbG8gV29ybGQh` für "Hello World!").

4. **Anhänge listen:**
   Rufen Sie `list_task_attachments` für dieselbe `task_id` auf, um zu überprüfen, ob Ihre Datei in der Liste der Anhänge auftaucht. Notieren Sie sich die angezeigte `id` des Anhangs.

5. **Anhang löschen:**
   Rufen Sie `delete_task_attachment` mit der `task_id` und der vorhin notierten `attachment_id` auf, um die Datei wieder zu löschen.

## Bekannte Einschränkungen

- **Größenbeschränkung:** Base64-kodierte Dateien über 2 MB werden mit einem `ValueError` abgelehnt. Der Client sollte in diesem Fall `get_task_frontend_url` nutzen.
