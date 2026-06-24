# User Guide: Cloudflare Access Support

## Überblick

Dieses Feature ermöglicht dem MCP-Server die Authentifizierung gegenüber einer selbst gehosteten Vikunja-Instanz, die hinter **Cloudflare Access (Zero Trust)** abgesichert ist. Der Server übergibt automatisch die konfigurierten Cloudflare Service-Token Header (`CF-Access-Client-Id` und `CF-Access-Client-Secret`), um die Sicherheitsbarriere an der Cloudflare Edge zu passieren.

## MCP-Tools

*Nicht relevant.* Das Feature fügt keine neuen MCP-Tools hinzu, sondern erweitert die bestehende Kommunikationsschicht (HTTP-Header) im Hintergrund, so dass alle registrierten MCP-Tools (wie `list_projects`, `list_tasks` etc.) auch hinter Cloudflare Access funktionsfähig bleiben.

## Voraussetzungen

1. Ein in **Cloudflare Zero Trust** konfiguriertes **Service Token** (erzeugt eine *Client ID* und ein *Client Secret*).
2. Eine entsprechende **Access Application Policy** (Bypass oder Service Auth), die dieses Service-Token für die Vikunja-Domain oder den API-Pfad (`/api/v1/*`) zulässt.

## Konfiguration

Füge die Zugangsdaten zu deiner Konfigurationsdatei hinzu (Standard: `~/.config/altiplano/env`):

```env
VIKUNJA_URL=https://tasks.melbjo.win/api/v1
VIKUNJA_API_TOKEN=dein-vikunja-api-token
CF_CLIENT_ID=deine-cloudflare-client-id
CF_CLIENT_SECRET=dein-cloudflare-client-secret
```

Alternativ können diese Werte als Umgebungsvariablen beim Start des MCP-Servers übergeben werden.

## Schritt-für-Schritt Demo

1. Konfiguriere das Service-Token in `~/.config/altiplano/env`.
2. Starte den MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector uv run altiplano
   ```
3. Öffne die angezeigte Web-Oberfläche.
4. Führe das Tool `list_projects` aus.
5. **Erwartetes Ergebnis:** Die API-Anfrage wird erfolgreich durch Cloudflare geschleust und du erhältst die Liste deiner Vikunja-Projekte. Es findet kein Redirect (`302 Found`) auf die Cloudflare-Login-Seite statt.

## Bekannte Einschränkungen

- Es wird nur die statische Service-Token-Authentifizierung unterstützt. Dynamische Anmeldeverfahren (wie Google Workspace OAuth oder GitHub Auth über Cloudflare Access) können vom Server nicht interaktiv durchlaufen werden.
