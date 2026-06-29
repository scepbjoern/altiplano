# User Guide: Project Identifier

## Überblick

Dieses Feature ermöglicht es dem MCP-Server, das Feld `identifier` bei Vikunja-Projekten vollständig zu unterstützen. Nutzer können nun beim Erstellen oder Aktualisieren eines Projekts einen sprechenden Project Identifier (z. B. `SHOP` oder `CORP`) vergeben. Vikunja verwendet diesen Identifier, um neu erstellten Aufgaben in diesem Projekt automatisch lesbare Task-IDs im Format `IDENTIFIER-NUMMER` (z. B. `SHOP-12`) zuzuweisen.

## MCP-Tools

Das Feature erweitert die zwei folgenden MCP-Tools um den Parameter `identifier`:

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|
| `create_project` | Erstellt ein neues Projekt (Board). | `title: str`<br>`parent_project_id: int \| None = None`<br>`description: str \| None = None`<br>`hex_color: str \| None = None`<br>`identifier: str \| None = None` | Das neu erstellte Projekt als Dictionary. |
| `update_project` | Aktualisiert die Eigenschaften eines bestehenden Projekts. | `project_id: int`<br>`title: str \| None = None`<br>`description: str \| None = None`<br>`hex_color: str \| None = None`<br>`parent_project_id: int \| None = None`<br>`identifier: str \| None = None` | Das aktualisierte Projekt als Dictionary. |

## Voraussetzungen

- **Vikunja-Instanz:** Vikunja unterstützt standardmässig Project Identifier ab Versionen, die dieses Feld in der API anbieten.
- **API-Berechtigungen:** Das verwendete Vikunja API-Token muss Schreibrechte (Write) für das jeweilige Projekt besitzen.

## Schritt-für-Schritt Demo

1. **MCP Server starten:** 
   Starte den MCP-Server lokal (z. B. via MCP Inspector):
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
2. **Projekt mit Identifier erstellen:**
   Rufe das Tool `create_project` im MCP Client auf:
   ```json
   {
     "title": "Shop Implementation",
     "identifier": "SHOP"
   }
   ```
   *Erwartetes Ergebnis:* Das Projekt wird in Vikunja erstellt. Du siehst in der Rückgabe das Feld `"identifier": "SHOP"`.
3. **Task-IDs prüfen:**
   Füge eine neue Aufgabe zu diesem Projekt hinzu. Vikunja weist ihr automatisch den Identifier zu, sodass die Aufgabe z. B. unter der ID `SHOP-1` aufrufbar ist.
4. **Identifier aktualisieren oder leeren:**
   Rufe das Tool `update_project` auf, um den Identifier zu ändern:
   ```json
   {
     "project_id": <ID>,
     "identifier": "STORE"
   }
   ```
   Oder um ihn komplett zu entfernen:
   ```json
   {
     "project_id": <ID>,
     "identifier": ""
   }
   ```

## Bekannte Einschränkungen

- **Validierungsregeln:** Der MCP-Server führt keine eigene clientseitige Syntaxprüfung (z. B. auf erlaubte Sonderzeichen oder maximale Länge) durch. Die Validierung wird direkt an die Vikunja-API delegiert, deren Fehlermeldungen transparent zurückgegeben werden.
