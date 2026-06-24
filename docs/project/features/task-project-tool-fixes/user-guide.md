# User Guide: Task- & Projekt-Tool-Fixes

## Überblick

Dieses Feature behebt zwei wichtige Lücken in der Vikunja-Integration:

1. **Task-Update-Zuverlässigkeit:** Tools wie `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` senden jetzt immer das Pflichtfeld `title` an die Vikunja-API, auch wenn Sie nur einzelne Felder (z.B. nur die Priorität oder eine Erinnerung) ändern möchten. Dies verhindert Fehler der Art `title: non zero value required`.

2. **Projekt-Management vervollständigt:** `list_projects` zeigt nun auch Beschreibung (`description`) und Projekt-Kennung (`identifier`) an, und `create_project` erlaubt es, direkt eine Projektfarbe (`hex_color`) zu setzen. Sie können Projekte damit vollständiger über KI-Assistenten verwalten.

## MCP-Tools

Diese Tools wurden überarbeitet oder erweitert:

| Tool | Änderung | Effekt |
|---|---|---|
| `update_task` | Sendet vollständigen Basis-Payload mit `title` | Teil-Updates (z.B. nur `priority` ändern) schlagen nicht mehr fehl |
| `set_reminders` | Ergänzt `title` im Payload | Erinnerungen können zuverlässig geändert werden |
| `complete_task` | Ergänzt `title` im Payload | Task-Status zuverlässig änderbar |
| `move_task_to_project` | Ergänzt `title` im Payload | Aufgaben zuverlässig verschiebbar |
| `list_projects` | Neu: `identifier`, `description` in Rückgabe | Sie sehen projektinterne Kennungen und Beschreibungen |
| `create_project` | Neu: optionaler Parameter `hex_color` | Sie können beim Anlegen direkt eine Farbe (z.B. `ff0000` für Rot) setzen |

## Voraussetzungen

- Vikunja-API-Token mit Lese- und Schreibrechten auf Projekte und Tasks (wie bisher).
- Keine zusätzlichen Umgebungsvariablen nötig.

## Schritt-für-Schritt Demo

### Szenario 1: Task mit Teil-Update (z.B. nur Priorität ändern)

**Vorher (v0.2.x):** Würde fehlschlagen, wenn Sie nur `priority` übergeben.
**Nachher (v0.3.0+):**

```python
# Im MCP Inspector oder Claude Desktop:
update_task(task_id=42, priority=3)
# → Sendet vollständigen Payload mit title, description, done, priority, dates
# → Update erfolgt zuverlässig
```

### Szenario 2: Erinnerung für eine Task setzen

```python
set_reminders(task_id=42, reminders=["2026-06-25T10:00:00Z"])
# → title wird jetzt immer mitgesendet
# → Vikunja akzeptiert das Update auch wenn nur reminders geändert werden
```

### Szenario 3: Task abschließen

```python
complete_task(task_id=42, comment="Finished!")
# → title wird mitgesendet
# → Task wird zuverlässig auf done=true gesetzt
```

### Szenario 4: Task in anderes Projekt verschieben

```python
move_task_to_project(task_id=42, project_id=7)
# → title wird mitgesendet
# → Task wechselt zuverlässig das Projekt
```

### Szenario 5: Projekte mit Details auflisten

```python
list_projects()
# → Rückgabe enthält jetzt auch:
# {
#   "id": 1,
#   "title": "Backlog",
#   "identifier": "BL",        ← neu
#   "description": "Alle künftigen Tasks",  ← neu
#   "hex_color": "ff0000",
#   "parent_project_id": 0,
#   "is_archived": false
# }
```

### Szenario 6: Projekt mit Farbe anlegen

```python
create_project(
  title="Urgent",
  description="High-priority tasks",
  hex_color="ff0000"  # ← neu, optional
)
# → Projekt wird angelegt und die Farbe sofort gesetzt
```

## Bekannte Einschränkungen

- `identifier` ist ein read-only Feld in Vikunja und wird automatisch vergeben. Sie können es nicht beim Anlegen oder Update setzen.
- Die `hex_color` muss als hexadezimaler RGB-Wert (z.B. `ff0000` für Rot) angegeben werden.
- Die Annahme, dass `title` als Pflichtfeld bei Task-Updates verlangt wird, ist durch die Analogie zu `update_project` gut begründet, wurde aber bisher nur gegen Tests, nicht gegen eine echte Vikunja-Instanz validiert. Falls Ihre Instanz anders konfiguriert ist, können Sie diesen Hinweis ignorieren — das zusätzliche `title` im Payload ist harmlos.
