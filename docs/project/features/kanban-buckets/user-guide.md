# User Guide: Kanban Buckets

## Überblick

Dieses Feature erweitert den Altiplano MCP-Server um die Unterstützung für Kanban-Buckets (Spalten) in Vikunja-Projekten. Damit lässt sich die Kanban-Struktur von Projekten direkt über MCP-Tools aus LLM-Workflows steuern. Das Erstellen von Spalten, das Umbenennen, Limitieren und das Verschieben von Aufgaben (Tasks) in Spalten wird vollständig unterstützt.

Da die Vikunja-API Buckets nicht direkt an einem Projekt, sondern an einer *Projekt-View* (wie z. B. Kanban, Liste, Gantt) verwaltet, kapselt Altiplano diese Views-Zwischenebene serverseitig. Die Tools verlangen vom Endanwender weiterhin nur die einfache `project_id`.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `list_buckets` | Listet alle Buckets (Spalten) der Kanban-View eines Projekts auf. | `project_id` (int) | Liste von Buckets (mit `id`, `title`, `limit`, `position`, `count`). |
| `create_bucket` | Erstellt einen neuen Kanban-Bucket (Spalte) in der Kanban-View eines Projekts. | `project_id` (int), `title` (str), `limit` (int, optional) | Details des erstellten Buckets. |
| `update_bucket` | Aktualisiert einen Kanban-Bucket. Nur übergebene Felder werden geändert. | `project_id` (int), `bucket_id` (int), `title` (str, optional), `limit` (int, optional) | Details des aktualisierten Buckets. |
| `move_task_to_bucket` | Verschiebt einen Task in einen bestimmten Kanban-Bucket (Spalte). | `task_id` (int), `bucket_id` (int) | Details des Zuweisungs-Status. |

## Voraussetzungen

* Der verwendete Vikunja-API-Token benötigt Lese- und Schreibrechte für Projekte, Views, Buckets und Tasks.
* Das Vikunja-Projekt muss in der Vikunja-UI bereits über eine Kanban-Ansicht verfügen (Standard bei neuen Vikunja-Projekten). Falls keine Kanban-Ansicht existiert, geben die Tools eine Fehlermeldung zurück.

## Schritt-für-Schritt Demo

1. **MCP Inspector starten:**
   Führe den Server im MCP Inspector aus:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. **Buckets auflisten:**
   Wähle das Tool `list_buckets` und gib eine gültige `project_id` ein. Du erhältst eine Liste der Spalten wie z. B. "Backlog", "Doing" und "Done".
3. **Neuen Bucket erstellen:**
   Rufe `create_bucket` mit `project_id` und `title="Review"` auf. Der neue Bucket erscheint sofort im Kanban-Board der Vikunja-Web-UI.
4. **Bucket aktualisieren:**
   Um ein Limit von maximal 3 Tasks einzuführen, rufe `update_bucket` mit der `project_id`, der `bucket_id` des neuen Buckets und `limit=3` auf.
5. **Task in Bucket verschieben:**
   Verschiebe einen Task mit `move_task_to_bucket`, indem du die `task_id` und die `bucket_id` des Ziel-Buckets übergibst.

## Bekannte Einschränkungen

* Es wird stets die erste in der API-Reihenfolge zurückgegebene Kanban-Ansicht eines Projekts verwendet.
* Falls ein Projekt keine Kanban-Ansicht besitzt, wird keine automatische Ansicht erzeugt. Der Benutzer muss diese in der Web-UI anlegen.
