# KILO_INSTRUCTIONS.md – Coding-Guide für altiplano

> Diese Datei steuert, wie Kilo Code in diesem Projekt arbeitet.
> Projektkontext (Was/Warum) → siehe AGENTS.md

## Tech-Stack (nicht verhandelbar)

| Bereich | Technologie |
|---|---|
| Framework / Protokoll | Model Context Protocol (MCP) |
| Sprache | Python >=3.10 |
| Paket- / Projektmanager | uv |
| HTTP-Client | httpx (für Vikunja-API-Anfragen) |
| MCP SDK | mcp (offizielles Python SDK) |
| Testing | pytest |
| Build System | hatchling |

**Verboten:** Node.js, npm, Next.js, React, Prisma, Better Auth, Tailwind CSS, DaisyUI, LangChain, Supabase.

## Sprache und Stil

- Code: **Python** (PEP 8 Konformität, Typ-Annotationen erwünscht)
- Kommentare: **Deutsch**, laienverständlich; jede neue Datei mit 1–2 Sätzen Kopf-Kommentar
- Namen: ausführlich und selbsterklärend (`get_vikunja_client`, `list_tasks_tool`)
- Keine Emojis, ausser explizit gewünscht

## Dokumentationsstruktur (docs/)

- `docs/starter-kit-usage/` – Anleitungen für Studierende: Was tut ein Feature, wie nutze ich es? Kein tiefer Code, keine Implementierungsdetails.
- `docs/starter-kit-erstellung/` – Implementierungsanleitungen für Agents und technisch Interessierte.
- `docs/project/` – Projektspezifische Pläne, PRDs und Entscheide.

## Projektstruktur (src/-Layout)

```
src/
└── altiplano/
    ├── __init__.py     # Paket-Initialisierung
    └── server.py       # Hauptlogik des MCP-Servers (Tools, API-Requests)
tests/                  # pytest Unit- und Integrationstests
```

## MCP-Konventionen

- **Tools:** Alle Tools werden im MCP-Server registriert und an die Vikunja-API weitergeleitet.
- **Fehlerbehandlung:** Verwende sauberes Exception-Handling für API-Requests (z.B. `httpx.HTTPStatusError`). Fehlerbeschreibungen für das LLM sollten klar und handlungsweisend sein.
- **Konfiguration:** API-Credentials werden über Umgebungsvariablen (`VIKUNJA_URL`, `VIKUNJA_API_TOKEN`) oder eine lokale Konfigurationsdatei geladen. Keine Secrets im Code oder in `mcp.json`.

## Testing (pytest)

**Brownfield-Pragmatismus (Pflicht):** 
1. Bei jedem **neuen oder geänderten** Tool zwingend Unit- oder Integrationstests (inkl. API-Mocks) schreiben.
2. Bestehende, unveränderte Alt-Funktionen müssen nicht lückenlos nachgetestet werden, um den MVP-Start nicht zu verzögern.
3. Echte API-Requests an Vikunja sind in Tests strikt verboten (alles via `httpx`-Mocks abfangen).

### pytest – `tests/`
- **Was:** Tool-Ausführungslogik, API-Client-Mocks, Request/Response-Transformationen
- **Befehl:** `uv run pytest`

### PIV-Loop (vollständig)
1. **Plan** – Feature mit `/plan-feature [Feature]` planen. Root-`TASKS.md` bleibt nur Feature-Index; Details, Tasks und Akzeptanzkriterien liegen in `docs/project/features/[feature-name]/plan-v001.md`.
   - Wenn beim Planen ein PRD-Widerspruch oder eine fehlende fachliche Grundlage auffällt, stoppt der Agent und fordert zuerst `/update-prd [PRD-Pfad]` an.
