# Plan: Kanban Buckets

## Status

**Feature-Status:** done
**Erstellt:** 2026-06-25
**Plan-Version:** v001
**Quelle:** PRD `docs/project/prds/vikunja-mcp-server-v006.md` Kapitel 15 ("Kanban Buckets", Medium-Phase), Kapitel 6 (Medium-Version Scope), Kapitel 7 (US-5)
**Confidence Score:** 8/10 — Task 1 wurde gegen die echte Instanz (`tasks.melbjo.win`) ausgeführt und hat die Architektur-Annahme (Views als Zwischenebene, `view_kind == "kanban"`, Bucket-Felder `id`/`title`/`project_view_id`/`limit`/`count`/`position`) für zwei reale Projekte 1:1 bestätigt (Details siehe Task 1). Verbleibendes Risiko: Die Schreib-Endpunkte (`PUT` create, `POST` update, `POST` Task-Zuweisung) sind bislang nur durch den Quellcode, nicht empirisch bestätigt — dieses Restrisiko deckt die ohnehin vorgesehene manuelle Level-2-Validierung in „Validation Commands" ab.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | Medium |
| Primär betroffene Systeme | server.py, Tests |
| Abhängigkeiten | Vikunja API `GET /projects/{id}/views`, `GET/PUT/POST /projects/{id}/views/{view}/buckets[/...]`, `POST /projects/{id}/views/{view}/buckets/{bucket}/tasks` |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan für Kanban Buckets erstellt |

## Feature Description

Vier neue MCP-Tools zur Verwaltung von Kanban-Buckets (Spalten) in Vikunja-Projekten: Buckets auflisten, anlegen, umbenennen/limitieren und Tasks gezielt einem Bucket zuweisen. Die Vikunja-API verwaltet Buckets nicht direkt am Projekt, sondern an einer Projekt-*View* (jedes Projekt hat mehrere Views: list/gantt/table/kanban). Diese Zwischenebene wird serverseitig versteckt — die Tools nehmen weiterhin nur `project_id` entgegen, analog zum bestehenden Tool-Stil.

## User Story

```text
Als Personal User
möchte ich in einem Vikunja-Projekt Kanban-Buckets anlegen, umbenennen und Tasks gezielt
einem Bucket zuweisen können,
damit ich meinen Workflow-Status (z.B. Backlog/Doing/Done) über die KI abbilden kann,
ohne die Vikunja-Web-UI öffnen zu müssen.
```

## Problem Statement

Aktuell bietet Altiplano keine Tools zur Kanban-Strukturierung. PRD Kapitel 15 listet „Kanban Buckets" als Medium-Phase-Feature mit `create_bucket`, `update_bucket` und Task-Zuweisung. PRD Kapitel 9 (Datenmodell) beschreibt `Bucket` jedoch nur mit `id, project_id, title` — ohne die Views-Ebene. Diese Beschreibung ist gegen den aktuellen Vikunja-Quellcode (bestätigt via `go-vikunja/vikunja`, `pkg/models/kanban.go`, `pkg/models/project_view.go`, `pkg/routes/routes.go`) **nicht mehr aktuell**: Buckets hängen über `project_view_id` an einer `ProjectView`, nicht direkt am Projekt. Ein Tool, das naiv `/projects/{id}/buckets` aufruft, würde mit hoher Wahrscheinlichkeit einen 404 erhalten.

## Solution Statement

1. Ein privater Helper `_resolve_kanban_view_id(project_id)` ermittelt automatisch die Kanban-View eines Projekts (`GET /projects/{id}/views`, Filter `view_kind == "kanban"`). Schlägt das fehl (keine Kanban-View vorhanden), wird ein klarer `RuntimeError` geworfen.
2. Vier neue Tools (`list_buckets`, `create_bucket`, `update_bucket`, `move_task_to_bucket`) nutzen diesen Helper intern und exponieren dem LLM-Client weiterhin nur `project_id`/`bucket_id`/`task_id` — keine `view_id`.
3. `update_bucket` folgt dem bestehenden GET-Overlay-Pattern (siehe `update_project`, `update_task`): Bucket-Liste laden, Basis-Payload aus dem gefundenen Bucket bauen, Änderungen überlagern, dann `POST`.
4. `move_task_to_bucket` folgt dem bestehenden „sicherer Wrapper holt sich Kontext selbst"-Pattern (siehe `move_task_to_project`, `complete_task`): `project_id` wird intern per `GET /tasks/{task_id}` ermittelt, nicht vom LLM verlangt.

## Scope

### Im Scope

- `list_buckets(project_id)` — Buckets der Kanban-View eines Projekts auflisten.
- `create_bucket(project_id, title, limit?)` — neuen Bucket anlegen.
- `update_bucket(project_id, bucket_id, title?, limit?)` — Bucket umbenennen/limitieren.
- `move_task_to_bucket(task_id, bucket_id)` — Task einem Bucket zuweisen.
- Privater Helper `_resolve_kanban_view_id(project_id)`.
- Zugehörige pytest-Tests inkl. Erweiterung der Tool-Registrierungsliste in `test_mcp_initialization`.

