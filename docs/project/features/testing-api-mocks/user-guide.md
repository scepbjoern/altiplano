# User Guide: Testing & API-Mocks

## Überblick

Dieses Feature dient der Absicherung der Codebasis für Entwickler. Es stellt keine direkten Endanwender-Tools über das Model Context Protocol (MCP) zur Verfügung, sondern etabliert ein stabiles Test- und Mocking-Setup. Dadurch können neue MCP-Tools entwickelt und getestet werden, ohne echte Anfragen an die produktive Vikunja-Instanz zu senden.

## MCP-Tools

*Nicht relevant.* Dieses Feature fügt keine neuen MCP-Tools hinzu. Die bestehenden Tools bleiben unverändert.

## Voraussetzungen

*Nicht relevant.* Es sind keine speziellen Laufzeit-Konfigurationen für Endanwender erforderlich.

## Schritt-für-Schritt Demo

Um die Funktionsfähigkeit des Test-Setups zu demonstrieren:

1. Navigiere im Terminal in das Projektverzeichnis.
2. Führe die Testsuite mit folgendem Befehl aus:
   ```bash
   uv run pytest
   ```
3. Das Testergebnis zeigt, dass die Tool-Tests (wie `test_tool_list_projects`) erfolgreich gegen simulierte API-Antworten ausgeführt werden, ohne Netzwerktraffic zu erzeugen.

## Bekannte Einschränkungen

- Die Tests simulieren die API-Antworten statisch und prüfen nicht das tatsächliche Verhalten einer Live-Vikunja-Instanz (dafür ist der MCP Inspector gedacht).
