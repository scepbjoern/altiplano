# Testing-Guide – Automatisierte Tests für den Altiplano MCP-Server

> **Für wen ist dieses Dokument?**
> Für Studierende, die verstehen möchten, wie der Python-basierte MCP-Server automatisiert getestet wird, wie man Tests ausführt und wie man die Integration mit der Vikunja-API validiert.

---

## Was ist automatisiertes Testen – und warum macht man es?

Beim manuellen Testen verbindet man den MCP-Server mit einem Client (z.B. Claude Desktop oder MCP Inspector) und prüft selbst, ob die Tools funktionieren. Das ist für die Entwicklung unerlässlich, wird aber bei Codeänderungen schnell mühsam, da man alle Tools und API-Anfragen erneut durchspielen müsste.

**Automatisierte Tests** übernehmen diese Arbeit: Sie prüfen eure Logik, stellen sicher, dass die Kommunikation mit der Vikunja-API korrekt aufgebaut wird, und melden Fehler in Sekunden.

### Der PIV-Loop: Warum Tests zum Entwicklungsprozess gehören

In diesem Projekt arbeitet ihr nach dem **PIV-Loop**:

```
Plan  →  Implement  →  Validate  →  Commit
```

- **Plan**: Was soll gebaut werden? Akzeptanzkriterien definieren.
- **Implement**: Code schreiben – gemeinsam mit dem AI Agent.
- **Validate**: **Der AI Agent** führt `uv run pytest` aus, prüft das Ergebnis und behebt Fehler – automatisch. Erst wenn alle Tests grün sind → Committen.

Tests sichern euch ab, bevor Code festgeschrieben wird. Der Agent schreibt bei jedem neuen Feature (z.B. einem neuen MCP-Tool oder API-Filter) automatisch einen passenden Test.

---

## Testing mit pytest

Da es sich bei Altiplano um ein Python-Projekt handelt, verwenden wir **pytest** für Unit- und Integrationstests.

### Was wird getestet?

1. **API-Requests:** Wir testen, ob unsere HTTP-Anfragen (mit `httpx`) die richtigen Header, Parameter und Payloads an Vikunja senden. Dafür mocken wir in der Regel die Vikunja-API, damit die Tests lokal ohne echte Netzwerkverbindung laufen.
2. **Tool-Handler:** Wir prüfen, ob die MCP-Tools (z.B. `list_tasks`, `create_task`) die Argumente korrekt validieren, an die API-Funktionen weitergeben und die API-Antworten in das richtige MCP-Format konvertieren.
3. **Fehlerbehandlung:** Wir stellen sicher, dass Verbindungsfehler, ungültige Tokens oder nicht gefundene Ressourcen (HTTP 404) sauber abgefangen und als verständliche Fehlermeldungen an den Client zurückgegeben werden.

### Tests ausführen

Tests werden im PIV-Loop **automatisch durch den AI Agent** ausgeführt. Falls ihr sie selbst starten möchtet:

```bash
# Alle Tests ausführen
uv run pytest

# Tests mit detaillierter Ausgabe ausführen
uv run pytest -v
```

**Erwartetes Ergebnis:** Eine Ausgabe wie `==== 15 passed in 0.23s ====` – alle Tests grün.

### Wo liegen die Tests?

Die Tests befinden sich im Ordner `tests/` im Wurzelverzeichnis des Projekts:

```
tests/
├── conftest.py          ← Gemeinsame pytest-Fixtures (z.B. MCP-Client-Mock)
├── test_server.py       ← Tests für den MCP-Server und die Tool-Registrierung
└── test_vikunja.py      ← Tests für die API-Kommunikation mit Vikunja
```

---

## Manuelle Validierung (MCP Runtime Testing)

Manche Aspekte, insbesondere wie das LLM mit den Tools interagiert, lassen sich schwer in automatisierten Tests abbilden. Dafür führen wir eine manuelle Validierung durch:

### 1. Testen mit dem MCP Inspector

Der MCP Inspector ist ein offizielles Entwickler-Tool von Anthropic, mit dem ihr euren Server in einer Weboberfläche interaktiv testen könnt.

Anleitung zum Starten des Inspectors findet ihr in [`MCP_LOCAL_SETUP.md`](MCP_LOCAL_SETUP.md).

### 2. Live-Test in Claude Desktop

Durch die Konfiguration des MCP-Servers in Claude Desktop könnt ihr den Server im realen Einsatz testen. Bittet Claude, Aufgaben aufzulisten oder Projekte anzulegen, und prüft, ob die Aktionen im Vikunja-Interface ankommen.

---

## Häufige Probleme

**«Tests schlagen fehl wegen fehlendem API-Token»**
→ Gute Integrationstests mocken die API-Anfragen, damit keine echten Anfragen rausgehen. Wenn Tests trotzdem echte Anfragen machen wollen und fehlschlagen, prüft, ob eure `.env`-Datei korrekt geladen wird (z.B. mittels `python-dotenv`).

**«pytest wird nicht gefunden»**
→ Verwendet immer das Präfix `uv run pytest`. Dadurch wird pytest im Kontext des virtuellen Environments ausgeführt, das von `uv` verwaltet wird. Falls die Abhängigkeiten nicht synchronisiert sind, führt zuerst `uv sync` aus.