### Nicht im Scope

- `delete_bucket` — nicht in PRD Kapitel 6/15 für die Medium-Phase gelistet; passt zum Projektprinzip „keine destruktiven Tools ohne explizites Bestätigungs-Pattern".
- Eigenes `list_views`-Tool oder ein `view_id`-Parameter auf den Bucket-Tools — die Views-Komplexität wird bewusst serverseitig versteckt (siehe Architekturentscheidungen).
- Explizites Setzen der Bucket-`position` (Reihenfolge) — Vikunja verwaltet das normalerweise per Drag-&-Drop in der UI; kein PRD-Bedarf dafür.
- Mehrere Kanban-Views pro Projekt — falls vorhanden, wird nur die erste gefunden verwendet (siehe Annahmen).
- Automatisches Anlegen einer Kanban-View, falls keine existiert — es wird stattdessen ein klarer Fehler zurückgegeben (kein stiller Seiteneffekt).
- Aktualisierung von PRD Kapitel 8/9 um die Views-Ebene — wird als Empfehlung für eine separate `/update-prd`-Runde dokumentiert, ist aber nicht blockierend für diesen Plan, da die Views-Auflösung serverseitig verborgen bleibt und das im PRD beschriebene Verhalten (create/rename/assign) unverändert erreichbar ist.

## Rollen und Berechtigungen

Wird über den Vikunja-API-Token gesteuert. Der Token benötigt Lese- und Schreibrechte für Projekte/Views/Buckets/Tasks. Keine Änderungen am Rollenkonzept.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` — Warum: Enthält alle zu spiegelnden Patterns: `update_project` (GET-Overlay, Zeilen 140-178), `update_task` (Zeilen 243-290), `move_task_to_project`/`complete_task` (sicherer Wrapper holt Kontext selbst, Zeilen 303-329), `list_labels`/`add_label` (einfache Listen-/Aktions-Tools, Zeilen 334-350), `_request` (Zeilen 67-85).
- `tests/test_server.py` — Warum: `test_tool_list_projects` (AsyncMock-Pattern, Zeilen 40-73), `test_mcp_initialization` (Tool-Registrierungsliste, Zeilen 5-37) müssen erweitert werden.
- `docs/project/features/task-project-tool-fixes/plan-v001.md` — Warum: Jüngstes Beispiel für das GET-Overlay-Pattern und den Plan-Detailgrad, der hier gespiegelt wird.
- `docs/project/prds/vikunja-mcp-server-v006.md` — Kapitel 6 (Medium-Scope), 7 (US-5), 8 (Kernfunktionen), 9 (Datenmodell — veraltet, siehe Problem Statement), 15 (Feature-Kandidat).

### Relevante Dokumentation

- [go-vikunja/vikunja — pkg/routes/routes.go](https://github.com/go-vikunja/vikunja/blob/main/pkg/routes/routes.go) — Warum: Bestätigt die exakten Routen: `GET/PUT /projects/:project/views/:view/buckets`, `POST/DELETE /projects/:project/views/:view/buckets/:bucket`, `POST /projects/:project/views/:view/buckets/:bucket/tasks`. Keine Route `/projects/:project/buckets` ohne Views-Ebene.
- [go-vikunja/vikunja — pkg/models/kanban.go](https://github.com/go-vikunja/vikunja/blob/main/pkg/models/kanban.go) — Warum: `Bucket`-Struct (Felder `id`, `title`, `project_view_id`, `limit`, `count`, `position`, `created`, `updated`, `created_by`). `ProjectID` ist `json:"-"` (wird **nicht** im Response zurückgegeben).
- [go-vikunja/vikunja — pkg/models/project_view.go](https://github.com/go-vikunja/vikunja/blob/main/pkg/models/project_view.go) — Warum: `ProjectView`-Struct, Enum `view_kind` mit Werten `list`, `gantt`, `table`, `kanban`.
- [go-vikunja/vikunja — pkg/models/kanban_task_bucket.go](https://github.com/go-vikunja/vikunja/blob/main/pkg/models/kanban_task_bucket.go) — Warum: `TaskBucket`-Struct bestätigt den dedizierten Task-zu-Bucket-Zuweisungs-Endpunkt mit Body `{"task_id": ...}`; das `bucket_id`-Feld am Task-Objekt selbst ist seit der Views-Migration nur noch intern relevant und löst über ein normales Task-Update keine Bucket-Änderung mehr aus.
- [vikunja.io/help/views](https://vikunja.io/help/views/) — Warum: Bestätigt, dass neue Projekte standardmässig mehrere Views (inkl. Kanban) erhalten.

## Codebase Intelligence

### Projektstruktur und Architektur

`server.py` ist eine Single-File-FastMCP-App mit Tools gruppiert per Kommentar-Sektion (`# --- projects ---`, `# --- tasks ---`, `# --- labels ---`, ...). Eine neue Sektion `# --- buckets (kanban) ---` wird nach der Tasks-Sektion (nach `move_task_to_project`, Zeile 329) und vor der Labels-Sektion (Zeile 332) eingefügt.

