---
name: document
description: >
  Creates end-user and developer documentation for an implemented and validated feature based on its confirmed versioned plan, implementation results, and validation evidence, then points to /reflect-rules when there is suspicion of repeated agent mistakes, plan gaps, unusual rework, or repeated user corrections before the final /commit. ONLY activate when the user explicitly runs /document or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  piv-phase: validate
  version: "4.0"
disable-model-invocation: true
argument-hint: "[path-to-plan]"
---

> **KiloCode-Modus:** Dieser Skill muss im **Code-Modus** ausgeführt werden. Im Architect- oder Plan-Modus beschränkt KiloCode Schreibrechte auf `.kilo/`-Ordner – Dokumentationsdateien würden dort abgelegt statt in `docs/`. Wechsle in KiloCode vor der Ausführung auf den **Code-Modus**.

# Document: Feature Dokumentieren

## Input

Pfad zur vollständig umgesetzten und validierten Plan-Datei: `$ARGUMENTS`

Beispiel:

```text
/document docs/project/features/mcp-label-tools/plan-v002.md
```

## Ziel

Erstelle die abschliessende Feature-Dokumentation als letzte Dokumentationsstufe vor dem finalen `/commit`. Wenn es Verdacht auf wiederholbare Agent-Fehler, Planlücken, ungewöhnliche Nacharbeiten oder wiederholte Nutzerkorrekturen gibt, soll vorher in derselben Session `/reflect-rules` empfohlen werden. Die Dokumentation beschreibt nur den bestätigten, umgesetzten und validierten Stand eines einzelnen Features.

Der Skill trennt konsequent zwischen:

- Endanwenderdokumentation (User Guide): Welche MCP-Tools stehen bereit und wie nutzt oder demonstriert man das Feature?
- Entwicklerdokumentation (Developer Notes): Wie ist das Feature technisch umgesetzt und wartbar?

## Grundregeln

- Schreibe keine neuen Produktivcode-Änderungen.
- Dokumentiere genau ein Feature pro Durchlauf.
- Verwende die Plan-Datei aus `$ARGUMENTS` als autoritative Quelle.
- Beschreibe nur implementierten und validierten Scope. Erfinde keine Funktionen, Tools, APIs oder Tests.
- Dokumentiere Abweichungen nur, wenn sie im Plan oder in genehmigten Umsetzungsergebnissen nachvollziehbar sind.
- Schreibe fachliche Projektdokumentation auf Deutsch. Technische Begriffe wie API, MCP, Tool, fastmcp oder pytest dürfen Englisch bleiben.
- Schreibe keine Secrets, echten Zugangsdaten, vertraulichen Unternehmensdetails oder personenbezogenen Echtdaten in die Dokumentation.
- Im Mehrpersonen-Fall: Bearbeite nur den Feature-Ordner des eigenen bestätigten Features und überschreibe keine fremden Feature-Dokumente.

## Preconditions

Der Skill darf finale Dokumentation nur erstellen, wenn alle Bedingungen erfüllt sind:

- `$ARGUMENTS` zeigt auf `docs/project/features/[feature-name]/plan-vNNN.md`.
- Die Plan-Datei existiert und gehört zu genau einem Feature.
- Die Feature-Plan-Version wurde vor `/execute` reviewed und integriert oder mit `/update-feature-plan` versioniert aktualisiert, danach fachlich bestätigt und committed.
- Alle relevanten Tasks im Plan stehen auf `done` oder begründete Ausnahmen sind im Plan dokumentiert.
- Validierungsergebnisse sind im Plan dokumentiert, z.B. `uv run pytest` oder manuelle Prüfung via MCP Inspector.
- Plan-/PRD-Abweichungen sind genehmigt und im Plan dokumentiert.

Wenn diese Bedingungen nicht erfüllt sind:

- Erstelle keine finale `user-guide.md` oder `developer-notes.md`.
- Erkläre kurz, welche Voraussetzung fehlt.
- Empfiehl den passenden nächsten Workflow, meistens `/execute docs/project/features/[feature-name]/plan-vNNN.md` oder Nachdokumentation der Validierung im Plan.

## Output-Artefakte

Erstelle oder aktualisiere im selben Feature-Ordner:

```text
docs/project/features/[feature-name]/user-guide.md
docs/project/features/[feature-name]/developer-notes.md
```

Optional nur bei klarer Relevanz oder wenn im Plan vorgesehen:

