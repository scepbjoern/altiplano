# Briefing zur Erstellung eines PRD: Altiplano-Fork für persönliche Vikunja-MCP-Integration

## Zweck dieses Dokuments

Dieses Dokument dient als Start-Briefing für einen frischen Chat-Verlauf in Claude Code, Codex Code oder einem vergleichbaren KI-Coding-Agenten.

Das Ziel ist **nicht**, sofort Code zu schreiben. Das Ziel ist zuerst, gemeinsam ein gutes **Product Requirements Document (PRD)** zu erstellen. Dieses PRD soll danach als Grundlage dienen, um einen Fork von `aichholzer/altiplano` gezielt an meine Bedürfnisse anzupassen.

Der Coding-Agent soll dieses Dokument lesen, das bestehende Repository analysieren und mir danach gezielte Fragen stellen, damit das PRD finalisiert werden kann.

---

## Wichtigste Anweisung an das neue Modell

Bitte beginne **nicht sofort mit der Implementierung**.

Deine erste Aufgabe ist:

1. Analysiere dieses Briefing.
2. Analysiere das Repository `aichholzer/altiplano` beziehungsweise meinen Fork davon.
3. Prüfe, welche Features bereits vorhanden sind.
4. Prüfe, welche Architektur das Projekt aktuell nutzt.
5. Erstelle danach **eine strukturierte Liste von Fragen**, die ich beantworten muss, bevor ein belastbares PRD erstellt werden kann.
6. Warte auf meine Antworten.
7. Erstelle erst danach das finale PRD.

Wenn Informationen fehlen, mache keine stillen Annahmen, sondern stelle Rückfragen. Falls eine Annahme sinnvoll ist, markiere sie ausdrücklich als Annahme.

---

## Ausgangslage

Ich nutze eine selbst gehostete Vikunja-Instanz.

Die aktuelle Vikunja-Instanz läuft auf:

- Vikunja Version: `2.3.0`
- Datenbank: ParadeDB/PostgreSQL
- Suche: ParadeDB/`pg_search`
- URL der Vikunja-Instanz: `https://tasks.melbjo.win/`
- Vikunja-API-Basis-URL voraussichtlich: `https://tasks.melbjo.win/api/v1`

Ich möchte aus KI-Tools heraus auf Vikunja zugreifen können, insbesondere aus:

- Codex Code
- ChatGPT Web
- ChatGPT Mobile
- Claude Code
- Claude Desktop oder Claude Web, sofern technisch sinnvoll möglich

Der Zugriff soll über einen MCP-Server erfolgen.

Als Ausgangspunkt soll das bestehende Repository verwendet werden:

```text
https://github.com/aichholzer/altiplano
```

Ich möchte dieses Repository forken, Python zunächst beibehalten und den Fork Schritt für Schritt anpassen.

---

## Strategische Entscheidung

Es wurde bereits entschieden:

- Kein kompletter Rewrite in Next.js.
- Kein kompletter Rewrite in TypeScript in der ersten Phase.
- Python bleibt zunächst erhalten.
- Der bestehende Altiplano-Code soll zuerst lokal getestet werden.
- Danach sollen nicht benötigte Features entfernt oder deaktiviert werden.
- Danach sollen fehlende Features ergänzt werden.
- Ein späterer Rewrite in TypeScript/Node.js bleibt möglich, ist aber nicht Teil der ersten Phase.

Next.js wird aktuell als Overkill betrachtet, da keine eigene GUI benötigt wird. Eine optionale ChatGPT-App-UI oder ein Widget kann später geprüft werden, ist aber nicht Bestandteil der ersten Umsetzung.

---

## Übergeordnetes Ziel

Ich möchte einen zuverlässigen, sicheren und schlanken MCP-Server für Vikunja haben, mit dem KI-Assistenten Aufgaben verwalten können.

Der MCP-Server soll insbesondere ermöglichen:

- Projekte auflisten
- Aufgaben suchen
- Aufgaben anzeigen
- neue Aufgaben erstellen
- Aufgaben aktualisieren
- Aufgaben in andere Projekte verschieben
- Aufgaben als erledigt markieren
- Kommentare hinzufügen

Der MCP-Server soll nicht unkontrolliert gefährliche Aktionen ausführen.

---

## Sicherheitsprinzipien

Sicherheit ist wichtig, weil der MCP-Server Schreibzugriff auf meine persönliche Aufgabenverwaltung erhält.

Folgende Grundsätze sollen gelten:

