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

Füge folgenden Eintrag in das `mcpServers`-Objekt ein (ersetze die Platzhalter):

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

Claude Web unterstützt Remote-MCP-Server über die **Integrations**-Funktion im Einstellungsmenü.
Diese Funktion ist nur für **Pro/Team/Enterprise**-Accounts verfügbar.

> **Einschränkung:** Claude Web erlaubt aktuell **keine** Injektion von benutzerdefinierten
> HTTP-Headern über die Web-UI. Eine direkte Verbindung zum Cloudflare-gesicherten Endpunkt
> ist daher **nur möglich, wenn die Access Policy auf `Bypass` gestellt wird** (nicht empfohlen)
> oder du einen lokalen Proxy (ähnlich wie bei Claude Desktop) auf deinem PC betreibst.
>
> **Empfehlung:** Verwende stattdessen **Claude Desktop** (Abschnitt 1) für eine sichere,
> header-authentifizierte Verbindung.

Falls du den Endpunkt temporär ohne Cloudflare Access (nur für Tests aus einem vertrauenswürdigen
Netzwerk) nutzen möchtest:
1. Gehe zu **claude.ai** → **Settings** → **Integrations**.
2. Klicke auf **Add Integration**.
3. Gib die URL `https://mcp-tasks.melbjo.win/sse` ein.
4. Klicke auf **Connect**.

---

## 3. ChatGPT Web (chat.openai.com)

ChatGPT erlaubt das Hinzufügen von Remote-MCP-Servern über die **Connectors**-Funktion.
Diese ist für **Pro/Team/Enterprise/Edu**-Accounts mit aktiviertem **Developer Mode** verfügbar.

> **Einschränkung:** Wie Claude Web unterstützt die ChatGPT-Web-UI aktuell **keine** direkte
> Konfiguration von benutzerdefinierten HTTP-Headern (wie die Cloudflare Service Token Header).
> Das Verbinden eines Cloudflare-Access-gesicherten Endpunkts ist daher ohne Bypass **nicht
> direkt** über die Web-UI möglich.
>
> **Empfehlung:** Verwende **Claude Desktop** (Abschnitt 1) oder den **Codex CLI** (Abschnitt 4)
> für eine vollständig gesicherte Verbindung.

Falls du den Endpunkt für Tests ohne Cloudflare-Sicherung freischaltest:
1. Gehe zu **ChatGPT** → **Settings** → **Connectors**.
2. Aktiviere **Developer Mode**.
3. Klicke auf **Create** / **+ Custom Connector**.
4. Gib folgende Details ein:
   - **Name:** `Altiplano Vikunja MCP`
   - **URL:** `https://mcp-tasks.melbjo.win/sse`
   - **Transport:** `SSE`
   - **Authentication:** `None` (da Cloudflare Access die Authentifizierung übernimmt)
5. Bestätige mit „I trust this provider" und klicke auf **Create**.

---

## 4. OpenAI Codex CLI

Der Codex CLI (`codex`) bietet native Unterstützung für Remote-MCP-Server mit benutzerdefinierten
HTTP-Headern über seine `config.toml`-Konfigurationsdatei. Dies ist die **empfohlene Methode**
für Codex.

### 4.1 Konfigurationsdatei öffnen

```bash
# Datei öffnen (erstellen, falls nicht vorhanden)
nano ~/.codex/config.toml
```

### 4.2 MCP-Server Eintrag hinzufügen

Füge folgenden Abschnitt in die `config.toml` ein:

```toml
[mcp_servers.altiplano-vikunja]
url = "https://mcp-tasks.melbjo.win/sse"

# Option A: Header direkt als statische Werte (einfacher, aber Secret im Klartext)
http_headers = { "CF-Access-Client-Id" = "<deine-client-id>", "CF-Access-Client-Secret" = "<dein-client-secret>" }

# Option B (empfohlen): Header aus Umgebungsvariablen lesen (Secret nicht im Klartext)
# env_http_headers = { "CF-Access-Client-Id" = "CF_CLIENT_ID_VAR", "CF-Access-Client-Secret" = "CF_CLIENT_SECRET_VAR" }
```

> **Sicherheitshinweis:** Bevorzuge **Option B** (`env_http_headers`), um das Client Secret
> nicht im Klartext in der Konfigurationsdatei zu speichern. Setze dazu die entsprechenden
> Umgebungsvariablen in deiner Shell-Konfiguration (`.bashrc`, `.zshrc` etc.):
>
> ```bash
> export CF_CLIENT_ID_VAR="<deine-client-id>"
> export CF_CLIENT_SECRET_VAR="<dein-client-secret>"
> ```

### 4.3 Verbindung testen

```bash
codex --mcp-server altiplano-vikunja list-tools
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
