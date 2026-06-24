# AGENTS.md – Projektkontext

> Angepasst von: [Gruppenname], [Datum]
> Coding-Regeln und Stack-Details: siehe KILO_INSTRUCTIONS.md

## Projektbeschreibung

[TODO: 2–3 Sätze – was digitalisiert dieser Prototyp, welcher Prozess wird abgebildet?]

Beispiel: «Dieses System stellt einen MCP (Model Context Protocol) Server für Vikunja bereit.
Er ermöglicht die Interaktion mit Projekten, Aufgaben, Labels, Kommentaren und Zuweisungen über
standardisierte MCP-Tools. Ziel ist es, Vikunja-Daten nahtlos in LLM-Workflows einzubinden.»

## Stack-Entscheidungen

> Vollständige Stack-Tabelle und Coding-Konventionen: `KILO_INSTRUCTIONS.md`

Kerntechnologien: Python 3.10+ · uv (Paketmanager) · mcp (Python SDK) · httpx (für Vikunja-API-Requests)

**Verboten:** Next.js, Prisma, Supabase, Better Auth, Tailwind CSS, DaisyUI, LangChain.

## Rollenkonzept

Da es sich um einen MCP-Server handelt, der als Brücke zur Vikunja-API dient, wird das Rollenkonzept primär über die Vikunja-API-Berechtigungen des verwendeten API-Tokens gesteuert. 

[TODO: Gegebenenfalls Rollenkonzept für den eigenen Prozess anpassen, falls zusätzliche Autorisierungsebenen eingezogen werden]

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

## Datenmodell

Die Kernentitäten entsprechen den Vikunja-Ressourcen:
- `Project`: id, title, parent_project_id, description
- `Task`: id, project_id, title, description, done, priority, due_date, reminders
- `Label`: id, title
- `Comment`: id, task_id, comment
- `User` / `Assignee`: id, username, email

## Entwicklungsstand

siehe `TASKS.md`

## Team

[TODO: Gruppenname, Mitglieder, Kursjahrgang]