1. **Kein Löschen in der ersten Phase**
   - Es soll kein Tool angeboten werden, das Tasks, Projekte, Kommentare oder Labels endgültig löscht.
   - Statt Löschen soll bevorzugt `complete_task` oder eine andere reversible/ungefährlichere Aktion verwendet werden.

2. **Keine Massenänderungen ohne explizite Schutzlogik**
   - Bulk-Operationen sollen entweder gar nicht angeboten werden oder harte Grenzen haben.
   - Beispiel: maximal 5 oder 10 Tasks pro Operation, sofern überhaupt vorgesehen.

3. **Explizite Zielangaben bei Verschiebungen**
   - Ein Task soll nur dann verschoben werden, wenn Zielprojekt oder Zielbereich eindeutig ist.
   - Bei unklaren Projektbezeichnungen soll der Agent nachfragen.

4. **Token bleibt serverseitig**
   - Der Vikunja-API-Token soll nicht an ChatGPT, Claude oder Codex weitergegeben werden.
   - Der Token liegt nur als Umgebungsvariable auf dem MCP-Server.

5. **Minimale Scopes**
   - Der Vikunja-API-Token soll nur die minimal notwendigen Berechtigungen erhalten.
   - Löschen soll, wenn möglich, nicht im Token enthalten sein.

6. **Logging ohne Geheimnisse**
   - Logs dürfen keine API-Tokens oder sensiblen Inhalte unnötig ausgeben.
   - Fehler sollen aber ausreichend nachvollziehbar sein.

7. **Bestätigung bei riskanten Aktionen**
   - Für potenziell riskante Änderungen soll der KI-Client nachfragen.
   - Das kann durch Tool-Beschreibungen, Systemregeln oder separate Confirm-Patterns unterstützt werden.

---

## Ziel-Clients und gewünschte Betriebsmodi

Der MCP-Server soll langfristig möglichst breit nutzbar sein.

### 1. Lokaler stdio-Modus

Für lokale Entwickler-Tools wie:

- Codex Code
- Claude Code lokal

Gewünschtes Prinzip:

```text
Client startet lokalen MCP-Prozess
→ MCP stdio
→ Altiplano-Fork
→ Vikunja REST API
```

### 2. Remote HTTP MCP

Für webbasierte oder mobile Clients wie:

- ChatGPT Web
- ChatGPT Mobile
- Claude Web/Desktop, sofern unterstützt
- eventuell Codex/Claude Code remote

Gewünschtes Prinzip:

```text
Client
→ HTTPS
→ eigener MCP-Endpunkt
→ Altiplano-Fork im Docker-Container
→ Vikunja REST API
```

Ein möglicher späterer Endpunkt könnte sein:

```text
https://mcp-tasks.melbjo.win/sse
```

Der genaue Domainname ist noch offen.

### 3. ChatGPT Apps SDK

Für ChatGPT soll geprüft werden, ob der MCP-Server direkt als ChatGPT-App beziehungsweise Connector nutzbar gemacht werden kann.

Wichtig:

- Zunächst ist keine eigene UI erforderlich.
- Es reicht in der ersten Phase eine tool-only App beziehungsweise ein tool-only MCP-Server.
- Eine UI-Komponente für ChatGPT kann später optional ergänzt werden.

---

## Aktuelles Repository: erwarteter Ausgangspunkt

Das Repository `aichholzer/altiplano` ist nach meinem Verständnis ein Python-MCP-Server für Vikunja.

Bitte analysiere das Repository selbst und verlasse dich nicht nur auf dieses Briefing.

Erwartete vorhandene Bereiche können sein:

- Vikunja-API-Client
- MCP-Tooldefinitionen
- Projekt-Tools
- Task-Tools
- Label-Tools
- Kommentar-Tools
- Assignee-Tools
- Konfiguration über Environment-Variablen oder Config-Datei
- Start über `uvx` oder Python-Paket

Bitte prüfe konkret:

- Welche Tools existieren bereits?
- Welche Tools sind sicher genug?
- Welche Tools sind zu generisch oder riskant?
- Welche Tools fehlen?
- Welche Startmodi werden unterstützt?
- Gibt es bereits HTTP-MCP oder nur stdio?
- Wie werden Secrets konfiguriert?
- Welche Tests existieren?
- Wie ist Packaging/Deployment gelöst?
- Wie gut lässt sich das Projekt dockerisieren?

---

## Vermutete bestehende Tools

Bitte verifiziere dies im Code.

