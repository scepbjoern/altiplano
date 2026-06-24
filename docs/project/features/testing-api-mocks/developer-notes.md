# Developer Notes: Testing & API-Mocks

## Überblick

Dieses Feature führt ein standardisiertes, asynchrones Mocking-Setup für automatisierte Tests mit `pytest` ein. Es stellt sicher, dass Tests für die MCP-Tools isoliert ausgeführt werden, ohne echte HTTP-Requests an eine Vikunja-Instanz abzusenden.

## Referenzen

- Plan: [plan-v001.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/testing-api-mocks/plan-v001.md)
- PRD: [vikunja-mcp-server-v004.md](file:///e:/bjoer/Documents/repos/altiplano/docs/project/prds/vikunja-mcp-server-v004.md)
- Relevante Guides: [KILO_INSTRUCTIONS.md](file:///e:/bjoer/Documents/repos/altiplano/KILO_INSTRUCTIONS.md)

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| `tests/test_server.py` | Import von `unittest.mock.patch` und `AsyncMock` sowie Definition des ersten gemockten Tool-Tests für `list_projects`. |

## Architektur und Datenfluss

Die asynchronen Aufrufe an die Vikunja-API werden zentral über die interne Funktion `_request()` in `src/altiplano/server.py` abgewickelt. 
In den Unittests patchen wir diese Funktion mithilfe von `@patch("altiplano.server._request", new_callable=AsyncMock)`. Der Mock liefert vordefinierte JSON-Strukturen zurück, die den echten API-Antworten von Vikunja entsprechen. Dadurch wird der gesamte HTTP-Verkehr über `httpx.AsyncClient` unterbunden.

## Datenmodell und API-Mapping

- Im Test `test_tool_list_projects` wird der Return-Value von `_request` auf eine Liste von Projekt-Dictionaries gesetzt.
- Der Test assertiert, dass die Python-Toolfunktion `list_projects` die Rohdaten korrekt verarbeitet und das erwartete Format zurückgibt.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| Automatischer Test | `uv run pytest` führt alle Tests erfolgreich aus. |
| Abdeckung | `test_tool_list_projects` validiert das Mocking-Setup sowie den Rückgabewert des Tools. |

## Betriebs- und Setup-Hinweise

*Nicht relevant.* Das Setup läuft rein über pytest im Entwicklungsmodus.

## Wartungshinweise

- Beim Hinzufügen oder Ändern von MCP-Tools müssen entsprechende asynchrone Tests unter Verwendung des Mock-Dekorators `@patch("altiplano.server._request", new_callable=AsyncMock)` in `tests/test_server.py` ergänzt werden (siehe *Brownfield-Pragmatismus* in `KILO_INSTRUCTIONS.md`).
- Es müssen keine externen Mocking-Bibliotheken wie `pytest-httpx` oder `respx` hinzugefügt werden, da das Patchen von `_request` ausreicht und Dependencies minimiert.

## Bekannte Einschränkungen

- Das Setup mockt die interne Funktion `_request` statt der eigentlichen HTTP-Ebene. Strukturänderungen an `_request` selbst erfordern Anpassungen in allen Mock-Testfällen.
