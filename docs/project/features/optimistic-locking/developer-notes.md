# Developer Notes: Optimistic Locking Support

## API-Kontext
Vikunja verwendet zur Absicherung gegen konkurrierende Schreibzugriffe ein optimistisches Sperrverfahren. 
Bei Ressourcen-Updates (`POST /projects/{id}` und `POST /tasks/{id}`) prüft der Server den Zeitstempel des empfangenen `updated`-Feldes mit dem aktuellen Datenbankeintrag. Weicht dieser ab oder fehlt er gänzlich, bricht die API mit `412 Precondition Failed` ab.

## Implementierungsdetails

### 1. `update_project`
Der bisherige Ablauf:
```python
async def update_project(...):
    payload = {...}
    return await _request("POST", f"/projects/{project_id}", json=payload)
```

Der neue Ablauf:
```python
async def update_project(...):
    payload = {...}
    # 1. Aktuellen Status holen
    project = await _request("GET", f"/projects/{project_id}")
    # 2. updated-Zeitstempel einfügen
    if "updated" in project:
        payload["updated"] = project["updated"]
    # 3. POST ausführen
    return await _request("POST", f"/projects/{project_id}", json=payload)
```

### 2. `update_task` und andere Task-Tools
Für `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` verfahren wir identisch. 
In `move_task_to_project` existiert bereits ein GET-Request, um das Feld `done` auszulesen. Dort müssen wir lediglich das `updated`-Feld zusätzlich in den POST-Request einfügen.

Beispiel für `update_task`:
```python
async def update_task(...):
    payload = {...}
    task = await _request("GET", f"/tasks/{task_id}")
    if "updated" in task:
        payload["updated"] = task["updated"]
    return await _request("POST", f"/tasks/{task_id}", json=payload)
```

## Testing & Mocks
Da nun bei Updates zwei Requests anstelle von einem abgesetzt werden (GET gefolgt von POST), müssen die Test-Mocks in `tests/test_server.py` angepasst werden.
Wir überschreiben hierzu den `return_value` des `_request` Mocks mit einem `side_effect`, welcher je nach HTTP-Methode und URL-Pfad passende Mock-Daten zurückgibt:

```python
async def mock_request_side_effect(method, path, **kwargs):
    if method == "GET" and path == "/projects/1":
        return {"id": 1, "title": "Old Title", "updated": "2026-06-24T12:00:00Z"}
    if method == "POST" and path == "/projects/1":
        return {"id": 1, "title": "Updated Title", "hex_color": "00ff00", "updated": "2026-06-24T12:00:00Z"}
    # ...
```
Dies stellt sicher, dass die Tests weiterhin die korrekte Abfolge der API-Calls prüfen.
