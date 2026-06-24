# Plan: Cloudflare Access Support

## Status

**Feature-Status:** done  
**Erstellt:** 2026-06-24  
**Plan-Version:** v001
**Quelle:** User Request und PRD v004  
**Confidence Score:** 10/10 - Standard-Header-Erweiterung für httpx.

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | Enhancement |
| Plan-Version | v001 |
| Komplexität | Low |
| Primär betroffene Systeme | `src/altiplano/server.py`, `tests/test_server.py` |
| Abhängigkeiten | `httpx` |

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-24 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Ermöglicht dem MCP-Server die Authentifizierung gegenüber einer Vikunja-Instanz, die hinter Cloudflare Access (Zero Trust) abgesichert ist. Dazu werden optional die Umgebungsvariablen / Config-Werte `CF_CLIENT_ID` und `CF_CLIENT_SECRET` ausgelesen und als HTTP-Header `CF-Access-Client-Id` und `CF-Access-Client-Secret` an alle API-Anfragen angehängt.

## User Story

```text
Als Administrator
möchte ich den MCP-Server so konfigurieren können, dass er Cloudflare Service Token Header mitsendet,
damit API-Anfragen die Cloudflare Access Barriere passieren können.
```

## Problem Statement

Wenn Vikunja hinter Cloudflare Access läuft, liefert die API bei MCP-Anfragen einen `302 Found` Redirect auf die Cloudflare-Loginseite zurück. Die MCP-Tools stürzen ab oder geben Fehlermeldungen zurück. Der Client kann sich nicht verbinden.

## Solution Statement

Erweiterung der Funktion `_headers()` in `src/altiplano/server.py`, um optional `CF_CLIENT_ID` und `CF_CLIENT_SECRET` über die Hilfsfunktion `_conf()` zu laden und diese als Cloudflare-spezifische Header an das Header-Dictionary anzuhängen.

## Scope

### Im Scope

- Laden von `CF_CLIENT_ID` und `CF_CLIENT_SECRET` aus der Config-Datei oder den Umgebungsvariablen.
- Hinzufügen der Header `CF-Access-Client-Id` und `CF-Access-Client-Secret` zu allen ausgehenden Requests an die Vikunja-API.
- Testabdeckung, die sicherstellt, dass die Header bei Vorhandensein der Variablen gesetzt werden.
- Dokumentation in der `README.md`.

### Nicht im Scope

- Automatischer OAuth-Flow für Cloudflare Access (nur statische Service-Tokens).

## Context References

- `src/altiplano/server.py` - Definition der Authentifizierung in `_headers()`.
- `README.md` - Konfigurations-Dokumentation.

## Codebase Intelligence

- Das Laden von Konfigurationen geschieht über die Funktion `_conf(key: str) -> str | None`, die zuerst `os.environ.get(key)` prüft und dann auf `~/.config/altiplano/env` zurückgreift.
- Die Header werden in `_headers() -> dict[str, str]` zusammengestellt.

## Architekturentscheidungen

### Gewählter Ansatz

Optionales Laden der Variablen `CF_CLIENT_ID` und `CF_CLIENT_SECRET` in `_headers()`.
Wenn diese Werte nicht `None` sind, werden sie unter den Keys `CF-Access-Client-Id` und `CF-Access-Client-Secret` in das Header-Dictionary geschrieben.

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` (Aktion: MODIFY, Header-Erstellung anpassen)
- `tests/test_server.py` (Aktion: MODIFY, Testfälle für die Header ergänzen)
- `README.md` (Aktion: MODIFY, Dokumentation ergänzen)

## Implementation Plan

### Phase 1: Code-Anpassung

- `src/altiplano/server.py` modifizieren, um `CF_CLIENT_ID` and `CF_CLIENT_SECRET` in `_headers()` zu injecten.

### Phase 2: Test-Erweiterung

- `tests/test_server.py` erweitern, um die korrekte Header-Generierung zu prüfen.

### Phase 3: Dokumentation

- `README.md` aktualisieren.

## Step-by-Step Tasks

### Task 1: UPDATE `src/altiplano/server.py`

**Status:** done  
**Ziel:** Cloudflare Header-Support in `_headers()` einbauen.  
**IMPLEMENT:** 
- Lese `cf_id = _conf("CF_CLIENT_ID")` und `cf_secret = _conf("CF_CLIENT_SECRET")` in `_headers()`.
- Wenn gesetzt, füge sie dem Rückgabe-Dictionary hinzu.
**ACCEPTANCE CRITERIA:**
- [x] Header werden optional geladen und mitgesendet.

### Task 2: UPDATE `tests/test_server.py`

**Status:** done  
**Ziel:** Testfall für die Cloudflare-Header hinzufügen.  
**IMPLEMENT:** 
- Schreibe `test_cloudflare_headers()`.
- Mocke `_conf` oder nutze `patch.dict(os.environ, ...)` um `CF_CLIENT_ID` und `CF_CLIENT_SECRET` zu simulieren.
- Überprüfe, ob `_headers()` diese korrekt enthält.
**ACCEPTANCE CRITERIA:**
- [x] Test stellt sicher, dass die Cloudflare-Header hinzugefügt werden, wenn die Konfiguration vorhanden ist.

### Task 3: UPDATE `README.md`

**Status:** done  
**Ziel:** Konfiguration dokumentieren.  
**IMPLEMENT:** 
- Füge Hinweise zu `CF_CLIENT_ID` und `CF_CLIENT_SECRET` im Konfigurationsabschnitt der README.md hinzu.
**ACCEPTANCE CRITERIA:**
- [x] Dokumentation ist verständlich und vollständig.

## Testing Strategy

- Unit-Tests prüfen die `_headers()` Logik mit gesetzten und ungesetzten Umgebungsvariablen.

## Validation Commands

```bash
uv run pytest
```