- `docs/project/features/[feature-name]/validation-notes.md` für ausführliche manuelle Validierungsprotokolle, wenn diese den Plan sprengen würden.
- `docs/project/operations/demo-checklist.md` als gemeinsames Demo-Dokument, aber nur wenn das Feature den projektweiten Demo-Ablauf verändert.
- `docs/project/decisions/adr-[nummer]-[thema].md`, wenn während Umsetzung eine dauerhafte Architektur- oder Fachentscheidung entstanden ist. Wenn die Entscheidung nicht genehmigt ist, nur vorschlagen und nicht selbst anlegen.

`docs/INDEX.md` muss normalerweise nicht pro Feature aktualisiert werden, weil die Feature-Dokumentationsstruktur dort bereits beschrieben ist.

## Pflichtlektüre

Lies vor dem Schreiben vollständig:

- Plan-Datei aus `$ARGUMENTS`
- `TASKS.md`
- `AGENTS.md`
- `KILO_INSTRUCTIONS.md`
- Bestehende `user-guide.md` und `developer-notes.md` im Feature-Ordner, falls vorhanden
- Relevantes PRD unter `docs/project/prds/`, falls im Plan referenziert
- Relevante Guides aus `docs/starter-kit-usage/`, wenn das Feature Testing oder Setup betrifft
- Betroffene Implementierungsdateien aus der Plan-Datei und, falls nötig, aus `git diff HEAD --name-only`

Nutze `git status` und `git diff HEAD --name-only`, um die dokumentierten Änderungen mit dem Arbeitsbaum abzugleichen. Verwende Git dabei nur lesend. Keine Commits, kein Staging, kein Checkout, kein Reset.

## Phase 1: Input Prüfen

1. Prüfe, ob `$ARGUMENTS` gesetzt ist.
2. Normalisiere den Pfad relativ zum Repository.
3. Prüfe, ob der Pfad dem Muster `docs/project/features/[feature-name]/plan-vNNN.md` entspricht.
4. Leite `[feature-name]` aus dem Ordnernamen ab.
5. Prüfe, ob der Feature-Ordner existiert.
6. Prüfe, ob bestehende Dokumentationsdateien vorhanden sind und gelesen werden müssen.

Wenn der Pfad nicht eindeutig ist, stoppe und fordere einen gültigen Plan-Pfad an.

## Phase 2: Implementierungsstand Verstehen

Extrahiere aus Plan, Validierungsnotizen und Implementierung:

- Feature-Name, Zweck und Problemstellung
- User Story und Zielrollen
- Scope und Non-Scope
- MVP / Medium / Extended, falls im PRD oder Plan unterschieden
- betroffene MCP-Tools, API-Requests (Vikunja), Helferfunktionen oder Mocks
- Validierungsergebnisse und manuelle Prüfschritte
- bekannte Einschränkungen, Risiken und spätere Erweiterungen
- genehmigte Plan-/PRD-Abweichungen

Gleiche diese Informationen gegen die tatsächlich betroffenen Dateien ab. Wenn Plan und Implementierung widersprüchlich sind, stoppe und beschreibe den Widerspruch.

## Phase 3: Dokumentationsbedarf Klassifizieren

Entscheide für dieses Feature konkret:

- Welche MCP-Tools werden bereitgestellt? Welche Argumente erwarten sie?
- Gibt es einen Demo-Ablauf, der Schritt für Schritt beschrieben werden muss?
- Welche technischen Entscheidungen müssen Entwickler später nachvollziehen können?
- Welche Dateien, Patterns und Tests sind für Wartung und Erweiterung relevant?
- Gibt es Betriebs- oder Setup-Hinweise, z.B. neue Umgebungsvariablen?

Wenn ein Abschnitt nicht relevant ist, schreibe `Nicht relevant` mit kurzer Begründung. Entferne Qualitätsabschnitte nicht nur deshalb, weil sie kurz ausfallen.

## Phase 4: `user-guide.md` Schreiben

Zielgruppe: Endanwender, Demo-Publikum und fachliche Prüfer.

Struktur:

```markdown
# User Guide: <Feature-Name>

## Überblick

<Was kann der MCP-Server mit diesem Feature tun (z.B. welche Tools stellt es bereit) und warum ist es nützlich?>

## MCP-Tools

| Tool-Name | Beschreibung | Argumente | Rückgabewert |
|---|---|---|---|

## Voraussetzungen

- <Vikunja-API-Berechtigungen, vorhandene Daten, ENV-Konfigurationen oder Nicht relevant>

## Schritt-für-Schritt Demo

1. <MCP Inspector starten oder in Claude Desktop einbinden>
2. <Konkreter Tool-Aufruf mit Beispielargumenten>
3. <Erwartetes Ergebnis in der API-Antwort und im Vikunja UI>

## Bekannte Einschränkungen

- <Nur dokumentierte Einschränkungen oder Nicht relevant>
```

