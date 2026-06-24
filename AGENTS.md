# AGENTS.md – Projektkontext

> Coding-Regeln und Stack-Details: siehe KILO_INSTRUCTIONS.md

## Projektbeschreibung

Dieses System stellt einen MCP (Model Context Protocol) Server für Vikunja bereit.
Er ermöglicht die Interaktion mit Projekten, Aufgaben, Labels, Kommentaren und Zuweisungen über
standardisierte MCP-Tools. Ziel ist es, Vikunja-Daten nahtlos in LLM-Workflows einzubinden.

## Stack-Entscheidungen

> Vollständige Stack-Tabelle und Coding-Konventionen: `KILO_INSTRUCTIONS.md`

Kerntechnologien: Python 3.10+ · uv (Paketmanager) · mcp (Python SDK) · httpx (für Vikunja-API-Requests)

## Rollenkonzept

Da es sich um einen MCP-Server handelt, der als Brücke zur Vikunja-API dient, wird das Rollenkonzept primär über die Vikunja-API-Berechtigungen des verwendeten API-Tokens gesteuert. 

## Scope des Prototypen

**Im Scope:**
- Integration mit der Vikunja-API für Projekte, Aufgaben, Labels, Kommentare und Assignees
- Server-seitiges Filtern und Sortieren (direkt über die Vikunja-API)
- Lokaler Betrieb und Testen des MCP-Servers via `uv run`

**Ausserhalb des Scope:**
- Eine eigene Benutzeroberfläche (UI)
- Eigenes Authentifizierungs- oder Benutzermanagement (wird an Vikunja delegiert)

## Testing-Ansatz

- **pytest** für Unit- und Integrationstests (Mocks für Vikunja-API)
- PIV-Loop: Plan → Implement → **du führst `uv run pytest` aus** → Document → bei Verdacht Reflect Rules → Commit
  - Tests laufen lokal via pytest

## Entwicklungsstand

siehe `TASKS.md`
