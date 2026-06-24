# Developer Notes: list_projects Hex Color

## Überblick

Das Feature fügt die Rückgabe des Attributes `hex_color` zum `list_projects` Tool des MCP-Servers hinzu. Es sorgt dafür, dass die Farbe, die Vikunja für Projekte speichert, nahtlos an den MCP-Client übermittelt wird.

## Referenzen

- Plan: `docs/project/features/list-projects-hex-color/plan-v001.md`
- PRD: `docs/project/prds/vikunja-mcp-server-v004.md`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| [src/altiplano/server.py](file:///e:/bjoer/Documents/repos/altiplano/src/altiplano/server.py) | `list_projects` holt `hex_color` per `.get("hex_color", "")` aus dem API-Response-Payload und reicht es im Rückgabe-Dictionary weiter. |
| [tests/test_server.py](file:///e:/bjoer/Documents/repos/altiplano/tests/test_server.py) | API-Mock-Daten und Assertions im Test `test_tool_list_projects` wurden um `hex_color` erweitert. |

## Architektur und Datenfluss

Wenn `list_projects` aufgerufen wird, sendet der MCP-Server einen GET-Request an `/projects`. Die Vikunja-API liefert eine Liste aller Projekte zurück. Jedes Projekt enthält optionale Farbcodes unter dem Schlüssel `hex_color`. Der MCP-Server filtert die relevanten Felder heraus und stellt das Ergebnis dem MCP-Client bereit.

## Datenmodell und API-Mapping

Die Transformation des API-Objekts zum MCP-Resultat sieht nun wie folgt aus:
```python
{
    "id": p["id"],
    "title": p["title"],
    "parent_project_id": p.get("parent_project_id", 0),
    "is_archived": p.get("is_archived", False),
    "hex_color": p.get("hex_color", ""),  # <-- Neu hinzugewügt
}
```

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `uv run pytest` | Bestanden. Der Test `test_tool_list_projects` mockt den HTTPX-Client und stellt sicher, dass `hex_color` in der Ausgabe vorhanden ist und mit dem Mock übereinstimmt. |

## Betriebs- und Setup-Hinweise

Keine neuen Konfigurationswerte erforderlich. Der API-Token benötigt lediglich die bereits vorhandenen Leserechte für Projekte.

## Wartungshinweise

- Sollte ein Projekt in Vikunja keine Farbe besitzen, wird standardmäßig ein leerer String `""` zurückgegeben. Dies verhindert Fehler im JSON-Parser des Clients und stellt eine konsistente API-Schnittstelle sicher.
- Farbänderungen können mit dem Tool `update_project` (separates Feature) durchgeführt werden, welches den Parameter `hex_color` ebenfalls akzeptiert.

## Bekannte Einschränkungen

- Hex-Farben werden ohne das führende Gatter-Zeichen `#` gespeichert und geliefert (z. B. `00ff00` statt `#00ff00`), was dem Vikunja-API-Standard entspricht. Client-Systeme müssen dies bei der Weiterverarbeitung berücksichtigen.
