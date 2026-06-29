# Developer Notes: Labels in create_task

## Überblick

Dieses Feature ermöglicht die atomare/gebündelte Übergabe von Labels beim Erstellen einer Aufgabe über das MCP-Tool `create_task`. Technisch wird nach der erfolgreichen Anlage der Aufgabe über Vikunja-API-Requests iteriert, um die Labels einzeln zuzuweisen. Fehlschläge bei der Label-Zuweisung werden abgefangen, um die Erstellung der Aufgabe selbst nicht fehlschlagen zu lassen (Partial Errors / Teilfehler).

## Referenzen

- Plan: `docs/project/features/labels-in-create-task/plan-v001.md`
- PRD: `docs/project/prds/vikunja-mcp-server-v011.md`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| [src/altiplano/server.py](file:///e:/bjoer/Documents/repos/altiplano/src/altiplano/server.py) | Erweiterung des `create_task`-Tools um den Parameter `label_ids` und die sequentielle Zuweisungs- und Fehlerbehandlungslogik. |
| [tests/test_server.py](file:///e:/bjoer/Documents/repos/altiplano/tests/test_server.py) | Hinzufügen von drei Unit- und Integrationstests (`test_tool_create_task_no_labels`, `test_tool_create_task_with_labels_success`, `test_tool_create_task_with_labels_partial_error`). |

## Architektur und Datenfluss

1. Der MCP-Client ruft `create_task` mit `project_id`, `title` und optional `label_ids` auf.
2. Der Server führt den `PUT`-Request zur Task-Erstellung unter `/projects/{project_id}/tasks` aus und erhält ein Dictionary mit der ID der neuen Aufgabe zurück.
3. Wenn `label_ids` übergeben wurden, iteriert der Server über diese Liste und führt für jede Label-ID einen `PUT`-Request an `/tasks/{task_id}/labels` mit Payload `{"label_id": label_id}` aus.
4. Alle auftretenden `RuntimeError`-Exceptions (die von `_request` bei HTTP-Fehlern geworfen werden) werden abgefangen und als Strings gesammelt.
5. Das Antwort-Dictionary wird bei Teilfehlern um den Key `label_errors` erweitert, der die Fehlerliste enthält, und an den Client zurückgegeben.

## Datenmodell und API-Mapping

- Parameter: `label_ids: list[int] | None = None`
- Rückgabe:
  - Bei Erfolg mit Labels: Das Standard-Task-Dictionary von Vikunja.
  - Bei Teilfehler mit Labels: Das Standard-Task-Dictionary erweitert um `label_errors: list[str]`.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `uv run pytest tests/test_server.py -k create_task` | Erfolgreich. Alle drei neuen Testfälle laufen grün durch und prüfen das Verhalten bei Erfolg, Teilfehler sowie ohne Labels. |
| `uv run pytest` | Erfolgreich. Gesamte Testsuite (41 Tests) läuft fehlerfrei. |

## Betriebs- und Setup-Hinweise

Nicht relevant. Es sind keine neuen Umgebungsvariablen oder Konfigurationsdateien erforderlich.

## Wartungshinweise

- **Gotchas / API-Verhalten**: Da Vikunja für jedes Label einen separaten API-Aufruf benötigt, steigt die Latenz linear mit der Anzahl der zuzuweisenden Labels. Für typische Anwendungsfälle (1-3 Labels) ist dies jedoch absolut vernachlässigbar.
- **Fehlerbehandlung**: Es werden gezielt nur `RuntimeError` abgefangen. Andere, unerwartete Exceptions brechen den Ablauf ab.

## Bekannte Einschränkungen

- **Keine textbasierten Labels**: Es werden nur numerische IDs unterstützt. Textuelle Bezeichnungen müssen zuvor über andere Tools aufgelöst oder erstellt werden.
