# User Guide: update_project Tool

## Überblick

Das `update_project` Tool ermöglicht es, bestehende Projekte in deiner Vikunja-Instanz über den MCP-Server zu aktualisieren. Du kannst damit Projektnamen, Beschreibungen, Farben und die Projekt-Hierarchie (Verschachtelung) anpassen.

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `update_project` | Aktualisiert ein bestehendes Projekt. Nur die übergebenen Felder werden geändert. | `project_id: int` (Pflicht)<br>`title: str` (Optional)<br>`description: str` (Optional)<br>`hex_color: str` (Optional)<br>`parent_project_id: int` (Optional) | `dict` (Das aktualisierte Projekt-Objekt von Vikunja) |

## Voraussetzungen

- Ein gültiger Vikunja API-Token mit Schreibrechten auf Projekte.
- Die ID des zu aktualisierenden Projekts (`project_id`).

## Schritt-für-Schritt Demo

1. Starte den MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. Öffne den Inspector im Browser (z.B. `http://localhost:5173`).
3. Wähle das Tool `update_project` aus.
4. Gib folgende Argumente ein:
   * `project_id`: `1` (oder eine andere gültige Projekt-ID)
   * `title`: `"Mein aktualisiertes Projekt"`
   * `hex_color`: `"ff0000"` (Farbe auf Rot setzen)
5. Klicke auf **Run Tool**. Das Projekt wird in Vikunja aktualisiert und das geänderte Objekt wird zurückgegeben.

## Bekannte Einschränkungen

- Archivierung (`is_archived`) und Löschen von Projekten sind über dieses Tool nicht möglich (Out of Scope für dieses MVP-Feature).