### Patterns to Follow

- Naming: `list_*`, `create_*`, `update_*`, `move_*_to_*` (siehe `move_task_to_project`).
- Fehlerbehandlung: `_request` fängt `httpx.HTTPStatusError` zentral ab. Eigene Validierungsfehler: `ValueError` für „keine Änderung übergeben" (siehe `update_task` Zeile 271-272), `RuntimeError` für „Ressource nicht gefunden/Vorbedingung fehlt" (neu für „keine Kanban-View" und „Bucket nicht gefunden").
- GET-Overlay-Pattern: Vor einem Teil-Update per `POST` zuerst den aktuellen Zustand per `GET` laden und Pflichtfelder in den Payload übernehmen (siehe `update_project` Zeilen 166-176, `update_task` Zeilen 274-289). Identisch für `update_bucket` anzuwenden — mit dem Unterschied, dass es keinen `GET /buckets/{id}` Einzel-Endpunkt gibt, sondern aus der Liste (`GET .../buckets`) gefiltert werden muss.
- Optimistic Locking: `updated`-Feld aus dem GET-Response in den Payload übernehmen, wenn vorhanden (siehe `update_task` Zeilen 286-287, `set_reminders` Zeilen 298-299). Gleiches Muster für `update_bucket`, auch wenn nicht bestätigt ist, dass Vikunja bei Buckets ebenfalls 412-Fehler bei fehlendem `updated` wirft — non-destruktive Ergänzung ohne Risiko.
- Sicherer Wrapper holt Kontext selbst: `move_task_to_project`/`complete_task` verlangen vom LLM nur die nötigsten Parameter und ermitteln den Rest per internem `GET` (Zeilen 303-329). `move_task_to_bucket` spiegelt das: nur `task_id`/`bucket_id` als Parameter, `project_id` wird intern aus `GET /tasks/{task_id}` gelesen.

### Anti-Patterns to Avoid

- Kein Node.js, Next.js, React, Prisma, Tailwind CSS, DaisyUI, LangChain.
- Keine `view_id`-Parameter auf den öffentlichen Tools (siehe Architekturentscheidungen).
- Keine client-seitige Sortierung/Filterung von Buckets — Vikunja liefert sie bereits positionssortiert.
- Kein Full-Replacement-Payload mit geratenen/hartkodierten Feldern bei `update_bucket` — nur das aus dem echten GET-Response gespiegelte Feld-Set.

### Dependency Analysis

Keine neuen Packages erforderlich. `httpx` und `mcp` decken den Bedarf vollständig ab.

### Testing Patterns

`pytest` mit `unittest.mock.patch` auf `altiplano.server._request` (`AsyncMock`). Da `list_buckets`/`create_bucket`/`update_bucket`/`move_task_to_bucket` **zwei** sequenzielle `_request`-Aufrufe machen (zuerst View-Auflösung, dann die eigentliche Aktion), muss `mock_request.side_effect = [<views_response>, <buckets_response>]` verwendet werden (neues Pattern gegenüber den meisten bestehenden Tests, die nur 1 Request mocken). Beispiel orientiert an `test_tool_update_project`, das bereits eine `side_effect`-Funktion für GET/POST nutzt.

## Architekturentscheidungen

### Gewählter Ansatz

Die Views-Ebene wird serverseitig komplett versteckt. Tools nehmen nur `project_id` entgegen; ein privater Helper `_resolve_kanban_view_id(project_id)` löst automatisch die zugehörige Kanban-View auf (`GET /projects/{id}/views`, erste View mit `view_kind == "kanban"`). Das hält den vom PRD vorgesehenen schlanken Tool-Scope (Kapitel 15 nennt nur `create_bucket`/`update_bucket`/Task-Zuweisung, keine Views) ein, ohne dass PRD oder Code-Konsumenten die Vikunja-interne Views-Architektur kennen müssen.

### Erwogene Alternativen

- Alternative: Eigenes `list_views`-Tool exponieren und `view_id` explizit vom LLM verlangen. Entscheidung: verworfen — verkompliziert die Tool-Oberfläche unnötig und widerspricht dem PRD-Scope und dem Projektprinzip „keine client-seitige Komplexität" (hier sinngemäss erweitert auf „keine Vikunja-Interna-Auflösung durch den Client").
- Alternative: `update_task` um einen `bucket_id`-Parameter erweitern, statt eines eigenen `move_task_to_bucket`-Tools. Entscheidung: verworfen — der Vikunja-Quellcode bestätigt, dass das `bucket_id`-Feld am Task seit der Views-Migration nur noch intern verwendet wird; ein Update darüber löst keine Bucket-Änderung mehr aus. Es existiert ein dedizierter Endpunkt, der genutzt werden muss.
- Alternative: Bei fehlender Kanban-View automatisch eine anlegen (`PUT /projects/{id}/views`). Entscheidung: verworfen — stiller Seiteneffekt, der nicht angefragt wurde; ein klarer Fehler ist im Sinne des Projektprinzips „Sicherheit vor Feature-Vollständigkeit" vorzuziehen.

