# LLM-Client Setup Guide – Altiplano MCP Server

Dieser Guide beschreibt, wie du die gängigen LLM-Clients so konfigurierst, dass sie
den Altiplano MCP-Server über die externe HTTPS-URL (`https://mcp-tasks.melbjo.win/sse`)
nutzen können. Da der Server hinter Cloudflare Access (Zero Trust) abgesichert ist,
müssen bei jeder Anfrage die Service-Token-Header mitgeschickt werden.

**Voraussetzung:** Du hast die Cloudflare Access Application und den Service Token gemäss
[docker-operations.md](./docker-operations.md) bereits eingerichtet und besitzt:
- `CF-Access-Client-Id`: `<deine-client-id>`
- `CF-Access-Client-Secret`: `<dein-client-secret>`

---

## Inhaltsverzeichnis
1. [Claude Desktop (Windows / macOS)](#1-claude-desktop-windows--macos)
2. [Claude Web (claude.ai)](#2-claude-web-claudeai)
3. [ChatGPT Web (chat.openai.com)](#3-chatgpt-web-chatopenaicom)
4. [OpenAI Codex CLI](#4-openai-codex-cli)
5. [Verifikation der Verbindung](#5-verifikation-der-verbindung)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Claude Desktop (Windows / macOS)

Claude Desktop unterstützt keine nativen HTTP-Header-Felder in seiner Konfiguration
für Remote-Server. Als Workaround verwenden wir das `mcp-remote`-Paket, das lokal als
Proxy-Prozess läuft und die Verbindung zur Remote-URL herstellt – inklusive Header-Injektion.

### 1.1 Voraussetzung: Node.js

`mcp-remote` wird via `npx` ausgeführt und erfordert Node.js (empfohlen: LTS-Version).
Prüfe, ob es installiert ist:
```bash
node --version
```
Falls nicht, lade es von [nodejs.org](https://nodejs.org) herunter und installiere es.

### 1.2 Konfigurationsdatei öffnen

Öffne die Konfigurationsdatei von Claude Desktop:

| Betriebssystem | Pfad |
|---|---|
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |

Alternativ: Claude Desktop → **Settings** → **Developer** → **Edit Config**.

### 1.3 MCP-Server Eintrag hinzufügen

Füge folgenden Eintrag in das `mcpServers`-Objekt ein (ersetze die Platzhalter). 

**Wichtig für Windows-Nutzer:** Da `npx` unter Windows ein Batch-Skript ist und der Node-Installationspfad oft Leerzeichen enthält (z. B. `C:\Program Files\nodejs`), muss der Befehl über `cmd /c` aufgerufen werden, um Pfadfehler (`C:\Program` not found) zu vermeiden.

**Konfiguration (Windows):**
```json
{
  "mcpServers": {
    "altiplano-vikunja": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "mcp-remote",
        "https://mcp-tasks.melbjo.win/sse",
        "--header",
        "CF-Access-Client-Id: <deine-client-id>",
        "--header",
        "CF-Access-Client-Secret: <dein-client-secret>"
      ]
    }
  }
}
```

**Konfiguration (macOS / Linux):**
```json
{
  "mcpServers": {
    "altiplano-vikunja": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp-tasks.melbjo.win/sse",
        "--header",
        "CF-Access-Client-Id: <deine-client-id>",
        "--header",
        "CF-Access-Client-Secret: <dein-client-secret>"
      ]
    }
  }
}
```

> **Hinweis:** Falls bereits andere MCP-Server konfiguriert sind, füge den neuen Eintrag
> innerhalb des bestehenden `mcpServers`-Objekts hinzu (durch Komma getrennt).

### 1.4 Claude Desktop neu starten

Claude Desktop **vollständig beenden** (nicht nur das Fenster schliessen) und neu starten.
Nach dem Start sollte unter **Settings → Developer** der Server `altiplano-vikunja` als
verbunden angezeigt werden.

---

## 2. Claude Web (claude.ai)

In neueren Versionen der Claude-Web-Benutzeroberfläche wurden „Integrations“ durch den Bereich **Customize (Anpassen)** ersetzt. Für Einzelbenutzer ist dort derzeit nur das Hochladen lokaler Plugins möglich; die direkte Konfiguration von benutzerdefinierten Remote-MCP-Servern per URL ist in der Web-Oberfläche für Standard-Accounts aktuell **nicht direkt verfügbar**.

Zudem besteht bei Cloudflare Managed OAuth das bekannte Risiko eines ungelösten Bugs im OAuth-Handshake von Claude Web ([Anthropic Issue #410](https://github.com/anthropics/claude-ai-mcp/issues/410)), welcher dazu führen kann, dass der Connector hängen bleibt.

**Empfehlung:** Nutzen Sie für Claude weiterhin **Claude Desktop** (Abschnitt 1), da hier die verlässliche Verbindung über einen lokalen Proxy und Service-Token läuft.

---

## 3. ChatGPT Web (chatgpt.com)

ChatGPT unterstützt Remote-MCP-Server über das Cloudflare MCP Server Portal unter Verwendung von **Managed OAuth**. Dadurch ist kein unsicherer Bypass mehr nötig und der Benutzer wird beim Verbinden sicher über Cloudflare Access authentifiziert.

**Einrichtungsschritte:**

1. Gehen Sie in **ChatGPT Web** zu **Settings** (Einstellungen) → **Connectors** (Konnektoren).
2. Aktivieren Sie den **Developer Mode** (Entwicklermodus).
3. Klicken Sie auf **Create** / **+ Custom Connector**.
4. Geben Sie folgende Details ein:
   * **Name**: `Vikunja Altiplano`
   * **Connection**: Wählen Sie `Server URL` und tragen Sie die Portal-Client-URL ein:
     **`https://mcp.melbjo.win/mcp`** *(WICHTIG: Das Suffix `/mcp` am Ende ist zwingend erforderlich, damit der Streamable-HTTP-Transport genutzt wird).*
   * **Authentication**: Wählen Sie **OAuth** aus der Liste.
5. ChatGPT führt im Hintergrund die Auto-Discovery durch und lädt alle nötigen OAuth-Endpunkte selbstständig vom Portal.
6. Setzen Sie das Häkchen bei *„I understand and want to continue“* und klicken Sie auf **Create**.
7. Sie werden nun zur Cloudflare Access Login-Seite weitergeleitet. Authentifizieren Sie sich (z. B. per One-Time-PIN).
8. Nach erfolgreicher Anmeldung leitet Cloudflare Sie zurück zu ChatGPT. Der Connector ist jetzt verbunden und die Tools sind aktiv.
9. Starten Sie einen Chat und bitten Sie die KI: *„Zeige meine Vikunja Projekte“*, um die Verbindung zu verifizieren.

---

## 4. OpenAI Codex (CLI & Desktop)

Sowohl das Codex CLI (`codex`) als auch die Codex Desktop App bieten native Unterstützung für Remote-MCP-Server mit benutzerdefinierten HTTP-Headern über eine zentrale `config.toml`-Konfigurationsdatei.

### 4.1 Konfigurationsdatei öffnen

Die Konfigurationsdatei befindet sich im Benutzerverzeichnis unter `.codex/config.toml`.

**Unter Windows (PowerShell):**
```powershell
# Erstellt das Verzeichnis falls nicht vorhanden und öffnet die Datei im Editor
New-Item -ItemType Directory -Force -Path "$HOME\.codex"
notepad "$HOME\.codex\config.toml"
```

**Unter Windows (CMD):**
```cmd
mkdir "%USERPROFILE%\.codex"
notepad "%USERPROFILE%\.codex\config.toml"
```

**Unter macOS / Linux:**
```bash
mkdir -p ~/.codex
nano ~/.codex/config.toml
```

### 4.2 MCP-Server Eintrag hinzufügen

Da Codex standardmäßig local-spawning MCP-Server erwartet, binden wir die Remote-Verbindung über den gleichen `mcp-remote`-Proxy ein wie bei Claude Desktop.

Füge folgenden Abschnitt in die `config.toml` ein:

**Unter Windows:**
```toml
[mcp_servers.altiplano-vikunja]
command = "cmd"
args = [
  "/c",
  "npx",
  "-y",
  "mcp-remote",
  "https://mcp-tasks.melbjo.win/sse",
  "--header",
  "CF-Access-Client-Id: <deine-client-id>",
  "--header",
  "CF-Access-Client-Secret: <dein-client-secret>"
]
```

**Unter macOS / Linux:**
```toml
[mcp_servers.altiplano-vikunja]
command = "npx"
args = [
  "-y",
  "mcp-remote",
  "https://mcp-tasks.melbjo.win/sse",
  "--header",
  "CF-Access-Client-Id: <deine-client-id>",
  "--header",
  "CF-Access-Client-Secret: <dein-client-secret>"
]
```

### 4.3 Verbindung testen

Testen Sie die Verbindung über das CLI:
```bash
# Zeigt die Liste der konfigurierten MCP-Server an
codex mcp list
```

---

## 5. Verifikation der Verbindung

Unabhängig vom Client kannst du die Erreichbarkeit des Servers zunächst lokal testen,
indem du `curl` mit den entsprechenden Headern verwendest:

```bash
curl -i \
  -H "CF-Access-Client-Id: <deine-client-id>" \
  -H "CF-Access-Client-Secret: <dein-client-secret>" \
  https://mcp-tasks.melbjo.win/sse
```

**Erwartete Antwort:**
- HTTP-Statuscode: `200 OK`
- `Content-Type: text/event-stream`
- Die Verbindung bleibt offen und streamt SSE-Events.

Ohne die korrekten Header antwortet Cloudflare mit `403 Forbidden`.

---

## 6. Troubleshooting

### `403 Forbidden` vom Server

Die Cloudflare Access Policy blockiert die Anfrage.

- **Prüfe:** Sind `CF-Access-Client-Id` und `CF-Access-Client-Secret` korrekt und vollständig?
- **Prüfe:** Ist der Service Token in Cloudflare noch aktiv (nicht abgelaufen)?
- **Prüfe:** Ist der Service Token in der Access Policy der Application eingetragen?

### `Connection refused` / Timeout

Der MCP-Container läuft möglicherweise nicht.

- Überprüfe den Container-Status auf dem Host: `docker compose ps`
- Prüfe die Tunnel-Konfiguration in Cloudflare Zero Trust.

### `mcp-remote` Fehler bei Claude Desktop

- Stelle sicher, dass Node.js installiert und `npx` im PATH verfügbar ist.
- Starte Claude Desktop **vollständig neu** nach jeder Änderung an der Config-Datei.
- Prüfe in den Claude Desktop Developer-Einstellungen die Fehlerausgabe des MCP-Servers.

### `ModuleNotFoundError` / Server startet nicht

- Der MCP-Container muss neu gebaut werden. Folge den Schritten in Abschnitt 3 des
  [docker-operations.md](./docker-operations.md).
