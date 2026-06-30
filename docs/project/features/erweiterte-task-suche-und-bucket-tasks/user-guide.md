# User Guide: Erweiterte Task-Suche und Bucket-Tasks

## Überblick

Dieses Feature ermöglicht es KI-Agenten, Aufgaben in Vikunja effizienter und flexibler zu suchen sowie Kanban-spezifische Abläufe präzise abzubilden.
Es stellt zwei Haupt-Tools zur Verfügung:
1. `search_tasks`: Ermöglicht eine globale, projektübergreifende Suche und Filterung von Aufgaben anhand diverser Komfort-Kriterien (z. B. Status, Priorität, Labels, Fälligkeiten).
2. `get_bucket_tasks`: Ruft alle Aufgaben innerhalb einer bestimmten Kanban-Spalte (Bucket) in der korrekten Reihenfolge ab.

Das bisherige, projektbezogene Tool `list_tasks` wurde vollständig entfernt.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `search_tasks` | Sucht und filtert Aufgaben global über alle zugänglichen Projekte hinweg. Kombiniert strukturierte Filter und bietet ein intelligentes Textsuche-Fallback. | Siehe Parameter-Details unten | `list[dict]` (schlanke Task-Liste mit ID, Identifier, Titel, Status, Priorität, Fälligkeit und Projekt-ID) |
| `get_bucket_tasks` | Ruft Aufgaben eines spezifischen Kanban-Buckets ab, sortiert nach ihrer Position im Bucket. | `project_id` (int), `bucket_id` (int), `view_id` (optional, int), `page` (optional, int), `per_page` (optional, int) | `list[dict]` (schlanke Task-Liste mit ID, Identifier, Titel, Status, Priorität, Fälligkeit und Projekt-ID) |

### Parameter-Details für `search_tasks`

*   `text` (str): Suchbegriff. Wird bei alleiniger Nutzung als einfache Textsuche (`s`) an Vikunja übergeben. In Kombination mit anderen Kriterien wird es automatisch zu `(title ~ 'text' || description ~ 'text')` im Filter übersetzt.
*   `filter` (str): Manueller, roher Vikunja-Filterausdruck. Wird per `&&` mit anderen Parametern kombiniert.
*   `project_id` (int): ID des Zielprojekts.
*   `done` (bool): Filtert nach Erledigungsstatus (`true`/`false`).
*   `title_contains` (str): Filtert Aufgaben, deren Titel diesen Text enthält.
*   `description_contains` (str): Filtert Aufgaben, deren Beschreibung diesen Text enthält.
*   `label_ids` (list[int]): Filtert nach zugewiesenen Labels. Ein Label führt zu `labels = ID`, mehrere Labels zu `labels in ID1, ID2`.
*   `assignee_ids` (list[int]): Filtert nach Zuweisungsempfängern (analog zu Labels).
*   `priority_min` / `priority_max` (int): Filtert nach Prioritäten (z. B. `>= min` und `<= max`).
*   `due_before` / `due_after` (str): ISO-8601-Zeitstempel für Fälligkeit (exklusive Grenzen `<` und `>`).
*   `start_before` / `start_after` (str): ISO-8601-Zeitstempel für den Arbeitsbeginn.
*   `end_before` / `end_after` (str): ISO-8601-Zeitstempel für das Arbeitsende.
*   `done_before` / `done_after` (str): ISO-8601-Zeitstempel für die Fertigstellung.
*   `created_before` / `created_after` (str): ISO-8601-Zeitstempel für das Erstellungsdatum.
*   `updated_before` / `updated_after` (str): ISO-8601-Zeitstempel für die letzte Aktualisierung.
*   `percent_done_min` / `percent_done_max` (int): Filtert nach Fortschritt in Prozent.
*   `sort_by` (list[str]) / `order_by` (list[str]): Listen von Feldern zur Sortierung und der jeweiligen Richtung (`asc`/`desc`). Müssen dieselbe Länge aufweisen.
*   `page` (int) / `per_page` (int): Steuert die Paginierung (Standard: Seite 1, 50 Einträge pro Seite).
*   `expand` (list[str]): Ermöglicht das Mitliefern verknüpfter Ressourcen (erlaubt: `subtasks`, `buckets`, `reactions`, `comments`).
*   `filter_timezone` (str): Zeitzone für Datumsberechnungen (Standard: `Europe/Zurich`).
*   `filter_include_nulls` (bool): Steuert, ob null-Werte in den Filterergebnissen berücksichtigt werden.

## Voraussetzungen

- **Vikunja-API-Token:** Der verwendete API-Token muss Lese- und Schreibrechte für Projekte und Aufgaben besitzen.
- **Kanban-View für Buckets:** Um `get_bucket_tasks` zu nutzen, muss das Projekt eine Kanban-View besitzen (wird in der Regel automatisch beim Erstellen eines Projekts angelegt).

## Schritt-für-Schritt Demo

1.  **MCP Inspector starten:**
    Starte den Inspector im Projektordner:
    ```bash
    npx @modelcontextprotocol/inspector uv run altiplano
    ```
2.  **Globale Textsuche ausführen:**
    Rufe das Tool `search_tasks` im Inspector auf:
    *   Argument: `{"text": "Tandoor"}`
    *   Erwartung: Gibt alle Aufgaben zurück, die das Wort "Tandoor" im Titel oder der Beschreibung tragen.
3.  **Kombinierte Suche ausführen:**
    Rufe das Tool `search_tasks` auf:
    *   Argumente: `{"text": "Tandoor", "done": false}`
    *   Erwartung: Nur offene Aufgaben mit "Tandoor" werden zurückgegeben (interner Filter: `done = false && (title ~ 'Tandoor' || description ~ 'Tandoor')`).
4.  **Bucket-Aufgaben abrufen:**
    *   Ermittle ein Projekt und einen Bucket (z. B. via `list_buckets(project_id=12)`).
    *   Rufe `get_bucket_tasks` auf: `{"project_id": 12, "bucket_id": 34}`.
    *   Erwartung: Listet alle Aufgaben in diesem Bucket in der exakten Kanban-Reihenfolge.

## Bekannte Einschränkungen

- **Mehrere Kanban-Views:** Besitzt ein Projekt mehrere Kanban-Views, wird bei `get_bucket_tasks` automatisch die erste von der API zurückgegebene Kanban-View verwendet.
- **Keine Kanban-View:** Existiert im Projekt keine Kanban-View, bricht `get_bucket_tasks` mit einer Fehlermeldung (`RuntimeError`) ab.