### Security, Performance, Maintainability

- Security: Keine neuen destruktiven Operationen (kein `delete_bucket`). Token-Berechtigungen weiterhin vikunja-seitig gesteuert.
- Performance: `_resolve_kanban_view_id` erzeugt einen zusätzlichen `GET`-Request pro Bucket-Tool-Aufruf (kein Caching, da der Server pro Tool-Call zustandslos arbeitet). Akzeptabler Trade-off für Einfachheit, da Bucket-Operationen erfahrungsgemäss nicht in Bulk auftreten.
- Maintainability: Konsistente Anwendung des bereits etablierten GET-Overlay- und „Wrapper holt Kontext selbst"-Patterns erleichtert künftige Wartung und Vergleichbarkeit mit `update_project`/`update_task`/`move_task_to_project`.

## Datenmodell und API-Mapping

| Vikunja-Feld (Bucket) | Quelle | MCP-Tool-Output (`list_buckets`) |
|---|---|---|
| `id` | GET-Response | `id` |
| `title` | GET-Response | `title` |
| `project_view_id` | GET-Response | nicht exponiert (interne Vikunja-Referenz) |
| `limit` | GET-Response | `limit` (Default `0` = unlimitiert) |
| `count` | GET-Response | `count` (aktuelle Anzahl Tasks im Bucket) |
| `position` | GET-Response | `position` |
| `created`/`updated`/`created_by` | GET-Response | nicht exponiert (analog zu `list_labels`, das ebenfalls nur ein schlankes Subset zurückgibt) |

| Tool | HTTP | Pfad | Payload |
|---|---|---|---|
| `list_buckets` | `GET` | `/projects/{project_id}/views/{view_id}/buckets` | — |
| `create_bucket` | `PUT` | `/projects/{project_id}/views/{view_id}/buckets` | `{"title": ..., "limit"?: ...}` |
| `update_bucket` | `POST` | `/projects/{project_id}/views/{view_id}/buckets/{bucket_id}` | `{"title": <aktuell oder neu>, "limit": <aktuell oder neu>, "updated"?: ...}` |
| `move_task_to_bucket` | `POST` | `/projects/{project_id}/views/{view_id}/buckets/{bucket_id}/tasks` | `{"task_id": ...}` |
| `_resolve_kanban_view_id` (intern) | `GET` | `/projects/{project_id}/views` | — (filtert `view_kind == "kanban"`) |

**Wichtiger Hinweis zur PRD-Abweichung:** PRD Kapitel 9 listet für `Bucket` die Felder `id, project_id, title`. Der reale Vikunja-Bucket hat **kein** `project_id`-Feld im Response (`json:"-"`), sondern `project_view_id`. Dieser Plan dokumentiert die reale Struktur und löst sie serverseitig auf; eine Korrektur von PRD Kapitel 9 wird für eine künftige `/update-prd`-Runde empfohlen, ist aber für die Umsetzung dieses Plans nicht blockierend.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` — ADD: `_resolve_kanban_view_id`, `list_buckets`, `create_bucket`, `update_bucket`, `move_task_to_bucket`.
- `tests/test_server.py` — UPDATE: `test_mcp_initialization` (Tool-Liste erweitern). ADD: Tests für alle vier neuen Tools plus Edge Cases.

### Neue Dateien

- Keine (gleiche Single-File-Architektur wie bestehender Code).

## Implementation Plan

### Phase 1: Verifikation gegen die echte Instanz
Manuelle Prüfung, dass die angenommene Views/Buckets-API-Form (recherchiert gegen den `main`-Branch von `go-vikunja/vikunja`) auf der tatsächlichen Instanz (`https://tasks.melbjo.win/api/v1`, Vikunja 2.3.0) zutrifft, bevor Code geschrieben wird.

### Phase 2: Foundation
`_resolve_kanban_view_id`-Helper implementieren.

### Phase 3: Core Implementation
Die vier neuen Tools implementieren (`list_buckets`, `create_bucket`, `update_bucket`, `move_task_to_bucket`).

### Phase 4: Testing and Validation
Tests ergänzen, `uv run pytest` ausführen, manuelle Validierung gegen die echte Instanz (MCP Inspector).

## Step-by-Step Tasks

Wichtig: Tasks top-to-bottom ausführen. Jeder Task ist atomic und einzeln validierbar. **Task 1 ist ein Gate:** Weicht die echte API-Form ab, muss der Plan vor Fortsetzung mit Task 2 überarbeitet werden (z.B. via `/update-feature-plan`).

### Task 1: Verifikation der Views/Buckets-API-Form gegen die echte Vikunja-Instanz

**Status:** done

