# User Guide: Task-Beziehungen

## Überblick

Das Feature "Task-Beziehungen" ermöglicht es, hierarchische und logische Abhängigkeiten zwischen Aufgaben in Vikunja abzubilden. Der MCP-Server stellt Tools bereit, um diese Beziehungen aufzulisten, hinzuzufügen und zu entfernen. Dies unterstützt komplexe Planungs- und Priorisierungsszenarien in LLM-Workflows.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `list_task_relations` | Listet alle Beziehungen einer Aufgabe auf. | `task_id: int` | Eine Liste von Beziehungsobjekten mit ID, Titel, Beziehungstyp, Erledigungsstatus und Priorität. |
| `add_task_relation` | Erstellt eine Beziehung zwischen der Ausgangsaufgabe und einer anderen Aufgabe. | `task_id: int`, `other_task_id: int`, `relation_kind: RelationKind` | Das Antwort-Objekt der Vikunja-API. |
| `remove_task_relation` | Entfernt eine bestehende Beziehung zwischen Aufgaben. | `task_id: int`, `other_task_id: int`, `relation_kind: RelationKind` | Das Antwort-Objekt der Vikunja-API. |

### Unterstützte Beziehungstypen (`RelationKind`)
Folgende Werte sind für `relation_kind` zulässig:
* `subtask`: Die andere Aufgabe ist eine Unteraufgabe dieser Aufgabe.
* `parenttask`: Die andere Aufgabe ist eine Hauptaufgabe dieser Aufgabe.
* `related`: Die Aufgaben sind lose miteinander verknüpft.
* `duplicateof`: Diese Aufgabe ist ein Duplikat der anderen Aufgabe.
* `duplicates`: Die andere Aufgabe ist ein Duplikat dieser Aufgabe.
* `blocking`: Diese Aufgabe blockiert die andere Aufgabe.
* `blockedby`: Diese Aufgabe wird von der anderen Aufgabe blockiert.
* `precedes`: Diese Aufgabe muss vor der anderen Aufgabe erledigt werden.
* `follows`: Diese Aufgabe muss nach der anderen Aufgabe erledigt werden.
* `copiedfrom`: Diese Aufgabe wurde von der anderen Aufgabe kopiert.
* `copiedto`: Diese Aufgabe wurde in die andere Aufgabe kopiert.

## Voraussetzungen

* **Vikunja-API-Token:** Der verwendete Token muss Lese- und Schreibrechte auf den betroffenen Projekten besitzen.
* **Existierende Aufgaben:** Beide Aufgaben müssen bereits in Vikunja existieren.

## Schritt-für-Schritt Demo

1. **MCP Inspector starten:**
   ```powershell
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. **Beziehung hinzufügen:**
   Rufe `add_task_relation` auf:
   * `task_id`: `1` (Ausgangsaufgabe)
   * `other_task_id`: `2` (Zielaufgabe)
   * `relation_kind`: `"subtask"`
3. **Beziehungen auflisten:**
   Rufe `list_task_relations` für `task_id=1` auf. Du erhältst ein Array mit der neuen Relation zurück:
   ```json
   [
     {
       "id": 2,
       "title": "Name der Unteraufgabe",
       "relation_kind": "subtask",
       "done": false,
       "priority": 0
     }
   ]
   ```
4. **Beziehung entfernen:**
   Rufe `remove_task_relation` auf mit `task_id=1`, `other_task_id=2` und `relation_kind="subtask"`.

## Bekannte Einschränkungen

* **Descriptiver Charakter:** Die Beziehungen in Vikunja dienen primär der Visualisierung und Strukturierung. Sie erzwingen standardmäßig keine automatischen Statusänderungen (z. B. wird eine Hauptaufgabe nicht automatisch als erledigt markiert, wenn alle Unteraufgaben erledigt sind).
