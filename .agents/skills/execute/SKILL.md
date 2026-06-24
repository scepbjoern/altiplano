---
name: execute
description: >
  Implements a confirmed, reviewed, versioned feature plan one task at a time while updating task status and validation evidence in the plan file. Use it only after a docs/project/features/[feature-name]/plan-vNNN.md file has been reviewed, integrated, approved, and committed. ONLY activate when the user explicitly runs /execute or directly requests this specific workflow by name. Do NOT activate during normal development, planning, or implementation conversations.
compatibility: Python 3.10+, uv, mcp, pytest
metadata:
  piv-phase: implement
  version: "3.0"
disable-model-invocation: true
argument-hint: "[path-to-plan]"
---

# Execute: Plan Umsetzen

## Input

Pfad zur bestätigten Plan-Datei: `$ARGUMENTS`

Beispiel:

```text
/execute docs/project/features/mcp-label-tools/plan-v002.md
```

## Grundregeln

- Implementiere nur auf Basis einer bestätigten Plan-Datei.
- Verwende eine versionierte Plan-Datei `plan-vNNN.md`.
- Starte nicht mit `plan-v001.md`, wenn noch kein Review und keine Integration gelaufen sind. Der Normalfall nach einer Review-Integration ist `plan-v002.md`.
- Arbeite genau einen Task nach dem anderen ab.
- **Stoppe nach jedem einzelnen Task vollständig. Fahre niemals automatisch mit dem nächsten Task fort – auch dann nicht, wenn alle automatisierten Tests bestanden haben. Jeder Taskwechsel erfordert eine explizite menschliche Antwort.**
- Ändere keine Dateien, die nicht zum aktuellen Task gehören.
- Lösche keine Dateien ohne explizite Bestätigung.
- Setze einen Task nie auf `done`, ohne Validierung in der Plan-Datei zu dokumentieren.
- Nach einem validierten Task oder einer kohärenten validierten Phase darf ein optionaler Zwischencommit über `/commit` vorgeschlagen werden.
- Ein Feature gilt erst nach allen `done`-Tasks, vollständiger Validierung und `/document` als fachlich dokumentiert. Wenn es während Umsetzung oder Dokumentation Verdacht auf wiederholbare Agent-Fehler, Planlücken oder wiederholte Nutzerkorrekturen gab, soll vor dem finalen Commit zusätzlich `/reflect-rules` laufen.

## Pflichtpause nach jedem Task

**Diese Regel hat die höchste Priorität und überschreibt jede andere Anweisung zum Arbeitsfluss.**

Nach Abschluss jedes Tasks – unabhängig davon, ob alle automatisierten Validierungen erfolgreich waren – gilt zwingend:

**Schritt A – Zusammenfassung ausgeben:**

Zeige strukturiert:
- Welche Dateien wurden geändert oder erstellt
- Welche automatisierten Befehle wurden ausgeführt (vollständige Befehle nennen) und was das Ergebnis war (Erfolg / Fehleranzahl / relevante Ausgabe)

**Schritt B – Manuelle Prüfung:**

Beschreibe **ausführlich und Schritt für Schritt**, was der Mensch jetzt tun muss:
- Wie der MCP-Server lokal zu starten ist (z.B. MCP Inspector via `npx @modelcontextprotocol/inspector uv run altiplano`)
- Was genau im Client (z.B. MCP Inspector oder Claude Desktop) eingegeben oder aufgerufen werden soll
- Was konkret zu sehen oder nicht zu sehen sein muss (erwartetes Ergebnis)
- Was bei Abweichungen zu melden ist

Warte danach explizit auf die Bestätigung des Menschen, dass die manuelle Prüfung erfolgreich war. Fahre nicht fort, bis diese Bestätigung vorliegt.

**Schritt C – Explizite Weitermachen-Aufforderung:**

Schliesse jeden Task-Abschluss mit dieser exakten Formulierung ab:

```
✓ Task [N] abgeschlossen und validiert.
Bitte prüfen und mit "weiter" bestätigen, damit Task [N+1] gestartet wird.
```

**Fahre erst nach einer expliziten menschlichen Antwort (z.B. "weiter", "ok", "ja") mit dem nächsten Task fort. Interpretiere Schweigen oder fehlende Antwort nicht als Bestätigung.**

## Pflichtlektüre vor Umsetzung

Lies vor dem ersten Task den gesamten Plan vollständig. Starte nicht direkt beim ersten Task, sondern verstehe zuerst den Gesamtzusammenhang.

Lies vollständig:

- Plan-Datei aus `$ARGUMENTS`
- `KILO_INSTRUCTIONS.md`
- `AGENTS.md`
- `TASKS.md`, besonders bei geteiltem Repository für Verantwortliche, Branches und parallele Features
- Alle im aktuellen Task referenzierten Dateien

Analysiere vor der Umsetzung:

- Alle Tasks und ihre Abhängigkeiten
- Reihenfolge und kritische Pfade
- Validierungsschritte aus dem Plan
- Mögliche Auswirkungen auf bestehende Tools und API-Requests