**Validierungsergebnis (2026-06-25, PowerShell `Invoke-RestMethod` gegen `tasks.melbjo.win`):**
- `GET /projects/-5/views` und `GET /projects/14/views` liefern beide ein Array mit `id`, `title`, `view_kind` — inkl. einer View mit `"view_kind": "kanban"` (Projekt `-5`: View-id `77`; Projekt `14`: View-id `32`).
- `GET /projects/14/views/32/buckets` liefert ein Array von 4 echten, im Alltag genutzten Buckets (`Backlog` id 27, `Beginnen` id 57, `Working` id 36, `Done` id 37), jeweils mit exakt den angenommenen Feldern `id`, `title`, `project_view_id`, `limit`, `count`, `position`, `created`, `updated`, `created_by`.
- Cross-Check `GET /projects/-5/views/77/buckets` liefert 1 Bucket (`Backlog`, id 102) mit identischer Feldstruktur — bestätigt die Form auch für ein zweites Projekt.
- Nicht jedes Projekt hat eine Kanban-View (das Pseudo-Projekt `Favorites`, id `-1`, hat nur List/Gantt/Table) — bestätigt empirisch den von `_resolve_kanban_view_id` antizipierten Fehlerfall.

**Ziel:** Bestätigen, dass `GET /projects/{id}/views` eine View mit `view_kind == "kanban"` liefert und dass die Bucket-Routen unter `/projects/{id}/views/{view}/buckets...` erreichbar sind.
**IMPLEMENT:** Kein Code. Gegen die echte Instanz mit einem existierenden, bekannten `project_id` ausführen (durchgeführt via PowerShell `Invoke-RestMethod` statt `curl`/`jq`, siehe Validierungsergebnis oben).
**PATTERN:** Keines (Recherche-/Verifikations-Task).
**GOTCHA:** `Format-Table` kann bei genau einem Ergebnis-Objekt irreführend leer wirken (PowerShell hängt eine synthetische `Count`-Eigenschaft an); bei Zweifeln immer mit `ConvertTo-Json` gegen die Rohantwort prüfen, nicht gegen die formatierte Tabelle.
**ACCEPTANCE CRITERIA:**

- [x] Eine View mit `view_kind == "kanban"` wurde für mindestens ein reales Projekt gefunden.
- [x] Die Bucket-Liste unter `/projects/{id}/views/{view}/buckets` wurde erfolgreich abgerufen.

**VALIDATE:**

- Manuell: PowerShell `Invoke-RestMethod`-Aufrufe wie oben, Ergebnis im Plan festgehalten (siehe Validierungsergebnis).

### Task 2: ADD `_resolve_kanban_view_id` Helper

**Status:** done
**Ziel:** Privater Helper, der für ein Projekt die `id` der Kanban-View liefert oder einen klaren Fehler wirft.
**IMPLEMENT:** In `src/altiplano/server.py` nach `_task_summary` (vor der `# --- projects ---` Sektion oder direkt vor der neuen Buckets-Sektion) folgende Funktion ergänzen:

```python
async def _resolve_kanban_view_id(project_id: int) -> int:
    views = await _request("GET", f"/projects/{project_id}/views")
    for v in views or []:
        if v.get("view_kind") == "kanban":
            return v["id"]
    raise RuntimeError(
        f"Project {project_id} has no Kanban view; create one in the Vikunja UI first."
    )
```