Mögliche bereits vorhandene Tools:

- `list_projects`
- `create_project`
- `list_tasks`
- `get_task`
- `create_task`
- `update_task`
- `set_reminders`
- `list_labels`
- `add_label`
- `remove_label`
- `list_comments`
- `add_comment`
- `search_users`
- `add_assignee`
- `remove_assignee`

Nicht alle davon müssen behalten werden.

---

## Gewünschte Kernfunktionen

Die erste produktiv sinnvolle Version soll möglichst klein und sicher sein.

### Must-have

#### `list_projects`

Zweck:

- Projekte anzeigen
- Projekt-IDs und Namen sichtbar machen
- Grundlage für Task-Erstellung und Task-Verschiebung

Anforderungen:

- Gibt Name, ID und optional Parent/Hierarchie zurück
- Soll nicht zu viele Details ausgeben
- Muss robust mit verschachtelten Projekten umgehen, falls Vikunja diese verwendet

#### `search_tasks`

Zweck:

- Aufgaben über Suchbegriff finden
- Grundlage für Aktualisierung, Verschiebung und Erledigung

Anforderungen:

- Suchbegriff als Pflichtfeld
- Optional Filter auf Projekt, Status, Fälligkeit
- Ausgabe soll Task-ID, Titel, Projekt, Status, Fälligkeit enthalten
- Keine riesigen Resultsets; Limit verwenden

#### `get_task`

Zweck:

- Detailansicht einer Aufgabe

Anforderungen:

- Task-ID als Pflichtfeld
- Rückgabe von Titel, Beschreibung, Status, Projekt, Labels, Assignees, Fälligkeit, Kommentaren optional

#### `create_task`

Zweck:

- Neue Aufgabe erstellen

Anforderungen:

- Projekt-ID oder eindeutiger Projektname
- Titel als Pflichtfeld
- Beschreibung optional
- Fälligkeit optional
- Labels optional
- Assignees optional
- Sichere Defaults

#### `update_task`

Zweck:

- Aufgabe gezielt aktualisieren

Anforderungen:

- Task-ID als Pflichtfeld
- Nur definierte Felder aktualisieren
- Kein unkontrolliertes Überschreiben ganzer Objekte
- Keine Löschoperation
- Änderungszusammenfassung zurückgeben

#### `move_task_to_project`

Zweck:

- Aufgabe in ein anderes Projekt verschieben

Anforderungen:

- Eigenes Tool, nicht nur generisches `update_task`
- Task-ID als Pflichtfeld
- Zielprojekt-ID oder eindeutig auflösbarer Projektname
- Bei Mehrdeutigkeit keine Aktion, sondern Rückfrage
- Rückgabe von altem und neuem Projekt

#### `complete_task`

Zweck:

- Aufgabe als erledigt markieren

Anforderungen:

- Eigenes Tool, nicht nur generisches `update_task`
- Task-ID als Pflichtfeld
- Optional Kommentar
- Keine Löschung

#### `add_comment`

Zweck:

- Kommentar zu Aufgabe hinzufügen

Anforderungen:

- Task-ID als Pflichtfeld
- Kommentartext als Pflichtfeld
- Optional Markierung, dass Kommentar von KI-Unterstützung stammt

---

## Nice-to-have

Diese Features sind optional und sollen erst nach Klärung ins PRD aufgenommen werden:

- `list_labels`
- `add_label_to_task`
- `remove_label_from_task`
- `list_assignees`
- `assign_user_to_task`
- `unassign_user_from_task`
- `set_due_date`
- `set_reminder`
- `list_overdue_tasks`
- `list_tasks_due_today`
- `list_tasks_due_this_week`
- `create_task_from_text`
- `create_multiple_tasks_from_text`
- `summarize_project`
- `weekly_task_review`
- `inbox_capture`
- `natural_language_task_parser`

---

## Konfiguration

Der MCP-Server soll über Umgebungsvariablen konfiguriert werden können.

Voraussichtliche Variablen:

```env
VIKUNJA_URL=https://tasks.melbjo.win/api/v1
VIKUNJA_API_TOKEN=...
MCP_TRANSPORT=stdio
LOG_LEVEL=info
```

Für Remote HTTP später zusätzlich:

```env
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8787
```

Falls sinnvoll:

```env
MCP_REQUIRE_AUTH=true
MCP_AUTH_TOKEN=...
```

