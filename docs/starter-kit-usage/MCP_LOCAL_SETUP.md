# MCP-Server lokal ausführen und testen

Dieses Dokument beschreibt, wie ihr euren Altiplano MCP-Server lokal ausführen und testen könnt.

---

## 1. Lokale Ausführung des Servers

Der MCP-Server kommuniziert standardmäßig über Standard-Input/-Output (stdio). Ihr könnt ihn direkt über `uv` starten:

```bash
uv run altiplano
```

Der Server läuft nun und wartet auf MCP-Nachrichten über die Standardeingabe. Drückt `Ctrl+C`, um ihn zu beenden.

---

## 2. Testen mit dem MCP Inspector (Empfohlen)

Der MCP Inspector ist ein interaktives Web-Interface, das von Anthropic bereitgestellt wird, um MCP-Server direkt über stdio zu inspizieren und zu testen.

### Starten des Inspectors

Führt den folgenden Befehl im Wurzelverzeichnis eures Projekts aus:

```bash
npx @modelcontextprotocol/inspector uv run altiplano
```

Dieser Befehl:
1. Lädt den Inspector herunter und startet ihn.
2. Startet euren lokalen Altiplano MCP-Server als Subprozess.
3. Öffnet eine Weboberfläche im Browser (standardmäßig unter `http://localhost:3000`).

In der Weboberfläche könnt ihr:
- Alle registrierten Tools auflisten.
- Tools mit benutzerdefinierten Argumenten aufrufen und die JSON-Antworten einsehen.
- Die genaue JSON-RPC-Kommunikation mitverfolgen (sehr nützlich zum Debuggen).

---

## 3. Einbinden in Claude Desktop

Um den lokalen MCP-Server in eurer alltäglichen Arbeit mit Claude Desktop zu nutzen, müsst ihr ihn in der Konfigurationsdatei registrieren.

### Speicherort der Konfigurationsdatei

Je nach Betriebssystem liegt die Konfigurationsdatei `claude_desktop_config.json` unter:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Konfiguration hinzufügen

Öffnet die Datei und fügt euren lokalen MCP-Server unter `mcpServers` hinzu. Ersetzt `E:/bjoer/Documents/repos/altiplano` durch den tatsächlichen absoluten Pfad zu eurem Projektverzeichnis:

```json
{
  "mcpServers": {
    "altiplano-local": {
      "command": "uv",
      "args": [
        "--directory",
        "E:/bjoer/Documents/repos/altiplano",
        "run",
        "altiplano"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Stellt sicher, dass die Umgebungsvariablen `VIKUNJA_URL` und `VIKUNJA_API_TOKEN` entweder in eurem System global gesetzt sind, in der Konfigurationsdatei über ein `"env"`-Objekt übergeben werden, oder im lokalen Config-Verzeichnis (`~/.config/altiplano/env`) hinterlegt sind.

Beispiel mit Umgebungsvariablen direkt in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "altiplano-local": {
      "command": "uv",
      "args": [
        "--directory",
        "E:/bjoer/Documents/repos/altiplano",
        "run",
        "altiplano"
      ],
      "env": {
        "VIKUNJA_URL": "https://todo.example.com/api/v1",
        "VIKUNJA_API_TOKEN": "tk_xxx"
      }
    }
  }
}
```

Nach dem Speichern der Konfiguration müsst ihr Claude Desktop neu starten. Anschließend steht euch ein kleines Stecker-Symbol zur Verfügung, das anzeigt, dass Altiplano geladen wurde.
