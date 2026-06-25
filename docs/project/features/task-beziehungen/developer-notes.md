# Developer Notes: Task-Beziehungen

## Überblick

Das Feature "Task-Beziehungen" erweitert den MCP-Server um die Verwaltung von Verbindungen zwischen Aufgaben in der Vikunja-Instanz.

## Referenzen

- Plan: `docs/project/features/task-beziehungen/plan-v001.md`
- PRD: `docs/project/prds/vikunja-mcp-server-v006.md`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| `src/altiplano/server.py` | Hinzufügen der MCP-Tools `list_task_relations`, `add_task_relation` und `remove_task_relation` sowie Einführung des `RelationKind` Literaltyps für formale Typsicherheit. |
| `tests/test_server.py` | Ergänzung der Unit- und Integrationstests (einschließlich Mocks für das Listen, Erstellen und Löschen von Beziehungen). |

## Architektur und Datenfluss

1. **MCP-Tool Discovery:** Beim Starten des MCP-Servers werden die Tools registriert. Der Typ `RelationKind` sorgt dafür, dass Clients die gültigen Werte via JSON-Schema/Enum auslesen können.
2. **Datenabruf:** `list_task_relations` ruft `GET /tasks/{task_id}` ab und liest das Feld `related_tasks` aus dem Task-Objekt.
3. **Beziehung erstellen:** `add_task_relation` sendet einen `PUT`-Request an `/tasks/{task_id}/relations` mit dem Zieltask und dem Relationstyp.
4. **Beziehung löschen:** `remove_task_relation` sendet einen `DELETE`-Request an `/tasks/{task_id}/relations/{relation_kind}/{other_task_id}`.

## Datenmodell und API-Mapping

Die Vikunja-API liefert `related_tasks` als verschachteltes Dictionary (Typ `RelatedTaskMap`), in dem die Schlüssel die Beziehungstypen (Strings) sind und die Werte Listen von Task-Objekten darstellen:
```json
{
  "subtask": [
    {
      "id": 2,
      "title": "Subtask Task",
      "done": false,
      "priority": 0
    }
  ]
}
```
Der Parser in `list_task_relations` ist robust ausgelegt und unterstützt sowohl dieses Dictionary-Format als auch ein flaches Listen-Format von Relationsobjekten, um Abwärtskompatibilität und Robustheit gegenüber API-Änderungen zu gewährleisten.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `uv run pytest` | 31 Tests erfolgreich bestanden (5 neue Testfälle für Beziehungen). |
| Mocks in `test_server.py` | `test_tool_list_task_relations`, `test_tool_list_task_relations_empty`, `test_tool_list_task_relations_dict`, `test_tool_add_task_relation`, `test_tool_remove_task_relation` |

## Betriebs- und Setup-Hinweise

* Keine zusätzlichen Umgebungsvariablen nötig. Es wird die bestehende Vikunja-Authentifizierung verwendet.

## Wartungshinweise

* **Gotcha:** Das Feld `related_tasks` in der API-Antwort von `GET /tasks/{id}` kann fehlen (`None` sein). Dies wird durch das Fallback-Mapping abgefangen.
* **Erweiterungen:** Falls Vikunja in Zukunft neue Beziehungstypen einführt, müssen diese im Typ `RelationKind` in `server.py` ergänzt werden.