Regeln:

- Keine internen Implementierungsdetails.
- Keine Dateipfade, ausser sie sind für die Demo oder Bedienung wirklich nötig.
- Beschreibe Tools und Aktionen so, wie sie tatsächlich über MCP verfügbar sind.

## Phase 5: `developer-notes.md` Schreiben

Zielgruppe: Entwicklerinnen, Entwickler und spätere Agent-Sessions.

Struktur:

```markdown
# Developer Notes: <Feature-Name>

## Überblick

<Technischer Zweck und Einordnung des Features.>

## Referenzen

- Plan: `docs/project/features/<feature-name>/plan-vNNN.md`
- PRD: `<Pfad oder Nicht relevant>`
- Relevante Guides: `<Pfade oder Nicht relevant>`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|

## Architektur und Datenfluss

<Wie arbeiten FastMCP, die httpx-Requests und die Vikunja-API zusammen?>

## Datenmodell und API-Mapping

<Wie werden Vikunja-API-Shapes in MCP-Datenstrukturen übersetzt? Gibt es Mocks oder Fallbacks?>

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|

## Betriebs- und Setup-Hinweise

- <Neue ENV-Werte, lokale Konfigurationsdateien oder Nicht relevant>

## Wartungshinweise

- <Gotchas, bewusst gewählte Patterns, Risiken, spätere Erweiterungen>

## Bekannte Einschränkungen

- <Nur bestätigte Einschränkungen oder Nicht relevant>
```

Regeln:

- Nenne konkrete Dateien und Verantwortlichkeiten, aber kopiere keinen grossen Code in die Dokumentation.
- Verweise auf bestehende Patterns, wenn sie für spätere Erweiterungen wichtig sind.
- Dokumentiere Tests mit Befehl und Ergebnis, aber fälsche keine Testresultate. Wenn ein Check nicht ausführbar war, schreibe Grund und manuelle Alternative.

## Phase 6: Bestehende Dokumentation Aktualisieren

Wenn `user-guide.md` oder `developer-notes.md` bereits existieren:

1. Lies die bestehende Datei vollständig.
2. Erhalte manuelle, weiterhin korrekte Inhalte.
3. Entferne oder korrigiere nur Inhalte, die nach Plan und Implementierung veraltet sind.
4. Überschreibe keine fremden Notizen ohne klaren Grund.
5. Halte die finale Datei konsistent.

## Phase 7: Plan-Datei Nachführen

Aktualisiere die Plan-Datei nur dokumentationsbezogen:

- Markiere in der `Completion Checklist`, falls vorhanden, dass das Feature dokumentiert wurde.
- Ergänze unter `Documentation Notes` oder einem neuen Abschnitt `Documentation Results` die erzeugten Dateien.
- Dokumentiere keine neuen fachlichen Scope-Entscheidungen ohne menschliche Bestätigung.
- Ändere Task-Status nur, wenn ein bestehender Dokumentations-Task im Plan ausdrücklich dafür vorgesehen ist.

## Phase 8: Qualitätsprüfung

Prüfe vor Abschluss:

- Stimmen Feature-Name, Tool-Namen, Argumente, Pfade und Befehle mit Plan und Code überein?
- Sind `user-guide.md` und `developer-notes.md` klar getrennt?
- Ist der dokumentierte Scope wirklich implementiert und validiert?
- Sind relative Links und Dateipfade korrekt?
- Enthält die Dokumentation keine Secrets, privaten Daten oder falschen Produktivversprechen?
- Wurden optionale projektweite Dokumente nur geändert, wenn es nötig und begründet war?

## Abschluss

Gib nach dem Schreiben aus:

- erstellte oder aktualisierte Dateien
- kurze Zusammenfassung pro Datei
- dokumentierte Validierungsbasis (z.B. pytest-Ergebnisse)
- offene Annahmen, Risiken oder nicht ausführbare Prüfungen
- Hinweis, dass bei Verdacht auf Agent-Fehler jetzt in derselben Session `/reflect-rules docs/project/features/[feature-name]/plan-vNNN.md` genutzt werden soll
- Hinweis, dass danach der finale Commit erfolgen soll (z.B. mit `/commit` oder VS Code)

Wenn keine Dateien geschrieben wurden, erkläre knapp den Blocker und den konkreten nächsten Schritt.
