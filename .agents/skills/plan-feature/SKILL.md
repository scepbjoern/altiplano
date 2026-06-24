---
name: plan-feature
description: >
  Turns a feature idea or PRD reference into a granular, reviewable, versioned implementation plan for this starter kit. Use it when a new feature needs an initial plan before review and before code is written. ONLY activate when the user explicitly runs /plan-feature or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  piv-phase: plan
  version: "3.0"
disable-model-invocation: true
argument-hint: "[feature-description-or-prd-reference]"
---

# Plan Feature: Feature Planen

## Input

Feature-Beschreibung oder Referenz auf bestehende Datei: `$ARGUMENTS`

Beispiele:

- `/plan-feature MCP-Label-Tools hinzufügen`
- `/plan-feature docs/project/prds/vikunja-mcp-v002.md Kapitel Tasks`

## Grundregel

Schreibe in dieser Phase keinen Produktivcode. Ziel ist ein reviewbarer, kontextreicher initialer Plan als Grundlage für `/review-feature-plan`.

Qualitätsziel: Der initiale Plan `plan-v001.md` soll so vollständig sein, dass er in einer frischen Reviewer-Session kritisch geprüft werden kann. Nach Review und Integration entsteht mindestens `plan-v002.md`; erst eine fachlich bestätigte, reviewte Plan-Version ist autoritative Arbeitsgrundlage für `/execute`.

## Phase 1: Initiales Feature-Verständnis

Verstehe zuerst grob, was gebaut werden soll. Stelle in dieser frühen Phase nur Fragen, wenn ohne Antwort keine sinnvolle Recherche starten kann.

Ermittle initial:

- Welches Problem löst das Feature?
- Welche MCP-Tools oder API-Aufrufe sind betroffen?
- Was ist im Scope und was explizit nicht?
- Welche Daten, Mappings oder API-Endpunkte (Vikunja) sind betroffen?
- Gibt es ein PRD oder bestehende Dokumentation unter `docs/`?
- Welche manuelle Prüfung soll am Ende möglich sein?

Erstelle oder verfeinere eine vorläufige User Story:

```text
Als <Rolle/Konsument>
möchte ich <Aktion/Ziel>,
damit <Nutzen/Wert>.
```

Klassifiziere das Feature vorläufig:

- Feature-Typ: New Capability, Enhancement, Refactor oder Bug Fix
- Komplexität: Low, Medium oder High
- Primär betroffene Systeme: FastMCP, httpx client, server.py, Tests
- Abhängigkeiten: externe Libraries, ENV-Werte, offene Entscheidungen

Wenn Anforderungen unklar sind, aber durch Repo- oder Dokumentationsrecherche wahrscheinlich geklärt werden können, recherchiere zuerst selbst.

## Phase 2: Relevanten Kontext Lesen

Lies mindestens:

- Relevante PRD- oder Konzeptdatei unter `docs/`, falls genannt oder auffindbar
- `KILO_INSTRUCTIONS.md`
- `AGENTS.md`
- `TASKS.md`
- `pyproject.toml`
- `src/altiplano/server.py`
- Ähnliche Implementierungen oder pytest-Dateien unter `tests/`

Nutze bestehende Patterns. Erfinde keine parallele Architektur.

Analysiere explizit:

- Projektstruktur, Sprachen, Frameworks und Runtime-Versionen (Python, fastmcp)
- Schnittstellen und Tool-Definitionen in `src/altiplano/server.py`
- ähnliche Implementierungen in der Codebase
- Naming-, Datei- und Fehlerbehandlungs-Patterns in Python
- externe Dependencies, Versionen und Integrationsweise (in pyproject.toml)
- bestehende Teststruktur und ähnliche pytest-Beispiele

## Phase 3: Externe Recherche und Dokumentation

Nutze externe Recherche nur, wenn sie für korrekte Planung nötig ist, z.B. bei FastMCP API, httpx oder pytest.

Dokumentiere Referenzen im Plan mit:

- Link zur offiziellen Dokumentation
- spezifischem Abschnitt oder Thema
- kurzer Begründung, warum diese Referenz relevant ist

## Phase 4: Menschliche Präzisierung nach Recherche

Stelle nach Phase 2 und 3 gezielte Rückfragen, wenn wichtige Punkte nicht selbst aus Repo, PRD, Dokumentation oder offiziellen Quellen ableitbar sind.

Frage nur nach Entscheidungen, nicht nach Informationen, die du selbst recherchieren kannst. Gute Rückfragen betreffen zum Beispiel:

- fachlicher Scope oder Non-Scope
- gewünschtes Verhalten bei Statuswechseln oder API-Fehlern
- Priorisierung zwischen zwei plausiblen Architekturvarianten
- unklare Akzeptanzkriterien

Plane nicht auf Basis kritischer Annahmen. Dokumentiere nichtkritische Annahmen ausdrücklich im Plan.

## PRD-Inkonsistenz erkannt

Wenn du beim Planen feststellst, dass das PRD widersprüchlich, unvollständig oder fachlich nicht mehr aktuell ist, stoppe die Feature-Planung.

