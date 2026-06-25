# Plan: Globales Label Management

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001
**Quelle:** User Request & docs/project/prds/vikunja-mcp-server-v009.md  
**Confidence Score:** 10/10 (API-Logik und MCP-Tools sind analog zu bereits implementierten Entitäten wie Project oder Task direkt abbildbar)

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | server.py / Tests |
| Abhängigkeiten | Vikunja API Label-Endpoints (`PUT /labels`, `GET /labels/{id}`, `POST /labels/{id}`, `DELETE /labels/{id}`) |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Ermöglicht der KI, globale Labels in der Vikunja-Instanz zu erstellen, zu aktualisieren und zu löschen. Dies vervollständigt das Label-Management, welches bisher nur das Zuweisen bestehender Labels zu Tasks unterstützte.

## User Story

```text
Als Personal User
möchte ich über den KI-Assistenten globale Labels erstellen, umbenennen oder sicher löschen können,
damit ich meine Aufgaben-Kategorisierung (Kontext, Grösse, Energie) dynamisch anpassen kann.
```

## Problem Statement

Aktuell können in Vikunja Labels über MCP-Tools zu Tasks hinzugefügt und davon entfernt werden, aber es gibt keine Tools, um neue Labels zu definieren oder alte umzubenennen/löschen. Die Pflege der Label-Struktur (`@anywhere`, `#large`, `!high` etc.) erfordert den manuellen Wechsel in die Weboberfläche.

## Solution Statement

Implementierung von drei neuen MCP Tools (`create_label`, `update_label`, `delete_label`) im Server. `delete_label` erhält das bereits etablierte Sicherheits-Muster mit dem obligatorischen `confirm=True` Flag, um unbeabsichtigten Datenverlust zu verhindern.

## Scope

### Im Scope

- Erstellen von Labels (`title`, `description`, `hex_color`).
- Partielles Aktualisieren von Labels durch vorheriges Fetchen des aktuellen Status.
- Löschen von Labels mit `confirm`-Schutz.
- Unit Tests inkl. API-Mocks in `tests/test_server.py`.

### Nicht im Scope

- UI-Komponenten oder Massen-Operationen für Labels.
- Verschmelzen (Merge) von zwei Labels.

## Rollen und Berechtigungen

Personal User. Zugriff via MCP stdio lokal oder Remote. Beschränkung des Löschens durch das Bestätigungs-Konzept.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` - Warum: Existierende `list_labels`, `update_project` und `delete_task` Muster.
- `tests/test_server.py` - Warum: `async def test_...` Mock-Muster mit `@patch("altiplano.server._request")`.

### Relevante Dokumentation

- `docs/project/prds/vikunja-mcp-server-v009.md` - Warum: Beschreibt die gebündelten Extended-Anforderungen an das Label Management.

## Codebase Intelligence

### Projektstruktur und Architektur

Das Projekt nutzt `mcp.server.fastmcp.FastMCP` und `httpx.AsyncClient` über die Hilfsfunktion `_request`.

### Patterns to Follow

- **Naming:** `create_label`, `update_label`, `delete_label`.
- **Update Pattern:** `update_label` empfängt optionale Parameter (z.B. `title: str | None = None`). Zuerst prüfen, ob Felder übergeben wurden (`if not changes: raise ValueError(...)`), dann Status mit `GET /labels/{label_id}` holen, `payload.update(changes)` ausführen und `POST /labels/{label_id}` an Vikunja senden.
- **Delete Pattern:** `if not confirm: raise ValueError("DANGER: ...")`

### Anti-Patterns to Avoid

- Neue Tools ohne Registrierung in `tests/test_server.py` im `expected_tools` Array im Test `test_mcp_initialization`.

### Dependency Analysis

Keine neuen Dependencies nötig.

### Testing Patterns

`@pytest.mark.anyio` und `patch("altiplano.server._request")` für Mocking der HTTPX Calls verwenden.

## Architekturentscheidungen

### Gewählter Ansatz

Direkte Einbindung der 3 neuen Tools als FastMCP-Tools unter den bestehenden Label-Funktionen. Verwendung des erprobten Partial-Update Patterns.

### Erwogene Alternativen

- Alternative: Alle Parameter bei `update_label` als Pflichtfelder (ohne vorheriges GET).
- Entscheidung: Zu fehleranfällig für KI-Clients. Das Partial-Update-Pattern (`fetch then update`) wie bei `update_project` verringert API-Fehler massiv und ist deutlich komfortabler.

### Security, Performance, Maintainability

- Security: `delete_label` erfordert `confirm=True`.
- Maintainability: Englischsprachige Docstrings, klare `dict`-Returns.

## Datenmodell und API-Mapping

- `create_label` -> `PUT /labels`
- `update_label` -> `POST /labels/{id}`
- `delete_label` -> `DELETE /labels/{id}`

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` - Hinzufügen der drei neuen Tools.
- `tests/test_server.py` - Aktualisieren der Initialisierungs-Tests und Hinzufügen von drei Unit Tests.

