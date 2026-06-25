# User Guide: Allgemeines Löschen

## Überblick

Das Feature **Allgemeines Löschen** erweitert den Vikunja MCP Server um die Möglichkeit, ungenutzte oder veraltete Tasks, Kommentare und Kanban-Buckets direkt über entsprechende MCP-Tools zu löschen.

Um unbeabsichtigten Datenverlust (z.B. durch Fehler oder Halluzinationen des LLMs) zu verhindern, wurde ein zweistufiges Sicherheits-Pattern implementiert:
* Jedes Lösch-Tool verlangt zwingend den Parameter `confirm=true`.
* Wenn das Tool mit `confirm=false` (Standard) aufgerufen wird, bricht es mit einer unmissverständlichen Fehlermeldung ab. Diese zwingt das LLM dazu, dich als Anwender explizit nach deiner Zustimmung zu fragen. Erst nach deiner Freigabe darf das LLM das Tool mit `confirm=true` erneut aufrufen, um die eigentliche Löschung durchzuführen.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `delete_task` | Löscht eine Aufgabe endgültig. | `task_id` (int), `confirm` (bool = False) | `dict` (z.B. `{"ok": true}`) |
| `delete_comment` | Löscht einen spezifischen Kommentar einer Aufgabe. | `task_id` (int), `comment_id` (int), `confirm` (bool = False) | `dict` (z.B. `{"ok": true}`) |
| `delete_bucket` | Löscht einen Kanban-Bucket in einem Projekt. | `project_id` (int), `bucket_id` (int), `confirm` (bool = False) | `dict` (z.B. `{"ok": true}`) |

## Voraussetzungen

* **Vikunja-API-Berechtigungen:** Das verwendete Vikunja-API-Token muss die Berechtigung besitzen, die entsprechenden Ressourcen zu löschen.
* **Kanban-View:** Für `delete_bucket` muss das Projekt eine Kanban-Ansicht besitzen, damit die interne Ansichts-ID (`view_id`) ermittelt werden kann.

## Schritt-für-Schritt Demo

1. Starte den MCP Inspector (falls nicht bereits aktiv):
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. Öffne die angezeigte Inspector URL im Browser (z.B. `http://localhost:6274`).
3. Gehe im linken Menü auf **Tools** und wähle `delete_task`.
4. **Schritt 1: Sicherheitsabbruch testen**
   * Trage eine beliebige `task_id` ein (z.B. `123`).
   * Belasse `confirm` auf `false`.
   * Klicke auf **Run Tool**.
   * **Erwartetes Ergebnis:** Das Tool schlägt mit folgender Fehlermeldung fehl:
     `ValueError: DANGER: This is a destructive operation. You MUST ask the human user for explicit confirmation...`
5. **Schritt 2: Bestätigte Löschung testen**
   * Trage die reale ID einer Aufgabe ein, die gelöscht werden soll.
   * Setze den Parameter `confirm` im Formular auf `true`.
   * Klicke auf **Run Tool**.
   * **Erwartetes Ergebnis:** Die Aufgabe wird in Vikunja gelöscht und das Tool gibt `{"ok": true}` zurück.

## Bekannte Einschränkungen

* **Kein Papierkorb:** Vikunja löscht Ressourcen direkt über die API. Gelöschte Ressourcen können nicht wiederhergestellt werden.
* **Projekte löschen:** Das Löschen ganzer Projekte ist aus Sicherheitsgründen nicht im Scope dieses Features und wird nicht unterstützt.
