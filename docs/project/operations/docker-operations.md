# Docker Operations Guide - Altiplano MCP

Dieser Guide beschreibt den Betrieb des Altiplano MCP-Servers als eigenständigen Docker-Container. Er richtet sich an Umgebungen (z.B. Host-VMs, LXC-Container), in denen der Server als Remote-HTTP-Endpunkt (SSE) für LLM-Clients betrieben werden soll.

---

## Inhaltsverzeichnis
1. [Architektur & Naming Schema](#1-architektur--naming-schema)
2. [Zusammenspiel der Dateien (Kurzübersicht)](#2-zusammenspiel-der-dateien-kurzübersicht)
3. [Initiale Einrichtung (Setup)](#3-initiale-einrichtung-setup)
4. [Updates und zukünftige Code-Änderungen einspielen](#4-updates-und-zukünftige-code-änderungen-einspielen)
5. [Logs und Troubleshooting](#5-logs-und-troubleshooting)

---

## 1. Architektur & Naming Schema

Das Standardmuster für diesen MCP-Server lautet:

```text
ChatGPT / Claude / Codex
  ↓
Cloudflare MCP Server Portal        (OAuth / Managed Auth)
  ↓
Cloudflare MCP Server Registry      (intern)
  ↓
Cloudflare Access                   (schützt den direkten Origin)
  ↓
direkter MCP-Origin                 (z.B. https://tasks-mcp.melbjo.win/sse)
  ↓
lokaler MCP-Container               (Port 6274)
  ↓
lokale Backend-API                  (Vikunja API)
```

**Namensschema für Vikunja:**
- **Docker Stack:** `/opt/stacks/vikunja-mcp`
- **Container:** `vikunja-mcp`
- **Interner/LAN-Port:** `6274`
- **Direkte MCP-Origin-Domain:** `tasks-mcp.melbjo.win`
- **Direkter Origin Endpoint:** `https://tasks-mcp.melbjo.win/sse`
- **Cloudflare Access App:** `MCP Origin - Tasks`
- **Cloudflare Service Token:** `svc-mcp-tasks`
- **Cloudflare MCP Server:** `vikunja-mcp`
- **Cloudflare MCP Portal:** `tasks-mcp-portal`
- **Portal-Domain:** `tasks-mcp-portal.melbjo.win`
- **ChatGPT Connector Name:** `Vikunja Tasks`
- **Connector URL für ChatGPT:** `https://tasks-mcp-portal.melbjo.win/mcp`

> **WICHTIGER HINWEIS:** Der direkte Origin-Endpunkt (`https://tasks-mcp.melbjo.win/sse`) darf nicht ungeschützt öffentlich erreichbar sein. Der MCP-Server hat den Vikunja-API-Token konfiguriert und erlaubt jedem Besucher vollen Zugriff auf deine Vikunja-Daten, wenn er nicht durch Cloudflare Access blockiert wird.

---

## 2. Zusammenspiel der Dateien (Kurzübersicht)

Das Deployment-Setup ist minimalistisch und stützt sich auf folgende Dateien:

- **`Dockerfile` (im Root):** Definiert, WIE der Container gebaut wird. Es basiert auf einem leichtgewichtigen Alpine-Image mit `uv`, kopiert den Code, installiert die Abhängigkeiten isoliert im `.venv` und konfiguriert einen sicheren Non-Root-User.
- **`deploy/docker-compose.yml`:** Definiert, WAS läuft. Startet den Container, mappt den internen Port nach aussen und schleust Umgebungsvariablen durch.
- **`deploy/.env`:** Beinhaltet sämtliche Konfigurationen (Ports, Vikunja-API-Tokens, Transport-Protokoll, DNS-Rebinding-Einstellungen).

| Aktion | Dockerfile ausgeführt? |
|--------|------------------------|
| `docker compose up -d` | Nein (verwendet bestehendes Image, falls vorhanden) |
| `docker compose up -d --build` | Ja (baut das Image zwingend neu aus dem aktuellen Code) |

---

## 3. Initiale Einrichtung (Setup)

Diese Schritte werden einmalig auf dem Ziel-Host (LXC, VM) ausgeführt.

### 4.1 Verzeichnisstruktur und Code bereitstellen

```bash
# Verzeichnis für den Stack erstellen
sudo mkdir -p /opt/stacks/vikunja-mcp
cd /opt/stacks/vikunja-mcp

# Repository klonen
sudo git clone https://github.com/scepbjoern/altiplano.git .

# Berechtigungen setzen (optional, je nach Setup)
sudo chown -R $(id -u):$(id -g) /opt/stacks/vikunja-mcp
```

### 4.2 Konfiguration (.env) erstellen

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

### 4.3 Container bauen und starten

Da wir den Code frisch geklont haben, müssen wir das Image bauen und den Container starten:

```bash
# Im deploy/ Verzeichnis ausführen:
docker compose up -d --build

# Status prüfen (sollte "Up" sein)
docker compose ps
```

### 3.4 Verifizierung / Reverse Proxy

Prüfe lokal auf dem Host, ob der Server erreichbar ist:
```bash
curl -i http://localhost:6274/sse
```
*Erwartet wird eine Antwort mit Status `200 OK` und `Content-Type: text/event-stream`.*

**Cloudflare / Reverse Proxy Konfiguration & Sicherheit (WICHTIG):**

Da der MCP-Server in seiner `.env`-Datei bereits deinen `VIKUNJA_API_TOKEN` hinterlegt hat, hat jeder, der diesen MCP-Endpunkt erreicht, **vollen Zugriff auf deine Vikunja-Daten**. Es ist daher zwingend erforderlich, diesen Endpunkt abzusichern!

Wenn du Cloudflare nutzt, gehst du am besten wie folgt vor:

1. **Tunnel Route:** 
   Richte in Cloudflare Zero Trust unter *Networks -> Tunnels* eine Route für `tasks-mcp.melbjo.win` ein, die auf `http://<IP-des-Hosts>:6274` zeigt.

2. **Access Application anlegen:** 
   Gehe zu *Access -> Applications* und erstelle eine neue App mit dem Namen `MCP Origin - Tasks` für die Domain `tasks-mcp.melbjo.win`. Diese App soll zwei Arten von Zugriff erlauben:
   - Benutzerzugriff für deine persönliche E-Mail-Adresse.
   - Service-Token-Zugriff für maschinelle Clients und den Cloudflare MCP Server.

3. **Service Token erstellen (für den LLM-Client):**
   Da maschinelle Clients (z. B. Claude Desktop, Flowise, LangChain) keinen Web-Login ausführen können.
   - Gehe zu *Access -> Service Auth -> Service Tokens* und erstelle einen neuen Token mit dem Namen `svc-mcp-tasks`.
   - Kopiere dir die *Client ID* und das *Client Secret*.

4. **Access Policy definieren:**
   - Gehe zurück zu deiner erstellten Application `MCP Origin - Tasks`.
   - Erstelle eine neue Policy:
     - **Action:** `Service Auth`
     - **Include:** `Service Token` -> Wähle den Token `svc-mcp-tasks` aus.

5. **LLM-Client konfigurieren:**
   Wenn du nun deinen LLM-Client anweist, sich mit dem direkten MCP-Origin zu verbinden (die URL lautet dann `https://tasks-mcp.melbjo.win/sse`), musst du im Client konfigurieren, dass er bei jedem Request folgende HTTP-Header mitsendet:
   - `CF-Access-Client-Id: <deine-client-id>`
   - `CF-Access-Client-Secret: <dein-client-secret>`

Nur Anfragen, die diese Header besitzen, werden von Cloudflare an deinen MCP-Container durchgelassen.

### 3.5 MCP Server Portal (Managed OAuth) für Web-Clients (z.B. ChatGPT)

Für Web-Clients (wie ChatGPT Web) wird das Cloudflare MCP Server Portal mit Managed OAuth verwendet. ChatGPT verbindet sich nicht direkt mit dem Origin `tasks-mcp.melbjo.win/sse`, sondern mit dem Portal unter `tasks-mcp-portal.melbjo.win/mcp`. Das Portal fungiert als Gateway: Es authentifiziert den Benutzer per OAuth 2.1 und leitet die Anfragen über Custom Headers (Service-Token) an den direkten Altiplano-Origin weiter.

**Einrichtungsschritte im Cloudflare Zero Trust Dashboard:**

1. **MCP Server registrieren**:
   - Gehe zu **Access** → **AI Controls** → **MCP Servers**.
   - Klicke auf **Add MCP server**.
   - **Name**: `vikunja-mcp`
   - **HTTP URL**: `https://tasks-mcp.melbjo.win/sse`
   - **Authentication type**: Wähle **Custom headers** und füge folgende zwei Header hinzu:
     - Name: `CF-Access-Client-Id` / Value: *(Deine Service-Token Client-ID von svc-mcp-tasks)*
     - Name: `CF-Access-Client-Secret` / Value: *(Dein Service-Token Client-Secret von svc-mcp-tasks)*
   - Speichere den Server. Der Status sollte auf **Ready** wechseln und die Anzahl der Tools anzeigen.

2. **MCP Server Portal erstellen**:
   - Gehe zu **Access** → **AI Controls** → **MCP server portals** und klicke auf **Add MCP server portal**.
   - **Portal name**: `tasks-mcp-portal`
   - **Custom domain**: Subdomain `tasks-mcp-portal` der Domain `melbjo.win` (ergibt `tasks-mcp-portal.melbjo.win`).
   - **Turn on code mode**: **Deaktivieren (grau)**, damit die Vikunja-Tools der KI direkt als einzelne Werkzeuge zur Verfügung stehen.
   - **Select MCP Servers**: Wähle den zuvor registrierten Server `vikunja-mcp` aus.
   - **Access policies**: Erstelle eine Policy, die den Zugriff per One-Time-PIN (OTP) für deine E-Mail-Adresse freigibt.
   - **Managed OAuth (Beta)**: Aktiviere diese Option ganz unten und trage unter **Allowed redirect URIs** folgende Muster ein:
     - `https://chatgpt.com/*`
     - `https://claude.ai/*`
     - `https://partner.ocean.openai.com/*`
   - Speichere das Portal.

3. **Client-Konfiguration**:
   - Die Verbindungs-URL (Connector URL) für ChatGPT lautet künftig: **`https://tasks-mcp-portal.melbjo.win/mcp`** (das Suffix `/mcp` am Ende ist zwingend erforderlich).

---

## 4. Updates und zukünftige Code-Änderungen einspielen

Wenn zukünftige Code-Änderungen (neue Features, Tool-Anpassungen, Bugfixes) auf GitHub gepusht wurden und auf dem Server ausgerollt werden sollen:

### 4.1 Code aktualisieren

Wechsle in das Root-Verzeichnis des Stacks und ziehe die neuesten Änderungen vom `main`-Branch:

```bash
cd /opt/stacks/vikunja-mcp
git pull origin main
```

### 4.2 Container neu bauen und neustarten

Da sich der Python-Code in `server.py` oder die Abhängigkeiten in `uv.lock` geändert haben, **muss** das Docker-Image zwingend neu gebaut werden. 
*Nur `docker compose restart` reicht nicht aus, da die Änderungen sonst nicht in den Container übernommen werden.*

Wechsle in den `deploy/`-Ordner und führe den Build-Prozess aus:

```bash
cd deploy
docker compose up -d --build
```
> **Tipp:** Durch den Schalter `--build` erkennt Docker Compose automatisch, dass ein neues Image gebaut werden muss. Der laufende Container wird erst gestoppt, wenn der Build erfolgreich war. Die Ausfallzeit (Downtime) beträgt somit nur wenige Sekunden.

### 4.3 Alte Images aufräumen (optional)

Da bei jedem Build ein neues Image entsteht, sammeln sich mit der Zeit ungenutzte Images (Dangling Images) an. Diese können bei Bedarf bereinigt werden, um Speicherplatz zu sparen:

```bash
docker image prune -f
```

---

## 5. Logs und Troubleshooting

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