**PATTERN:** `_base()`/`_headers()` als Vorbild für kleine, fokussierte private Helper mit klarer `RuntimeError`-Fehlermeldung (Zeilen 44-64).
**IMPORTS:** Keine neuen.
**GOTCHA:** Falls mehrere Kanban-Views existieren, wird bewusst die erste in der API-Reihenfolge zurückgegebene verwendet (siehe Scope „Nicht im Scope").
**ACCEPTANCE CRITERIA:**

- [ ] Helper gibt die `id` der ersten Kanban-View zurück, wenn vorhanden.
- [ ] Helper wirft `RuntimeError` mit verständlicher Meldung, wenn keine Kanban-View existiert.

**VALIDATE:**

- `uv run pytest` (Test folgt indirekt über die Tools in Task 3-6, plus dedizierter Edge-Case-Test in Task 7).

### Task 3: ADD `list_buckets` Tool

**Status:** done
**Ziel:** Buckets eines Projekts auflisten.
**IMPLEMENT:** Neue Sektion `# --- buckets (kanban) ---` nach `move_task_to_project` (Zeile 329) einfügen:

```python
@mcp.tool()
async def list_buckets(project_id: int) -> list[dict]:
    """List Kanban buckets (columns) of a project's Kanban view."""
    view_id = await _resolve_kanban_view_id(project_id)
    data = await _request("GET", f"/projects/{project_id}/views/{view_id}/buckets")
    return [
        {
            "id": b.get("id"),
            "title": b.get("title"),
            "limit": b.get("limit", 0),
            "position": b.get("position"),
            "count": b.get("count", 0),
        }
        for b in (data or [])
    ]
```

**PATTERN:** `list_labels` (Zeilen 334-338) für die schlanke Listen-Mapping-Struktur.
**IMPORTS:** Keine neuen.
**GOTCHA:** Vikunja liefert Buckets bereits nach `position` sortiert — keine eigene Sortierung ergänzen.
**ACCEPTANCE CRITERIA:**

- [ ] `list_buckets` löst die Kanban-View auf und gibt eine Liste schlanker Bucket-Dicts zurück.
- [ ] Bei fehlender Kanban-View wird der `RuntimeError` aus `_resolve_kanban_view_id` durchgereicht.

**VALIDATE:**

- `uv run pytest` (Test in Task 7).

### Task 4: ADD `create_bucket` Tool

**Status:** done
**Ziel:** Neuen Bucket in der Kanban-View eines Projekts anlegen.
**IMPLEMENT:**

```python
@mcp.tool()
async def create_bucket(project_id: int, title: str, limit: int | None = None) -> dict:
    """Create a new Kanban bucket (column) in a project's Kanban view.

    Use `limit` to cap how many tasks may be placed in this bucket (omit for unlimited).
    """
    view_id = await _resolve_kanban_view_id(project_id)
    payload: dict[str, Any] = {"title": title}
    if limit is not None:
        payload["limit"] = limit
    return await _request("PUT", f"/projects/{project_id}/views/{view_id}/buckets", json=payload)
```

**PATTERN:** `create_project` (Zeilen 119-136) für die Parameter-zu-Payload-Struktur bei `PUT`.
**IMPORTS:** Keine neuen.
**GOTCHA:** `PUT` ist in Vikunja das Create-Verb (nicht `POST`) — analog zu `create_project`/`create_task`.
**ACCEPTANCE CRITERIA:**

- [ ] `create_bucket` legt einen Bucket mit `title` an.
- [ ] `limit` wird nur gesendet, wenn explizit übergeben.

**VALIDATE:**

- `uv run pytest` (Test in Task 7).

### Task 5: ADD `update_bucket` Tool

**Status:** done
**Ziel:** Bucket umbenennen und/oder Limit ändern, ohne andere Felder zu überschreiben.
**IMPLEMENT:**

```python
@mcp.tool()
async def update_bucket(
    project_id: int,
    bucket_id: int,
    title: str | None = None,
    limit: int | None = None,
) -> dict:
    """Update a Kanban bucket. Only the fields you pass are changed."""
    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title
    if limit is not None:
        changes["limit"] = limit
    if not changes:
        raise ValueError("No fields to update")

    view_id = await _resolve_kanban_view_id(project_id)
    buckets = await _request("GET", f"/projects/{project_id}/views/{view_id}/buckets")
    bucket = next((b for b in (buckets or []) if b.get("id") == bucket_id), None)
    if bucket is None:
        raise RuntimeError(f"Bucket {bucket_id} not found in project {project_id}")

    payload: dict[str, Any] = {
        "title": bucket["title"],
        "limit": bucket.get("limit", 0),
    }
    if "updated" in bucket:
        payload["updated"] = bucket["updated"]
    payload.update(changes)

    return await _request(
        "POST", f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}", json=payload
    )
```

**PATTERN:** `update_project` (Zeilen 140-178) — identisches GET-Overlay-Pattern, hier per Filterung aus der Bucket-Liste statt einem dedizierten Einzel-GET (existiert für Buckets nicht).
**IMPORTS:** Keine neuen.
**GOTCHA:** Es gibt keinen `GET /buckets/{id}`-Einzel-Endpunkt — der aktuelle Zustand muss aus der Listen-Antwort gefiltert werden. Der `ValueError`-Check muss vor den beiden `_request`-Aufrufen erfolgen (Performance + Konsistenz mit `update_task`).
**ACCEPTANCE CRITERIA:**

- [ ] `update_bucket` ohne Parameter wirft `ValueError("No fields to update")`, ohne einen Request auszuführen.
- [ ] `update_bucket` mit nur `title` sendet trotzdem das bestehende `limit` mit (kein unbeabsichtigtes Zurücksetzen).
- [ ] `update_bucket` mit unbekannter `bucket_id` wirft `RuntimeError` mit verständlicher Meldung.

**VALIDATE:**

- `uv run pytest` (Tests in Task 7).

### Task 6: ADD `move_task_to_bucket` Tool

**Status:** done
**Ziel:** Task einem bestimmten Bucket im (eigenen) Projekt zuweisen.
**IMPLEMENT:**

```python
@mcp.tool()
async def move_task_to_bucket(task_id: int, bucket_id: int) -> dict:
    """Move a task into a specific Kanban bucket within its current project."""
    task = await _request("GET", f"/tasks/{task_id}")
    project_id = task["project_id"]
    view_id = await _resolve_kanban_view_id(project_id)
    return await _request(
        "POST",
        f"/projects/{project_id}/views/{view_id}/buckets/{bucket_id}/tasks",
        json={"task_id": task_id},
    )
```

**PATTERN:** `move_task_to_project` (Zeilen 320-329) — gleiches Prinzip „Wrapper holt Kontext (hier: `project_id`) selbst per GET".
**IMPORTS:** Keine neuen.
**GOTCHA:** `project_id` kommt aus dem Task selbst, nicht als Parameter vom LLM — verhindert Inkonsistenzen, falls der Task in einem anderen Projekt liegt als angenommen. Kein `title`-Pflichtfeld-Risiko hier, da der Endpunkt kein normales Task-Update ist, sondern der dedizierte Bucket-Zuweisungs-Endpunkt.
**ACCEPTANCE CRITERIA:**

- [ ] `move_task_to_bucket` ermittelt `project_id` automatisch aus dem Task.
- [ ] Bei fehlender Kanban-View im Zielprojekt wird der `RuntimeError` aus `_resolve_kanban_view_id` durchgereicht.

**VALIDATE:**

- `uv run pytest` (Test in Task 7).

### Task 7: UPDATE/ADD Tests in `tests/test_server.py`

**Status:** done
**Ziel:** Alle neuen Tools und der Helper sind durch Tests abgedeckt; die Tool-Registrierungsliste ist aktuell.
**IMPLEMENT:**
- `test_mcp_initialization`: `expected_tools`-Liste um `"list_buckets"`, `"create_bucket"`, `"update_bucket"`, `"move_task_to_bucket"` ergänzen.
- Neuer Test `test_tool_list_buckets`: `mock_request.side_effect = [<views-Liste mit kanban-View>, <buckets-Liste>]`, ruft `list_buckets(1)` auf, prüft Rückgabe-Mapping und beide `_request`-Aufrufe (`GET /projects/1/views`, dann `GET /projects/1/views/{view_id}/buckets`).
- Neuer Test `test_tool_create_bucket`: analoges `side_effect` für Views + `PUT`-Response, prüft gesendeten Payload (`title`, optional `limit`).
- Neuer Test `test_tool_update_bucket`: `side_effect` für Views + Bucket-Liste + `POST`-Response, prüft Merge-Verhalten (z.B. nur `title` übergeben, `limit` bleibt aus GET erhalten) sowie `ValueError` bei leerem Aufruf und `RuntimeError` bei unbekannter `bucket_id`.
- Neuer Test `test_tool_move_task_to_bucket`: `side_effect` für `GET /tasks/{id}` (liefert `project_id`) + Views + `POST .../tasks`, prüft gesendeten Body `{"task_id": ...}`.
- Neuer Test `test_resolve_kanban_view_id_missing`: `mock_request.return_value = []` (keine Views), prüft `RuntimeError`-Meldung direkt am Helper oder indirekt über `list_buckets`.

**PATTERN:** `test_tool_update_project` (`side_effect`-Funktion für mehrere `_request`-Aufrufe), `test_tool_list_projects` (Mapping-Assertion).
**IMPORTS:** Keine neuen (bestehende `pytest`, `unittest.mock.patch`, `AsyncMock`).
**GOTCHA:** Bei `side_effect` als Liste muss die Reihenfolge exakt der tatsächlichen Aufrufreihenfolge im Tool entsprechen (erst View-Auflösung, dann die eigentliche Aktion) — sonst liefert der Mock die falsche Antwort für den falschen Call.
**ACCEPTANCE CRITERIA:**

- [ ] `test_mcp_initialization` listet alle vier neuen Tools.
- [ ] Jedes neue Tool hat mindestens einen Happy-Path-Test.
- [ ] Edge Cases (`ValueError` bei leerem Update, `RuntimeError` bei unbekanntem Bucket, `RuntimeError` bei fehlender Kanban-View) sind abgedeckt.

**VALIDATE:**

- `uv run pytest` — alle Tests grün, inkl. der vier neuen plus erweitertem Initialisierungstest.

## Testing Strategy

### Unit / Integration Tests

- Für jedes der vier neuen Tools: Happy-Path-Test mit gemocktem `_request` (`side_effect`-Liste für die zwei sequenziellen Calls).
- Für `update_bucket`: Merge-Verhalten (Teil-Update überschreibt nicht das bestehende `limit`), `ValueError` bei keiner Änderung, `RuntimeError` bei unbekannter `bucket_id`.
- Für `_resolve_kanban_view_id`: `RuntimeError` bei fehlender Kanban-View.

### Regression Tests

- `test_mcp_initialization` deckt weiterhin alle bisherigen 19 Tools plus die 4 neuen ab (23 insgesamt).
- Bestehende Tests (`test_tool_list_projects`, `test_cloudflare_headers`, etc.) bleiben unverändert grün.

### Edge Cases

- Projekt ohne Kanban-View → `RuntimeError` mit klarer, handlungsweisender Meldung (Nutzer/LLM wird auf die Vikunja-UI verwiesen).
- `update_bucket` ohne jegliche Parameter (ausser IDs) → `ValueError("No fields to update")`, kein API-Call.
- `update_bucket` mit `bucket_id`, die nicht in der Bucket-Liste des Projekts existiert → `RuntimeError`.
- `move_task_to_bucket` mit `task_id` aus einem Projekt ohne Kanban-View → `RuntimeError` (gleiche Meldung wie oben, über den Helper durchgereicht).
- Vikunja-API offline / ungültiger Token → bereits zentral durch `_request` abgefangen, keine neue Behandlung nötig.

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

### Level 2: Manual Validation

1. Server starten via `npx @modelcontextprotocol/inspector uv run altiplano`.
2. **Voraussetzung (Task 1):** Verifikation gegen die echte Instanz wie in Task 1 beschrieben durchführen.
3. `list_buckets` mit einer echten `project_id` aufrufen — Erwartung: Liste der Standard-Buckets (z.B. "Backlog"), keine Fehler.
4. `create_bucket` mit `project_id` und `title="Testing"` aufrufen — Erwartung: neuer Bucket erscheint in der Vikunja-Web-UI im Kanban-Board.
5. `update_bucket` mit der neuen `bucket_id` und `title="Renamed"` aufrufen — Erwartung: Bucket ist in der UI umbenannt, `limit` unverändert.
6. `move_task_to_bucket` mit einer echten `task_id` und der neuen `bucket_id` aufrufen — Erwartung: Task erscheint in der Vikunja-Kanban-Ansicht im Ziel-Bucket.

## Acceptance Criteria

- [x] Feature implementiert alle Scope-Anforderungen
- [x] Typvalidierung und API-Fehlerbehandlung sind korrekt
- [x] Relevante pytest-Tests sind ergänzt und grün
- [x] Relevante manuelle Flows sind validiert (insb. Task 1 Verifikation gegen die echte Instanz)
- [x] Keine bekannten Regressionen in bestehenden Kernworkflows
- [x] Dokumentationsbedarf ist notiert

## Completion Checklist

- [x] Alle Tasks sind umgesetzt
- [x] Jeder Task wurde validiert
- [x] Alle relevanten Tests laufen erfolgreich oder Ausnahmen sind begründet
- [x] Manuelle Prüfung (MCP Inspector / Vikunja-UI) ist dokumentiert
- [x] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt
- [x] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Nach Abschluss sollen `user-guide.md` und `developer-notes.md` im Feature-Ordner `docs/project/features/kanban-buckets/` ergänzt werden (via `/document`). Inhaltlich relevant:
- Endanwender: Wie lege ich Buckets an, wie weise ich Tasks zu, was passiert, wenn ein Projekt keine Kanban-Ansicht hat (klare Fehlermeldung statt automatischer Erstellung).
- Entwickler: Erklärung der Views-Ebene, warum sie versteckt wird, Verweis auf die `go-vikunja/vikunja`-Quellcode-Referenzen als Beleg für die API-Form, Hinweis auf die PRD-Kapitel-9-Abweichung.

## Notes and Trade-offs

- Die Views-Komplexität wird bewusst serverseitig versteckt (siehe Architekturentscheidungen) — das hält die Tool-Oberfläche schlank, bedeutet aber einen zusätzlichen `GET`-Request pro Bucket-Tool-Aufruf ohne Caching. Bei zukünftigem Performance-Bedarf könnte ein kurzlebiger In-Memory-Cache für `project_id → kanban_view_id` erwogen werden — nicht Teil dieses Plans.
- PRD Kapitel 9 Datenmodell für `Bucket` ist unvollständig (fehlt `project_view_id`/Views-Ebene). Dieser Plan dokumentiert die reale Struktur und löst sie auf, schlägt aber keine stille PRD-Korrektur vor — Empfehlung für eine separate `/update-prd`-Runde, analog zur in PRD Kapitel 14 bereits dokumentierten Praxis, offene Fragen explizit zu vermerken statt sie zu verstecken.
- Bewusst kein gemeinsamer generischer „GET-Overlay"-Helper trotz der dritten Wiederholung des Patterns (`update_project`, `update_task`, jetzt `update_bucket`) — konsistent mit der in `task-project-tool-fixes/plan-v001.md` getroffenen Entscheidung, den Diff klein zu halten. Bei einer vierten Wiederholung sollte eine Extraktion als eigenständiges Refactoring-Feature erwogen werden.

## Offene Fragen

- ~~Bestätigt Task 1 die angenommene Views/Buckets-API-Form gegen die echte Instanz?~~ Geklärt: ja, siehe Task 1 Validierungsergebnis (2026-06-25).
- Soll `delete_bucket` in einer späteren Iteration ergänzt werden? Aktuell laut PRD Kapitel 6/15 nicht im Scope der Medium-Phase.
- Soll PRD Kapitel 8/9 in einer separaten `/update-prd`-Runde um die Views-Ebene ergänzt werden? Empfehlung: ja, nicht blockierend für diesen Plan.

## Plan Review Notes

(Wird durch `/integrate-feature-plan-review` in einer späteren Plan-Version ergänzt. Beim initialen `plan-v001.md`: nicht relevant.)