Führe keine stille Korrektur im Feature-Plan durch und plane nicht um das Problem herum.

Erkläre dem Nutzer konkret:

- welche PRD-Stelle problematisch ist
- warum daraus kein belastbarer Feature-Plan entstehen kann
- welche Entscheidung, Ergänzung oder Korrektur im PRD nötig ist

Fordere den Nutzer auf, zuerst `/update-prd [PRD-Pfad]` auszuführen. Danach soll `/plan-feature` mit der neuen PRD-Version erneut gestartet werden.

Wenn durch die PRD-Aktualisierung bereits vorhandene Feature-Pläne betroffen sind, weise darauf hin, dass dafür `/update-feature-plan [Plan-Pfad]` genutzt werden soll.

## Phase 5: Strategisches Durchdenken

Denke vor der Plan-Datei explizit durch:

- Wie passt das Feature in die bestehende Architektur?
- Welche Reihenfolge und Abhängigkeiten sind kritisch?
- Welche Edge Cases, API-Fehler oder Verbindungsabbrüche können auftreten?
- Welche Security-, Performance- und Maintainability-Risiken gibt es?
- Welche Alternativen wurden erwogen und warum wird der gewählte Ansatz bevorzugt?

## Phase 6: Architektur- und Datei-Entscheide

Dokumentiere im Plan:

- Betroffene bestehende Dateien (z.B. `src/altiplano/server.py`)
- Neue Dateien mit Begründung (z.B. neue Testmodule in `tests/`)
- konkrete Patterns to Follow mit Beispielen oder Dateireferenzen
- FastMCP tool decorators, Argumente und Typen
- API-Anbindung (httpx endpoint Mappings)
- Unit- und Integrationstest-Strategie mit pytest
- Edge Cases und Regressionen

## Phase 7: Plan-Datei Erstellen

Erstelle eine Markdown-Datei unter:

```text
docs/project/features/[feature-name]/plan-v001.md
```

Nutze kebab-case für `[feature-name]`, z.B. `docs/project/features/mcp-label-tools/plan-v001.md`.

Die Datei ist kombinierter Spec+Plan+Tasks-Container. Verwende `references/plan-template.md` als Ausgangspunkt und fülle alle relevanten Abschnitte konkret aus.

Dokumentiere im Plan selbst die Plan-Version `v001` und fülle im Abschnitt `## Plan-Änderungshistorie` mindestens den Eintrag für `v001` aus. Wenn ein Feature-Ordner bereits eine `plan-v001.md` enthält, stoppe und frage den Nutzer.

Task-Format:

- Nutze Aktionskeywords wie `CREATE`, `UPDATE`, `ADD`, `REMOVE`, `REFACTOR`, `MIRROR`.
- Jeder Task muss aus Nutzersicht sinnvoll validierbar sein.
- Jeder Task muss `IMPLEMENT`, `PATTERN`, `IMPORTS`, `GOTCHA`, `ACCEPTANCE CRITERIA` und `VALIDATE` enthalten, sofern anwendbar.
- Jeder Task startet mit Status `planned`.

VALIDATE-Abschnitt: Unterscheide explizit zwischen automatisierten und manuellen Prüfungen:

- **Automatisiert:** Nenne den genauen Befehl (z.B. `uv run pytest`) und das erwartete Ergebnis.
- **Manuell:** Beschreibe Schritt für Schritt, was der Mensch tun muss: wie der Server gestartet wird, welche Argumente im MCP Inspector einzugeben sind und was das erwartete JSON-Ergebnis ist.

## Phase 8: Plan-Qualität Prüfen

Prüfe den Plan vor dem Speichern gegen diese Kriterien:

- Context Completeness: Pflichtlektüre, Patterns, Gotchas und Docs sind spezifisch.
- Implementation Ready: Ein anderer Agent kann top-to-bottom umsetzen.
- Pattern Consistency: Bestehende Architektur und Konventionen werden eingehalten.
- Validation Complete: Jeder Task hat konkrete Validierungsschritte (pytest / Inspector).
- Edge Cases: relevante Fehlerfälle (API offline, ungültige Tokens) sind bedacht.
- Documentation Ready: spätere Endanwender- und Entwicklerdokumentation ist mitgedacht.

Vergib einen Confidence Score `#/10` für die Wahrscheinlichkeit, dass `/execute` den Plan taskweise erfolgreich umsetzen kann. Begründe Werte unter 8 kurz.

## Phase 9: Root-TASKS.md Aktualisieren

Nach Erstellung der Plan-Datei aktualisiere `TASKS.md` als Feature-Index.

## Output

Zeige danach:

- Pfad der erstellten Plan-Datei
- Kurzzusammenfassung des Ansatzes
- Confidence Score für die Umsetzung
- Offene Fragen oder Annahmen
- Hinweis auf Committen von `v001`
- Hinweis: Als nächster Schritt soll eine neue Reviewer-Session gestartet werden: zuerst `/prime`, danach `/review-feature-plan [Plan-Pfad]`.