## Implementation Plan

### Phase 1: Core Implementation

Hinzufügen der FastMCP Tools `create_label`, `update_label`, `delete_label` in `src/altiplano/server.py`.

### Phase 2: Testing

Hinzufügen der Mocks und pytest-Checks in `tests/test_server.py`.

## Step-by-Step Tasks

### Task 1: UPDATE src/altiplano/server.py

**Status:** done  
**Ziel:** `create_label`, `update_label` und `delete_label` implementieren.  
**IMPLEMENT:**
- Schreibe Funktion `create_label(title: str, description: str | None = None, hex_color: str | None = None) -> dict` (Call `PUT /labels`).
- Schreibe Funktion `update_label(label_id: int, title: str | None = None, description: str | None = None, hex_color: str | None = None) -> dict` (Call `GET /labels/{label_id}` -> Call `POST /labels/{label_id}`).
- Schreibe Funktion `delete_label(label_id: int, confirm: bool = False) -> dict` (prüfe confirm -> Call `DELETE /labels/{label_id}`).
**PATTERN:** `update_project` und `delete_task` in derselben Datei.  
**ACCEPTANCE CRITERIA:**
- [x] Alle drei Tools haben englische Docstrings.
- [x] Partial Updates funktionieren sicher.
- [x] Bestätigungsprüfung greift bei `delete_label`.

**VALIDATE:**
- Manuelle Prüfung: Durch Code-Review. (Erfolgreich durchgeführt)

### Task 2: UPDATE tests/test_server.py

**Status:** done  
**Ziel:** Neues Toolset testen.  
**IMPLEMENT:**
- Füge `create_label`, `update_label`, `delete_label` dem `expected_tools` Array in `test_mcp_initialization` hinzu.
- Schreibe `test_create_label(mock_request)`.
- Schreibe `test_update_label(mock_request)`.
- Schreibe `test_delete_label(mock_request)` (beide Fälle: mit und ohne `confirm`).
**ACCEPTANCE CRITERIA:**
- [x] Initialisierungstest läuft durch.
- [x] Unit Tests verifizieren die korrekten Endpunkte und Payloads.

**VALIDATE:**
- `uv run pytest` (Muss erfolgreich durchlaufen). (Erfolgreich durchgeführt: alle 36 Tests bestanden)

## Testing Strategy

### Unit / Integration Tests

- Unit Tests in `tests/test_server.py` mocken `altiplano.server._request` und validieren, dass die Parameter richtig gemappt werden.

### Edge Cases

- Teilweises Update: Ein Update nur mit `hex_color` muss den bestehenden `title` aus dem GET-Request mitgeben.
- Unbestätigtes Delete: Darf den DELETE Request nicht auslösen.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. `uv run altiplano` starten oder in Inspector laden.
2. `create_label` mit Title "Test Label" aufrufen.
3. ID kopieren, `update_label` mit neuer `hex_color` aufrufen.
4. `delete_label` ohne Confirm -> Error.
5. `delete_label` mit Confirm=True -> Erfolgreich.

## Acceptance Criteria

- [x] Feature implementiert alle Scope-Anforderungen
- [x] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [x] Relevante pytest-Tests sind ergänzt und grün
- [x] Relevante manuelle Flows sind validiert
- [x] Keine bekannten Regressionen in bestehenden Kernworkflows
- [x] Dokumentationsbedarf ist notiert

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Alle relevanten Tests laufen erfolgreich oder Ausnahmen sind begründet
- [x] Manuelle Prüfung (MCP Inspector / Claude Desktop) ist dokumentiert
- [x] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Die Dokumentation wurde erfolgreich erstellt:
- [User Guide](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/globales-label-management/user-guide.md)
- [Developer Notes](file:///e:/bjoer/Documents/repos/altiplano/docs/project/features/globales-label-management/developer-notes.md)

## Notes and Trade-offs

Die Vikunja API verlangt beim Label-Update wahrscheinlich alle Felder (insbes. `title`). Daher wenden wir das bewährte Pattern "GET then POST" an. Das verursacht einen Request mehr, macht den Agenten aber wesentlich robuster.

## Offene Fragen

- Keine.

