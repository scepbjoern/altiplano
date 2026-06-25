# Docker Operations Guide - Altiplano MCP

Dieser Guide beschreibt den Betrieb des Altiplano MCP-Servers als eigenständigen Docker-Container. Er richtet sich an Umgebungen (z.B. Host-VMs, LXC-Container), in denen der Server als Remote-HTTP-Endpunkt (SSE) für LLM-Clients betrieben werden soll.

---

## Inhaltsverzeichnis
1. [Zusammenspiel der Dateien (Kurzübersicht)](#1-zusammenspiel-der-dateien-kurzübersicht)
2. [Initiale Einrichtung (Setup)](#2-initiale-einrichtung-setup)
3. [Updates und zukünftige Code-Änderungen einspielen](#3-updates-und-zukünftige-code-änderungen-einspielen)
4. [Logs und Troubleshooting](#4-logs-und-troubleshooting)

---

## 1. Zusammenspiel der Dateien (Kurzübersicht)

Das Deployment-Setup ist minimalistisch und stützt sich auf folgende Dateien:

- **`Dockerfile` (im Root):** Definiert, WIE der Container gebaut wird. Es basiert auf einem leichtgewichtigen Alpine-Image mit `uv`, kopiert den Code, installiert die Abhängigkeiten isoliert im `.venv` und konfiguriert einen sicheren Non-Root-User.
- **`deploy/docker-compose.yml`:** Definiert, WAS läuft. Startet den Container, mappt den internen Port nach aussen und schleust Umgebungsvariablen durch.
- **`deploy/.env`:** Beinhaltet sämtliche Konfigurationen (Ports, Vikunja-API-Tokens, Transport-Protokoll, DNS-Rebinding-Einstellungen).

| Aktion | Dockerfile ausgeführt? |
|--------|------------------------|
| `docker compose up -d` | Nein (verwendet bestehendes Image, falls vorhanden) |
| `docker compose up -d --build` | Ja (baut das Image zwingend neu aus dem aktuellen Code) |

---

## 2. Initiale Einrichtung (Setup)

Diese Schritte werden einmalig auf dem Ziel-Host (LXC, VM) ausgeführt.

### 2.1 Verzeichnisstruktur und Code bereitstellen

```bash
# Verzeichnis für den Stack erstellen
sudo mkdir -p /opt/stacks/vikunja-mcp
cd /opt/stacks/vikunja-mcp

# Repository klonen
sudo git clone https://github.com/scepbjoern/altiplano.git .

# Berechtigungen setzen (optional, je nach Setup)
sudo chown -R $(id -u):$(id -g) /opt/stacks/vikunja-mcp
```

### 2.2 Konfiguration (.env) erstellen

Das Setup nutzt den `deploy/` Ordner für die Orchestrierung:

```bash
cd deploy

# .env aus der Vorlage kopieren
cp .env.example .env

# Wichtige Anpassungen in .env vornehmen:
nano .env
```

**Zwingend anzupassende Werte in `.env`:**
- `VIKUNJA_URL`: Die Basis-URL deiner Vikunja-Instanz, inklusive `/api/v1` (z.B. `https://todo.meinedomain.ch/api/v1`).
- `VIKUNJA_API_TOKEN`: Ein valider API-Token aus Vikunja (mit den entsprechenden Rechten für Projekte/Tasks).
- `FASTMCP_DISABLE_DNS_REBINDING`: Standardmäßig auf `true`. Dies ist **empfohlen**, wenn der Server hinter einem Reverse Proxy (z.B. Nginx, Cloudflare Tunnels) betrieben wird, da der Host-Header sonst geblockt wird.
- *(Optional)* `CF_CLIENT_ID` / `CF_CLIENT_SECRET`: Falls deine Vikunja-Instanz hinter Cloudflare Access (Zero Trust) liegt, musst du hier die Service Token Credentials hinterlegen. Der MCP-Server hängt diese dann bei jeder Anfrage an Vikunja an.

### 2.3 Container bauen und starten

Da wir den Code frisch geklont haben, müssen wir das Image bauen und den Container starten:

```bash
# Im deploy/ Verzeichnis ausführen:
docker compose up -d --build

# Status prüfen (sollte "Up" sein)
docker compose ps
```

### 2.4 Verifizierung / Reverse Proxy

Prüfe lokal auf dem Host, ob der Server erreichbar ist:
```bash
curl -i http://localhost:6274/sse
```
*Erwartet wird eine Antwort mit Status `200 OK` und `Content-Type: text/event-stream`.*

**Cloudflare / Reverse Proxy Konfiguration:**
Leite Anfragen an z.B. `mcp-tasks.melbjo.win` auf `http://<IP-des-Hosts>:6274` weiter. Der LLM-Client (z.B. ChatGPT, Claude) kommuniziert dann über diese externe URL mit dem SSE-Endpunkt.

---

## 3. Updates und zukünftige Code-Änderungen einspielen

Wenn zukünftige Code-Änderungen (neue Features, Tool-Anpassungen, Bugfixes) auf GitHub gepusht wurden und auf dem Server ausgerollt werden sollen:

### 3.1 Code aktualisieren

Wechsle in das Root-Verzeichnis des Stacks und ziehe die neuesten Änderungen vom `main`-Branch:

```bash
cd /opt/stacks/vikunja-mcp
git pull origin main
```

### 3.2 Container neu bauen und neustarten

Da sich der Python-Code in `server.py` oder die Abhängigkeiten in `uv.lock` geändert haben, **muss** das Docker-Image zwingend neu gebaut werden. 
*Nur `docker compose restart` reicht nicht aus, da die Änderungen sonst nicht in den Container übernommen werden.*

Wechsle in den `deploy/`-Ordner und führe den Build-Prozess aus:

```bash
cd deploy
docker compose up -d --build
```
> **Tipp:** Durch den Schalter `--build` erkennt Docker Compose automatisch, dass ein neues Image gebaut werden muss. Der laufende Container wird erst gestoppt, wenn der Build erfolgreich war. Die Ausfallzeit (Downtime) beträgt somit nur wenige Sekunden.

### 3.3 Alte Images aufräumen (optional)

Da bei jedem Build ein neues Image entsteht, sammeln sich mit der Zeit ungenutzte Images (Dangling Images) an. Diese können bei Bedarf bereinigt werden, um Speicherplatz zu sparen:

```bash
docker image prune -f
```

---

## 4. Logs und Troubleshooting

### Logs prüfen

Um zu sehen, was im MCP-Server passiert (inkl. eingehender Tool-Aufrufe oder Fehlermeldungen der Vikunja-API):

```bash
cd /opt/stacks/vikunja-mcp/deploy
docker compose logs -f app
```

### Typische Fehlerbilder

1. **Host rejected / 403 Forbidden (FastMCP / SSE URL)**
   - **Ursache:** Das DNS-Rebinding-Protection-Feature von FastMCP blockiert die Anfrage, weil der Host-Header der URL nicht `localhost` ist.
   - **Lösung:** Stelle sicher, dass in der `deploy/.env` die Variable `FASTMCP_DISABLE_DNS_REBINDING=true` gesetzt ist (und starte mit `docker compose up -d` neu). Alternativ kann `FASTMCP_ALLOWED_HOSTS` gesetzt werden.

2. **Connection Refused / Timeout zur Vikunja-API**
   - **Ursache:** Der MCP-Server erreicht Vikunja nicht.
   - **Lösung:** Prüfe die `VIKUNJA_URL` in der `.env`. Teste vom Host-System aus, ob sich Vikunja anpingen/aufrufen lässt.

3. **HTTP 401 Unauthorized von Vikunja in den Logs**
   - **Ursache:** Der MCP-Server kann sich nicht authentifizieren.
   - **Lösung:** Prüfe, ob der `VIKUNJA_API_TOKEN` korrekt kopiert wurde und nicht abgelaufen ist. Falls Vikunja zusätzlich von Cloudflare geschützt wird, stelle sicher, dass `CF_CLIENT_ID` und `CF_CLIENT_SECRET` gesetzt sind.