Bitte im PRD prüfen, ob ein zusätzlicher Auth-Mechanismus vor dem MCP-Server nötig ist, insbesondere wenn der Server über HTTPS öffentlich erreichbar gemacht wird. -> Eigentlich ist dieser schon klar, da Cloudflare Zero Trust für alle anderen Dienste wie z.B. Vikunja selbst im Einsatz ist.

---

## Deployment-Ziel

Der MCP-Server soll später in meiner Docker-/Reverse-Proxy-Umgebung laufen.

Mögliche Zielstruktur:

```yaml
services:
  vikunja-mcp:
    image: ghcr.io/<mein-github-user>/<repo>:latest
    container_name: vikunja-mcp
    restart: unless-stopped
    environment:
      VIKUNJA_URL: "https://tasks.melbjo.win/api/v1"
      VIKUNJA_API_TOKEN: "${VIKUNJA_API_TOKEN}"
      MCP_TRANSPORT: "http"
      MCP_HOST: "0.0.0.0"
      MCP_PORT: "8787"
    ports:
      - "8787:8787"
```

Der Reverse Proxy würde später HTTPS bereitstellen.

Der genaue Deployment-Weg soll im PRD geklärt werden.

---

## Teststrategie

Das PRD soll eine Teststrategie enthalten.

Gewünscht sind mindestens:

### Lokale Tests

- Server startet
- Konfiguration wird geladen
- Fehlende Konfiguration führt zu verständlicher Fehlermeldung
- Vikunja-Verbindung kann geprüft werden
- Tools sind registriert

### API-/Integrationstests gegen Test-Vikunja oder produktive Instanz mit Testprojekt

- Projekte listen
- Test-Task erstellen
- Test-Task lesen
- Test-Task aktualisieren
- Test-Task verschieben
- Test-Task erledigen
- Kommentar hinzufügen

### Sicherheitstests

- Kein Delete-Tool vorhanden
- Fehlende Pflichtparameter führen nicht zu API-Aufrufen
- Mehrdeutige Projektnamen führen zu Rückfrage/Fehler statt zufälliger Auswahl
- Token wird nicht geloggt
- Fehler enthalten keine Secrets

### Client-Tests

- Codex Code lokal
- Claude Code lokal
- Optional ChatGPT Developer Mode / Connector
- Optional Claude Desktop/Web Remote MCP

---

## Fragen, die vermutlich gestellt werden sollten

### Nutzung

1. Welche konkreten Alltagsszenarien sollen zuerst unterstützt werden?
4. Welche Sprache sollen Tool-Beschreibungen bevorzugt haben: Deutsch, Englisch oder zweisprachig?

### Vikunja-Struktur

5. Welche Projekte gibt es ungefähr in Vikunja?
6. Gibt es ein Inbox-Projekt?
7. Gibt es verschachtelte Projekte?
8. Werden Labels intensiv genutzt?
9. Werden Assignees überhaupt genutzt?
10. Werden Kommentare intensiv genutzt?

### Schreibrechte

11. Darf der Assistent Tasks erstellen?
12. Darf der Assistent Tasks ändern?
13. Darf der Assistent Tasks verschieben?
14. Darf der Assistent Tasks als erledigt markieren?
15. Darf der Assistent Fälligkeiten setzen?
16. Darf der Assistent Labels ändern?
17. Darf der Assistent Assignees ändern?
18. Soll Löschen komplett ausgeschlossen bleiben?

### Sicherheit

19. Soll es eine harte Grenze für Bulk-Aktionen geben?
20. Sollen Schreibaktionen immer bestätigt werden?
21. Gibt es Aktionen, die nur lokal erlaubt sein sollen, aber nicht über Remote-MCP?
22. Soll der MCP-Server eine eigene Authentifizierung vor den Tools haben?
23. Soll es Audit-Logs geben?

### Deployment

24. Soll zunächst nur lokaler stdio-Modus gebaut werden?
25. Soll HTTP-MCP direkt in Phase 1 gebaut werden?
26. Soll Docker in Phase 1 enthalten sein?
27. Welche Domain soll für Remote-MCP verwendet werden?

### ChatGPT / Claude / Codex

30. Soll ChatGPT zuerst nur tool-only genutzt werden?
31. Soll eine ChatGPT-UI später geplant werden?
32. Soll Claude Desktop lokal via stdio oder remote via HTTP genutzt werden?
33. Soll Codex lokal via stdio oder remote via HTTP genutzt werden?
34. Gibt es verschiedene Sicherheitsprofile pro Client?

---