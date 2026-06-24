# Getting Started – Starter Kit für eigenes Projekt anpassen

Dieses Dokument erklärt die ersten Schritte, um das Starter Kit für euren eigenen Vikunja MCP-Server vorzubereiten.

---

## 1. Projektkontext definieren

Öffne `AGENTS.md` im Wurzelverzeichnis und ersetze alle `[TODO]`-Einträge:

- **Projektbeschreibung:** Welcher Integrations-Scope wird abgebildet? Welche Vikunja-API-Bereiche (z.B. Projekte, Tasks, Labels) werden angebunden?
- **Rollen:** MCP-Server haben meist keine eigenen Benutzerrollen (da API-basiert), aber dokumentiert hier, welche Berechtigungsstufe das verwendete Vikunja-Token besitzt.
- **Scope:** Was ist im / ausserhalb des Scope?
- **Team-Info:** Gruppenname, Mitglieder, Kursjahrgang

---

## 2. Umgebungsvariablen setzen

Befülle `.env` (oder `~/.config/altiplano/env`) mit den benötigten Werten für die Vikunja-Verbindung.

```env
VIKUNJA_URL="https://todo.example.com/api/v1"   # Eure Vikunja-API-URL
VIKUNJA_API_TOKEN="tk_..."                       # Euer persönlicher Vikunja-API-Token
```

Alternativ könnt ihr die Variablen direkt in eurer Shell exportieren oder das MCP-Konfigurations-File des Clients nutzen.

---

## 3. PRD erstellen und reviewen

Das PRD (Product Requirements Document) beschreibt euren MCP-Server: die angebotenen Tools, den Scope der API-Anbindung und die Ausbaustufen.

```text
/create-prd docs/project/prds/[systemname].md
```

Der Skill führt euch durch einen Dialog und schreibt das PRD.
Danach folgt mindestens eine kritische Review-Runde in einer frischen Agent-Session:

```text
/review-prd docs/project/prds/[systemname]-v001.md
```

Zurück in der Autor-Session integriert ihr den Review. Dabei entsteht eine neue PRD-Version, typischerweise `v002`:

```text
/integrate-prd-review docs/project/prds/[systemname]-v001.md docs/project/prd-reviews/[systemname]-v001-r01-review.md
```

Prüft die neue PRD-Version sorgfältig und bestätigt sie erst, wenn sie als Grundlage für die Feature-Planung taugt. Danach separat committen.

Wenn sich später fachlich etwas am PRD ändert, nutzt:

```text
/update-prd docs/project/prds/[systemname]-v002.md
```

---

## 4. Starter Kit bereinigen

Nach PRD-Review und Bestätigung der neuesten PRD-Version bereinigt `/adapt-to-project` den Workspace: Nicht benötigte Tools oder Hilfsfunktionen werden entfernt. Der Skill validiert am Ende den Code durch Tests.

```text
/adapt-to-project docs/project/prds/[systemname]-v002.md
```

Testet danach mit `uv run altiplano` oder `uv run pytest`, ob der Server korrekt hochfährt und alle Tests grün sind.

---

## 5. Features bauen

Ab jetzt wiederholt ihr für jedes Feature aus dem PRD denselben Zyklus. Die vollständige Anleitung steht in [`PIV-WORKFLOW.md`](PIV-WORKFLOW.md).

Kurzablauf pro Feature:

1. Neue Agent-Session starten, `/prime` ausführen
2. `/plan-feature "[Feature aus PRD]"` – Agent erstellt `docs/project/features/[feature-name]/plan-v001.md`
3. Initialen Plan und `TASKS.md` committen
4. Neue Reviewer-Session starten, `/prime`, dann `/review-feature-plan docs/project/features/[feature-name]/plan-v001.md`
5. Zurück in die Autor-Session, `/integrate-feature-plan-review ...` – Agent erstellt typischerweise `plan-v002.md` und aktualisiert `TASKS.md`
6. Neue Plan-Version prüfen, bestätigen und committen
7. `/execute docs/project/features/[feature-name]/plan-v002.md` – Task für Task umsetzen
8. Nach jedem Task: `uv run pytest` und manuelle Prüfung (z.B. via Claude Desktop)
9. Wenn alle Tasks `done`: `/document` ausführen, bei Verdacht auf wiederholbare Fehler `/reflect-rules`, dann `/commit`

`TASKS.md` ist nur ein Feature-Index. Detailtasks und Validierung liegen immer in der jeweiligen Datei `docs/project/features/[feature-name]/plan-vNNN.md`.
gen Datei `docs/project/features/[feature-name]/plan-vNNN.md`.
