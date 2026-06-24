# User Guide: Task Security Tools

## Überblick

Dieses Feature stellt zwei dedizierte Sicherheits-Tools (`complete_task` und `move_task_to_project`) zur Verfügung. Diese dienen als Convenience-Wrapper um das allgemeine `update_task` Tool. Sie reduzieren das Risiko von Fehlern oder unerwünschten Datenüberschreibungen durch KI-Agenten, da sie nur die spezifisch benötigten Parameter annehmen und verarbeiten.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `complete_task` | Markiert eine Aufgabe als erledigt (`done=True`) und fügt optional einen Kommentar hinzu. | `task_id` (int, Pflicht)<br>`comment` (str, optional) | JSON-Objekt der aktualisierten Aufgabe. |
| `move_task_to_project` | Verschiebt eine Aufgabe in ein anderes Projekt und behält dabei den aktuellen Erledigungsstatus bei. | `task_id` (int, Pflicht)<br>`project_id` (int, Pflicht) | JSON-Objekt der aktualisierten Aufgabe. |

## Voraussetzungen

- Die Vikunja-Instanz muss erreichbar und der API-Token gültig sein (Schreibrechte für Aufgaben und Kommentare).

## Schritt-für-Schritt Demo

1. Starte den MCP Inspector:
   ```powershell
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. Rufe das Tool `complete_task` mit einer validen Task-ID auf (z. B. `task_id=123`).
3. Prüfe, ob die Antwort der API `{"done": true}` zurückgibt und die Aufgabe in Vikunja als erledigt angezeigt wird.
4. Rufe das Tool `move_task_to_project` mit einer Task-ID und einer gültigen Project-ID auf (z. B. `task_id=123`, `project_id=456`).
5. Prüfe im Vikunja UI, ob die Aufgabe in das neue Projekt verschoben wurde und ihr Status (erledigt) erhalten geblieben ist.

## Bekannte Einschränkungen

Keine.