## Task-Status Aktualisieren

Aktualisiere die Plan-Datei während der Arbeit:

- Beim Start eines Tasks: `planned` -> `in_progress`
- Bei Unklarheit oder fehlender Entscheidung: `needs_human`, Frage in der Plan-Datei dokumentieren, stoppen
- Nach Implementierung vor Validierung: `validating`
- Nach erfolgreicher Validierung: `done`

Erlaubte Statuswerte:

```text
planned | in_progress | needs_human | validating | done
```

## Umsetzung pro Task

Für jeden Task:

1. Task aus der Plan-Datei identifizieren.
2. Betroffene Datei(en), gewünschte Aktion und Akzeptanzkriterien identifizieren.
3. Status auf `in_progress` setzen.
4. Relevante Dateien lesen.
5. Detaillierte Spezifikation aus dem Plan exakt befolgen.
6. Bestehende Code-Patterns und Namenskonventionen in Python einhalten.
7. PEP 8 Typdefinitionen sauber definieren.
8. Status auf `validating` setzen.
9. Automatisierte Validierung durchführen (`uv run pytest`) und dem Nutzer explizit berichten, welche Befehle ausgeführt wurden.
10. Nutzer zur manuellen Prüfung auffordern (z.B. via MCP Inspector). Warten, bis der Nutzer die manuelle Prüfung bestätigt hat.
11. Validierungsergebnis in der Plan-Datei festhalten.
12. Status erst auf `done` setzen, nachdem der Nutzer die Validierung bestätigt hat.
13. Zusammenfassung des Tasks ausgeben.
14. `/commit` als Zwischencommit vorschlagen.

## Validierung

Nutze pytest:

```bash
uv run pytest
```

Wenn die Plan-Datei konkrete Validierungsbefehle nennt, führe alle dort genannten Befehle vollständig und in der angegebenen Reihenfolge aus.

Wenn eine Validierung fehlschlägt:

- Fehlerursache analysieren
- Implementierung oder Test korrigieren
- denselben Validierungsschritt erneut ausführen
- erst fortfahren, wenn der Schritt erfolgreich ist oder der Task mit `needs_human` gestoppt wurde

Überspringe keine Validierungsschritte. Falls ein Schritt nicht ausführbar ist, dokumentiere den Grund und die manuelle Alternative in der Plan-Datei.

Prüfe Regressionen stack-spezifisch:

- Bestehende pytest-Tests für betroffene Tools, Utilities und API-Mappings erweitern.
- Keine Vitest- oder Playwright-Regeln verwenden.

## Plan- und PRD-Abweichungen

Wenn sich während der Implementierung ergibt, dass der bestätigte Plan oder ein zugrunde liegendes PRD nicht mehr korrekt ist:

- Setze den betroffenen Task auf `needs_human`, wenn die Abweichung eine fachliche oder architektonische Entscheidung erfordert.
- Führe keine stille Korrektur im Produktivcode durch.
- Erkläre konkret, welche Plan- oder PRD-Stelle nicht mehr tragfähig ist.
- Wenn das PRD betroffen ist, fordere den Nutzer auf, zuerst `/update-prd [PRD-Pfad]` auszuführen.
- Wenn der Feature-Plan betroffen ist, fordere den Nutzer auf, danach oder direkt `/update-feature-plan [Plan-Pfad]` auszuführen.
- Fahre erst mit `/execute [neuer Plan-Pfad]` fort, wenn die neue Plan-Version fachlich und technisch bestätigt sowie committed wurde.

## Dokumentation nach Umsetzung

Am Ende der Umsetzung soll nach vollständiger Validierung der Dokumentations-Skill aufgerufen werden:

```text
/document docs/project/features/[feature-name]/plan-vNNN.md
```

Der Skill erstellt `user-guide.md` und `developer-notes.md`. Danach soll der Nutzer prüfen, ob `/reflect-rules` in derselben Session sinnvoll ist, bevor der finaler Commit erstellt wird.

## Abschluss

Wenn alle Tasks `done` sind:

- Root-`TASKS.md` auf Status `done` für dieses Feature aktualisieren.
- Zusammenfassung aller abgeschlossenen Tasks ausgeben.
- Dateien mit Änderungen auflisten.
- Validierungsergebnisse zusammenfassen.
- Manuelle Test-Anleitung geben.
- Auf `/document` als nächsten Workflow hinweisen.

## Unerwartete Issues und Planabweichungen

- Dokumentiere Issues, die nicht im Plan vorgesehen waren.
- Begründe jede notwendige Abweichung vom Plan.
- Führe keine nicht genehmigten fachlichen Scope-Änderungen durch.
- Halte bestehende Funktionalität regressionsfrei.
e nicht genehmigten fachlichen Scope-Änderungen durch.
- Halte bestehende Funktionalität regressionsfrei; wenn ein Restrisiko bleibt, dokumentiere es im Abschlussbericht.