2. **Review Plan** – Initialen Plan committen, dann in frischer Session mit `/review-feature-plan` prüfen und in der Autor-Session mit `/integrate-feature-plan-review` in eine neue Plan-Version überführen, typischerweise `plan-v002.md`.
3. **Implement** – Mit `/execute docs/project/features/[feature-name]/plan-v002.md` genau einen Task nach dem anderen umsetzen.
4. **Validate** – `uv run pytest` ausführen, Ergebnis auswerten und Fehler beheben.
5. **Document** – Nach vollständiger Umsetzung und Validierung mit `/document` Endanwender- und Entwicklerdokumentation erstellen.
6. **Reflect bei Verdacht** – Nach `/document` prüfen, ob Agent-Fehler, Planlücken, Nacharbeiten oder wiederholte Nutzerkorrekturen dauerhafte Regel- oder Skill-Anpassungen erfordern.
7. **Commit** – Nach validierten Tasks oder Phasen darf mit `/commit` ein fokussierter Zwischencommit erstellt werden.

## Verfügbare PIV-Skills

Skills liegen in `.agents/skills/`. Aufruf per `/skill-name` im Chat. Nie automatisch aktivieren – immer nur auf expliziten Aufruf.

| Skill | Aufruf | PIV-Phase |
|---|---|---|
| prime | `/prime` | Session-Start: Projekt-Kontext laden |
| create-prd | `/create-prd [Dateiname]` | Setup/Plan: PRD-Entwurf als `v001` generieren |
| review-prd | `/review-prd [Pfad-zum-PRD]` | Setup/Plan: PRD in frischer Reviewer-Session kritisch prüfen |
| integrate-prd-review | `/integrate-prd-review [Pfad-zum-PRD] [Pfad-zum-Review]` | Setup/Plan: Review bewerten und integrieren |
| update-prd | `/update-prd [Pfad-zum-PRD]` | Setup/Plan: PRD versioniert aktualisieren |
| adapt-to-project | `/adapt-to-project [Pfad-zum-PRD]` | Setup: Code nach bestätigtem PRD bereinigen, Tests validieren |
| plan-feature | `/plan-feature [Feature]` | Plan: initialen Feature-Plan `plan-v001.md` erstellen |
| review-feature-plan | `/review-feature-plan [Pfad-zum-Plan]` | Plan: Feature-Plan in frischer Reviewer-Session prüfen |
| integrate-feature-plan-review | `/integrate-feature-plan-review [Pfad-zum-Plan] [Pfad-zum-Review]` | Plan: Review integrieren und neue Plan-Version erstellen |
| update-feature-plan | `/update-feature-plan [Pfad-zum-Plan]` | Plan: Feature-Plan versioniert aktualisieren |
| execute | `/execute [Pfad-zum-Plan]` | Implement: Task-by-Task umsetzen |
| document | `/document [Pfad-zum-Plan]` | Validate/Docs: Feature-Dokumentation erstellen |
| reflect-rules | `/reflect-rules [Pfad-zum-Plan]` | Validate/Retro: Agent-Regeln und Skills verbessern |
| commit | `/commit` | Commit: Konventionellen Commit erstellen |
| create-rules | `/create-rules` | Setup: Instructions-Dateien aktualisieren |
| init-project | `/init-project` | Setup: Projekt initialisieren |

## Wann stoppen und fragen?

Stoppe und frage **vor**:
- Strukturänderungen an `server.py` oder Schnittstellenänderungen der Tools
- Hinzufügen neuer externer Abhängigkeiten in `pyproject.toml`
- Kritischen Architekturentscheidungen
- Unklarheiten über den Vikunja-API-Integration-Scope

## Commit-Konventionen

- Format: `feat:`, `fix:`, `docs:`, `test:`
- Kein Commit ohne erfolgreiche Validierung
- Kleine, fokussierte Zwischencommits nach validierten Tasks oder Phasen sind erlaubt
- Finaler Feature-Commit erst nach `/document` und, falls Verdachtsmomente vorliegen, nach `/reflect-rules`
