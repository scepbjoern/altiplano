# User Guide: OAuth 2.1 Authentifizierung via Cloudflare MCP Server Portal

## Überblick

Dieses Feature ermöglicht es Web-LLM-Clients (insbesondere ChatGPT Web), sich sicher und komfortabel über Cloudflare Managed OAuth an Ihrem Altiplano MCP-Server anzumelden. Dadurch entfällt für diese Clients die Notwendigkeit, statische HTTP-Header (wie Cloudflare Service Tokens) manuell zu konfigurieren, was in Web-Interfaces oft nicht unterstützt wird. Das Cloudflare MCP Server Portal fungiert als sicheres Gateway.

## MCP-Tools

Das Portal stellt alle Tools Ihres Altiplano MCP-Servers bereit. Bei der initialen Einrichtung kann der Administrator eine Tool-Allowlist konfigurieren, um den Zugriff auf bestimmte Tools einzuschränken.

## Voraussetzungen

- Ein eingerichtetes Cloudflare MCP Server Portal (z.B. unter `https://mcp.melbjo.win`).
- Eine konfigurierte Access Policy im Portal, die den Zugriff regelt (z.B. per OTP-Mail).
- Aktiviertes *Managed OAuth* auf dem Portal mit registrierten Redirect-URIs für die Clients.

## Schritt-für-Schritt Demo

### ChatGPT Web

1. Gehen Sie in **ChatGPT Web** zu **Settings** (Einstellungen) -> **Connectors** (Konnektoren).
2. Aktivieren Sie den **Developer Mode** (Entwicklermodus).
3. Klicken Sie auf **Create** (oder **+ Custom Connector**).
4. Geben Sie als **Connection URL** Ihre Portal-Client-URL mit dem Suffix `/mcp` ein:
   `https://mcp.melbjo.win/mcp`
5. Wählen Sie unter Authentication **OAuth** aus.
6. ChatGPT führt die Auto-Discovery aus. Bestätigen Sie das Risiko-Häkchen und klicken Sie auf **Create**.
7. Durchlaufen Sie den Cloudflare Access Login-Flow im sich öffnenden Browser-Fenster.
8. Nach der Autorisierung ist der Connector verbunden.
9. Schreiben Sie im Chat: *„Zeige meine Vikunja Projekte“*. Die Vikunja-Projekte werden über das Portal vom Altiplano-Server abgerufen.

## Bekannte Einschränkungen

- **Claude Web (claude.ai)**: In neueren Versionen der Claude-Web-Benutzeroberfläche können Einzelbenutzer keine Custom Connectors per URL mehr anlegen (es werden dort nur lokale Plugins unterstützt). Zudem besteht ein bekanntes Problem im OAuth-Handshake von Claude Web ([Anthropic Issue #410](https://github.com/anthropics/claude-ai-mcp/issues/410)). Verwenden Sie für Claude daher weiterhin **Claude Desktop** mit Service-Token.
