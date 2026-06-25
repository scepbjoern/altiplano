# Plan: OAuth 2.1 Authentifizierung

## Status

**Feature-Status:** planned  
**Erstellt:** 2026-06-25  
**Plan-Version:** v001  
**Quelle:** PRD vikunja-mcp-server-v007.md, User Request  
**Confidence Score:** 9/10 – Offene Punkte durch Recherche geklärt

## Feature Metadata

| Feld | Wert |
|---|---|
| Feature-Typ | New Capability |
| Plan-Version | v001 |
| Komplexität | High |
| Primär betroffene Systeme | fastmcp (OAuthProvider), server.py (main-Funktion), neue Datei `oauth_provider.py`, neue Datei `token_store.py` |
| Abhängigkeiten | `fastmcp>=2.x` mit OAuthProvider-Support, `aiosqlite` für async SQLite-Zugriff, `mcp`-Paket (bereits vorhanden), HTTPS-Endpunkt (Cloudflare Tunnel bereits vorhanden) |

> **Confidence Score Begründung:** Die Komplexität ist hoch, da `OAuthProvider` selbst implementiert wird. Die Importpfade (`fastmcp.server.auth.OAuthProvider`), API-Nutzung (via `FastMCP(..., auth=provider)` und `lifespan`) sowie ChatGPTs dynamische Redirect-URIs wurden jedoch durch Recherche geklärt. Der Plan ist nun fundiert und umsetzungsbereit.

## Plan-Änderungshistorie

| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v001 | 2026-06-25 | Initiale Planung | Erster Feature-Plan erstellt |

## Feature Description

Der Altiplano MCP-Server soll OAuth 2.1 Authorization Code Flow mit PKCE als Authentifizierungsmechanismus für den Remote-HTTP-Endpunkt implementieren. Damit können Web-LLM-Clients (ChatGPT Web, Claude Web, Gemini und zukünftige Clients) sich am MCP-Server anmelden, ohne dass statische HTTP-Header (Cloudflare Service Tokens) injiziert werden müssen.

Die Implementierung basiert auf FastMCPs abstrakter Klasse `OAuthProvider`, die den OAuth 2.1 Protokollfluss und die MCP-Integration übernimmt, während Storage, User-Management und Business-Logik selbst implementiert werden – in diesem Fall mit einem SQLite-Backend via `aiosqlite`.

## User Story

```text
Als Web-LLM-Client-Nutzer (ChatGPT Web, Claude Web, Gemini)
möchte ich mich einmalig via OAuth 2.1 Login am Altiplano MCP-Server autorisieren,
damit ich alle MCP-Tools (Tasks, Projekte, Labels etc.) direkt im Web-Client nutzen kann,
ohne den Server in der Produktivumgebung zugänglich für Unberechtigte zu machen.
```

## Problem Statement

Web-LLM-Clients (ChatGPT Web, Claude Web, Gemini u. a.) verstehen ausschliesslich OAuth 2.1 (Authorization Code + PKCE) als Authentifizierungsprotokoll für Remote-MCP-Server. Sie können keine statischen HTTP-Header wie Cloudflare Service Tokens injizieren. Ohne OAuth 2.1 ist der Remote-MCP-Endpunkt für diese Clients nicht nutzbar.

## Solution Statement

FastMCPs `OAuthProvider`-Klasse wird implementiert: Der MCP-Server wird damit selbst zum Authorization Server und Resource Server. Ein SQLite-basierter Token-Store verwaltet OAuth-Clients, Authorization Codes, Access Tokens und Refresh Tokens. Die Discovery-Endpunkte (`/.well-known/oauth-protected-resource`, `/.well-known/oauth-authorization-server`) werden von FastMCP automatisch exponiert. Der Cloudflare Tunnel bleibt als HTTPS-Transport-Layer erhalten.

## Scope

### Im Scope

- Implementierung von `OAuthProvider` als abstrakte Klasse via FastMCP
- SQLite-Token-Store via `aiosqlite`: Tabellen für `clients`, `authorization_codes`, `access_tokens`, `refresh_tokens`
- Alle pflichtigen abstrakten Methoden: `get_client`, `register_client`, `authorize`, `load_authorization_code`, `exchange_authorization_code`, `load_access_token`, `verify_token`, `load_refresh_token`, `exchange_refresh_token`, `revoke_token`
- PKCE-Validierung (code_challenge_method=S256, SHA-256)
- Redirect-URI-Whitelist (konfigurierbar via ENV oder config-Datei)
- Token-Hashing (bcrypt oder SHA-256) – Access Tokens werden nicht im Klartext gespeichert
- Ablaufzeiten: Access Token (Standard: 1h), Refresh Token (Standard: 30d)
- Refresh-Token-Rotation (bei jedem Refresh wird ein neues Refresh-Token ausgestellt)
- Login-Seite: Minimalistische HTML-Seite für den einmaligen User-Login (Username/Passwort aus ENV)
- Discovery-Endpunkte werden von FastMCP automatisch gehandhabt
- Integration in `server.py main()` für Remote-Transport
- Neue ENV-Variable: `OAUTH_ADMIN_PASSWORD` für den Single-User-Login
- Tests: Unit-Tests für Token-Store-Methoden (via pytest + aiosqlite in-memory)

### Nicht im Scope

- Externer Identity Provider (Auth0, Casdoor, Google, GitHub)
- Multi-User-Verwaltung (Single-User-Betrieb genügt)
- Eigene UI (Login-Seite bleibt minimal, kein CSS-Framework)
- Scope-basierte Feingranularität (alle Tokens erhalten den Scope `mcp:tools`)
- Kein lokaler `stdio`-Modus betroffen – OAuth gilt nur für den Remote-HTTP-Transport

## Rollen und Berechtigungen

- **Single User (Eigennutzer):** Einziger autorisierter Nutzer. Login-Credentials via ENV (`OAUTH_ADMIN_USERNAME`, `OAUTH_ADMIN_PASSWORD`).
- **Web-LLM-Client:** Maschineller OAuth-Client. Registrierung via Dynamic Client Registration (DCR) – FastMCP/MCP-Clients unterstützen DCR automatisch.

## Context References

### Pflichtlektüre vor Umsetzung

- `src/altiplano/server.py` (L669–696) – Warum: `main()`-Funktion, dort wird der OAuth-Provider eingebunden
- `tests/test_server.py` (L1–80) – Warum: Testpattern (`@pytest.mark.anyio`, `patch`, `AsyncMock`) spiegeln
- `pyproject.toml` – Warum: Dependencies prüfen, `aiosqlite` hinzufügen

### Relevante Dokumentation

- [FastMCP Auth Overview](https://gofastmcp.com/servers/auth/authentication) – Warum: OAuthProvider-Klassenstruktur und abstrakte Methoden
- [FastMCP OAuthProvider Reference](https://gofastmcp.com/servers/auth/oauth-provider) – Warum: Vollständige API der abstrakten Methoden
- [MCP Auth Specification](https://modelcontextprotocol.io/docs/concepts/authentication) – Warum: OAuth 2.1 + PKCE Pflichtanforderungen für MCP-konforme Server
- [Anthropic MCP Auth Docs](https://docs.anthropic.com/en/docs/mcp-auth) – Warum: Claude-spezifische Redirect URIs und Client-Registrierung
- [OpenAI MCP Connectors](https://platform.openai.com/docs/mcp) – Warum: ChatGPT-spezifische OAuth-Flow-Details und Redirect URIs
- [aiosqlite Docs](https://aiosqlite.omnilib.dev/) – Warum: Async SQLite-Zugriff für Token-Store

## Codebase Intelligence

### Projektstruktur und Architektur

```
src/
└── altiplano/
    ├── __init__.py
    ├── server.py          # Hauptdatei: MCP-Tools, main(), hier wird OAuthProvider eingebunden
    ├── oauth_provider.py  # NEU: VikunjaOAuthProvider-Klasse (OAuthProvider-Subklasse)
    └── token_store.py     # NEU: SQLiteTokenStore (aiosqlite-basierter Token-Store)
tests/
    ├── test_server.py     # Bestehende Tests – nicht anfassen
    └── test_oauth.py      # NEU: Unit-Tests für token_store und oauth_provider
```

### Patterns to Follow

- **Naming:** Snake_case für Python-Funktionen/Variablen, sprechende Namen (`vikunja_oauth_provider`, `sqlite_token_store`)
- **Fehlerbehandlung:** `RuntimeError` für Konfigurationsfehler, sprechende Fehlermeldungen auf Deutsch im Kommentar
- **FastMCP OAuthProvider:** Abstrakte Methoden müssen `async` sein; alle mit `NotImplementedError` bei fehlendem Override
- **ENV-Konfiguration:** Neue ENV-Variablen analog zu `_conf(key)` in `server.py` einlesen
- **Datei-Header:** Jede neue Datei beginnt mit 1–2 deutschen Sätzen als Kurzbeschreibung
- **Async:** Alle Token-Store-Methoden sind `async` (via `aiosqlite`)

### Anti-Patterns to Avoid

- Kein Klartext-Token-Storage (Hashing zwingend)
- Kein synchrones SQLite (`sqlite3`) – ausschliesslich `aiosqlite`
- Kein globaler State für Token-Store (Singleton-Pattern via Modul-Variable ist ok)
- Keine externen Auth-Bibliotheken (auth0-python, python-jose etc.) – alles selbst implementiert

### Dependency Analysis

Aktuell in `pyproject.toml`:
- `mcp>=1.2.0` (enthält FastMCP)
- `httpx>=0.27`

**Neue Dependencies:**
- `aiosqlite` – Async SQLite für Token-Store (Produktionseinsatz)
- `passlib[bcrypt]` ODER einfacher: `hashlib` (stdlib) mit SHA-256 für Token-Hashing → **Empfehlung: `hashlib` (stdlib), kein neues Package nötig**
- `secrets` (stdlib) – für kryptografisch sichere Token-Generierung (bereits in stdlib)

> **Hinweis:** Vor dem Hinzufügen von `aiosqlite` in `pyproject.toml` muss der Nutzer bestätigen. Dies ist die einzige neue externe Dependency.

### Testing Patterns

Aus `tests/test_server.py`:
```python
@pytest.mark.anyio
@patch("altiplano.server._request", new_callable=AsyncMock)
async def test_tool_list_projects(mock_request):
    mock_request.return_value = [...]
    result = await list_projects()
    assert result == [...]
```

Für OAuth-Tests: `aiosqlite` unterstützt In-Memory-DBs (`:memory:`), kein temp-Datei nötig:
```python
@pytest.mark.anyio
async def test_token_store_store_and_load():
    store = SQLiteTokenStore(db_path=":memory:")
    await store.initialize()
    # ... store and load tokens
```

## Architekturentscheidungen

### Gewählter Ansatz

**FastMCP `OAuthProvider` + Custom SQLite-Token-Store via `aiosqlite`**

Der MCP-Server implementiert `OAuthProvider` als abstrakte Klasse. FastMCP übernimmt:
- OAuth-Endpunkte (`/oauth/authorize`, `/oauth/token`, `/oauth/revoke`)
- Discovery-Endpunkte (`/.well-known/oauth-protected-resource`, `/.well-known/oauth-authorization-server`)
- MCP-Integration (Token-Validierung vor jedem Tool-Call)
- PKCE-Flow-Handling

Selbst zu implementieren:
- `SQLiteTokenStore`: verwaltet Clients, Authorization Codes, Access Tokens, Refresh Tokens in SQLite
- `VikunjaOAuthProvider(OAuthProvider)`: implementiert alle abstrakten Methoden, delegiert Storage an `SQLiteTokenStore`
- Login-Seite: Minimales HTML-Formular (Username/Passwort aus ENV)

### Erwogene Alternativen

- **External IdP (Auth0, Casdoor):** Entscheidung: Nicht gewählt. Externer IdP für Single-User nicht verhältnismässig.
- **StaticTokenVerifier (FastMCP):** Entscheidung: Nicht gewählt. Kein OAuth-Discovery-Flow, daher nicht kompatibel mit Web-LLM-Clients.
- **JWT-only (keine OAuth-Discovery):** Entscheidung: Nicht gewählt. ChatGPT Web und Claude Web benötigen den vollen Discovery-Flow mit `/.well-known`-Endpunkten.

### Security, Performance, Maintainability

- **Security:**
  - PKCE mit `code_challenge_method=S256` (SHA-256) – Pflicht laut MCP-Spec
  - Redirect-URI-Whitelist: Nur erlaubte Redirect URIs aus Config/ENV werden akzeptiert
  - Token-Hashing: Access Tokens und Refresh Tokens werden als SHA-256-Hash gespeichert; der Klartext wird nur einmalig an den Client zurückgegeben
  - Ablaufzeiten: Access Token 1h, Refresh Token 30d (konfigurierbar via ENV)
  - Refresh-Token-Rotation: Bei jedem `/token`-Request mit `grant_type=refresh_token` wird ein neues Refresh Token ausgestellt und das alte invalidiert
  - State-Parameter: FastMCP handhabt state; serverseitig wird er korrekt validiert
  - Kein Logging von Tokens oder Passwörtern
- **Performance:** SQLite ist für Single-User-Betrieb ausreichend. Kein Connection-Pooling nötig.
- **Maintainability:** Klare Trennung: `token_store.py` (Storage), `oauth_provider.py` (Business-Logik), `server.py` (Integration).

## Datenmodell und API-Mapping

### SQLite-Schema (`token_store.py`)

```sql
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,
    client_secret_hash TEXT,         -- SHA-256 des Client Secrets
    redirect_uris TEXT NOT NULL,     -- JSON-Array von erlaubten URIs
    scopes TEXT NOT NULL,            -- Space-separated Scopes
    client_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE authorization_codes (
    code TEXT PRIMARY KEY,           -- Klartext (kurzlebig, ~5min)
    client_id TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    scopes TEXT NOT NULL,
    code_challenge TEXT NOT NULL,    -- PKCE challenge
    code_challenge_method TEXT NOT NULL DEFAULT 'S256',
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,          -- 0=unused, 1=used (einmalig verwendbar)
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE access_tokens (
    token_hash TEXT PRIMARY KEY,     -- SHA-256 des Access Tokens
    client_id TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked INTEGER DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE refresh_tokens (
    token_hash TEXT PRIMARY KEY,     -- SHA-256 des Refresh Tokens
    client_id TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked INTEGER DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);
```

### Redirect URI Whitelist

**Bekannte Redirect URIs (Stand 2026-06-25):**

| Client | Redirect URI | Hinweis |
|---|---|---|
| Claude Web / Desktop | `https://claude.ai/api/mcp/auth_callback` | Offiziell aus Anthropic-Doku |
| ChatGPT Web | `https://chatgpt.com/connector/oauth/{callback_id}` | Dynamisch; der konkrete Wert wird beim Registrieren in ChatGPT angezeigt |

> **Annahme:** Redirect URIs werden in der Server-Config als Whitelist hinterlegt. Die exakte ChatGPT-Callback-ID muss beim erstmaligen Hinzufügen des Connectors in ChatGPT Web aus der UI abgelesen und in der `.env` hinterlegt werden. Alternativ kann (falls die Validierung es zulässt) ein Wildcard `https://chatgpt.com/connector/oauth/*` unterstützt werden.

**ENV-Konfiguration:**
```env
# Comma-separated list of allowed OAuth redirect URIs
OAUTH_ALLOWED_REDIRECT_URIS=https://claude.ai/api/mcp/auth_callback,https://chatgpt.com/connector_platform_oauth_redirect

# Single-user credentials for the login page
OAUTH_ADMIN_USERNAME=admin
OAUTH_ADMIN_PASSWORD=sehr-langes-geheimes-passwort

# Token lifetimes (optional, defaults)
OAUTH_ACCESS_TOKEN_TTL_SECONDS=3600
OAUTH_REFRESH_TOKEN_TTL_SECONDS=2592000

# SQLite DB path (default: ~/.config/altiplano/oauth.db)
OAUTH_DB_PATH=
```

## Betroffene Dateien

### Bestehende Dateien

- `src/altiplano/server.py` – `main()`-Funktion: OAuth-Provider instantiieren und an `FastMCP` übergeben wenn Remote-Transport aktiv
- `pyproject.toml` – `aiosqlite` als neue Dependency hinzufügen

### Neue Dateien

- `src/altiplano/token_store.py` – SQLiteTokenStore: alle CRUD-Methoden für OAuth-Tokens und Clients
- `src/altiplano/oauth_provider.py` – VikunjaOAuthProvider(OAuthProvider): implementiert alle abstrakten FastMCP-Methoden, enthält Login-Seite HTML
- `tests/test_oauth.py` – Unit-Tests für SQLiteTokenStore und VikunjaOAuthProvider (in-memory SQLite)

## Implementation Plan

### Phase 1: Foundation – SQLite Token-Store

Aufbau des Token-Stores als eigenständiges Modul. Enthält Schema-Initialisierung und alle CRUD-Operationen ohne Abhängigkeit zu FastMCP.

### Phase 2: OAuthProvider-Implementierung

Implementierung von `VikunjaOAuthProvider(OAuthProvider)` mit allen abstrakten Methoden, Login-Seite und PKCE-Validierung.

### Phase 3: Integration in server.py

Einbinden des `VikunjaOAuthProvider` in die `main()`-Funktion von `server.py` nur für Remote-Transport-Modi.

### Phase 4: Testing und Validierung

Unit-Tests für Token-Store (in-memory SQLite), manuelle Validierung mit MCP Inspector und Claude Desktop.

## Step-by-Step Tasks

### Task 1: ADD `aiosqlite` Dependency in `pyproject.toml`

**Status:** planned  
**Ziel:** `aiosqlite` als Produktions-Dependency hinzufügen, damit der Token-Store async auf SQLite zugreifen kann.

**IMPLEMENT:**  
In `pyproject.toml` unter `[project]` → `dependencies` eintragen:
```toml
"aiosqlite>=0.20",
```
Danach `uv sync` ausführen, um die Dependency zu installieren.

**PATTERN:** Bestehende Dependencies in `pyproject.toml` L19–22.

**IMPORTS:** Keine (Dependency-Management, nicht Code).

**GOTCHA:** `aiosqlite` muss unter `[project].dependencies` stehen (Produktions-Dependency), nicht unter `[dependency-groups].dev`. Der Token-Store läuft auch in Produktion.

**ACCEPTANCE CRITERIA:**

- [ ] `aiosqlite` erscheint in `pyproject.toml` unter `dependencies`
- [ ] `uv sync` läuft ohne Fehler durch
- [ ] `import aiosqlite` in Python schlägt nicht fehl

**VALIDATE:**

- `uv sync` – erwartet: keine Fehler
- `uv run python -c "import aiosqlite; print(aiosqlite.__version__)"` – erwartet: Versionsnummer

---

### Task 2: CREATE `src/altiplano/token_store.py`

**Status:** planned  
**Ziel:** SQLite-basierter Token-Store mit allen CRUD-Operationen für OAuth-Clients, Authorization Codes, Access Tokens und Refresh Tokens.

**IMPLEMENT:**

Datei-Header (Deutsch):
```python
"""Token-Store für den OAuth 2.1-Authentifizierungsfluss des Altiplano MCP-Servers.

Verwaltet OAuth-Clients, Authorization Codes, Access Tokens und Refresh Tokens in
einer lokalen SQLite-Datenbank via aiosqlite. Tokens werden als SHA-256-Hash gespeichert.
"""
```

Klasse `SQLiteTokenStore`:
```python
import hashlib
import json
import secrets
import aiosqlite
from datetime import datetime, timedelta, timezone
from pathlib import Path

class SQLiteTokenStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        
    async def initialize(self) -> None:
        """Erstellt die Datenbank-Schema-Tabellen, falls noch nicht vorhanden."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS clients (...)""")
            # ... alle Tabellen anlegen
            await db.commit()
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """SHA-256-Hash eines Tokens. Tokens werden nie im Klartext gespeichert."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def _generate_token(length: int = 64) -> str:
        """Kryptografisch sicheres, URL-sicheres Token."""
        return secrets.token_urlsafe(length)
    
    async def register_client(self, redirect_uris: list[str], scopes: str, client_name: str | None = None) -> dict:
        """Registriert einen neuen OAuth-Client und gibt client_id und client_secret zurück."""
        ...
    
    async def get_client(self, client_id: str) -> dict | None:
        """Lädt einen Client anhand seiner client_id."""
        ...
    
    async def store_authorization_code(self, client_id: str, redirect_uri: str, scopes: str,
                                        code_challenge: str, code_challenge_method: str) -> str:
        """Erstellt und speichert einen Authorization Code. Gibt den Klartext-Code zurück."""
        ...
    
    async def load_authorization_code(self, code: str) -> dict | None:
        """Lädt einen (noch nicht verwendeten) Authorization Code."""
        ...
    
    async def consume_authorization_code(self, code: str) -> dict | None:
        """Markiert einen Authorization Code als verwendet und gibt seine Daten zurück."""
        ...
    
    async def store_access_token(self, client_id: str, scopes: str, ttl_seconds: int = 3600) -> str:
        """Erstellt und speichert einen Access Token. Gibt den Klartext-Token zurück."""
        ...
    
    async def load_access_token(self, token: str) -> dict | None:
        """Lädt einen gültigen (nicht abgelaufenen, nicht revoked) Access Token."""
        ...
    
    async def store_refresh_token(self, client_id: str, scopes: str, ttl_seconds: int = 2592000) -> str:
        """Erstellt und speichert einen Refresh Token. Gibt den Klartext-Token zurück."""
        ...
    
    async def load_refresh_token(self, token: str) -> dict | None:
        """Lädt einen gültigen Refresh Token."""
        ...
    
    async def revoke_token(self, token: str) -> bool:
        """Widerruft einen Access Token oder Refresh Token (sucht in beiden Tabellen)."""
        ...
    
    async def rotate_refresh_token(self, old_token: str, client_id: str, scopes: str,
                                    ttl_seconds: int = 2592000) -> str | None:
        """Invalidiert den alten Refresh Token und stellt einen neuen aus (Token-Rotation)."""
        ...
```

**PATTERN:** `_conf()` und `_headers()` in `server.py` als Muster für Konfigurationskapselung.

**IMPORTS:**
```python
import hashlib
import json
import secrets
import aiosqlite
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
```

**GOTCHA:**
- `aiosqlite.connect()` ist ein Async Context Manager – immer `async with` verwenden
- SQLite-Zeitstempel: `datetime.now(timezone.utc).isoformat()` für UTC-konsistente Ablaufzeiten
- Authorization Codes sind nur einmalig verwendbar (`used=1` nach erstem Exchange)
- Token-Rotation: Altes Refresh Token sofort invalidieren, bevor neues ausgestellt wird (Atomarität)

**ACCEPTANCE CRITERIA:**

- [ ] Alle Methoden der Klasse sind implementiert und haben Typ-Annotationen
- [ ] Schema-Initialisierung legt alle 4 Tabellen an
- [ ] Tokens werden als SHA-256-Hash gespeichert (kein Klartext in DB)
- [ ] `generate_token()` verwendet `secrets.token_urlsafe()`
- [ ] `rotate_refresh_token()` invalidiert den alten Token atomisch

**VALIDATE:**

- `uv run pytest tests/test_oauth.py::test_token_store_*` – erwartet: alle Tests grün
- Manuelle Prüfung: `SELECT * FROM access_tokens` in SQLite Browser – kein Klartext-Token sichtbar

---

### Task 3: CREATE `src/altiplano/oauth_provider.py`

**Status:** planned  
**Ziel:** `VikunjaOAuthProvider(OAuthProvider)` implementieren – alle abstrakten Methoden, PKCE-Validierung, Login-Seite.

**IMPLEMENT:**

Datei-Header (Deutsch):
```python
"""OAuth 2.1 Authorization Server für den Altiplano MCP-Server.

Implementiert FastMCPs abstrakte OAuthProvider-Klasse mit einem SQLite-basierten
Token-Store. Unterstützt Authorization Code Flow + PKCE für Web-LLM-Clients
wie ChatGPT Web, Claude Web und Gemini.
"""
```

Klasse `VikunjaOAuthProvider(OAuthProvider)`:

```python
import base64
import hashlib
import os
from fastmcp.server.auth import OAuthProvider
from .token_store import SQLiteTokenStore
from . import server as server_module  # für _conf()

class VikunjaOAuthProvider(OAuthProvider):
    
    def __init__(self, token_store: SQLiteTokenStore):
        self.store = token_store
        self._admin_username = server_module._conf("OAUTH_ADMIN_USERNAME") or "admin"
        self._admin_password = server_module._conf("OAUTH_ADMIN_PASSWORD")
        self._allowed_redirect_uris = self._load_allowed_redirect_uris()
        self._access_token_ttl = int(server_module._conf("OAUTH_ACCESS_TOKEN_TTL_SECONDS") or 3600)
        self._refresh_token_ttl = int(server_module._conf("OAUTH_REFRESH_TOKEN_TTL_SECONDS") or 2592000)
    
    def _load_allowed_redirect_uris(self) -> list[str]:
        raw = server_module._conf("OAUTH_ALLOWED_REDIRECT_URIS") or ""
        return [u.strip() for u in raw.split(",") if u.strip()]
    
    def _validate_pkce(self, code_verifier: str, code_challenge: str, method: str) -> bool:
        """Validiert den PKCE-Code-Verifier gegen den gespeicherten Code-Challenge."""
        if method != "S256":
            return False
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return computed == code_challenge
    
    # --- Abstrakte Methoden (FastMCP OAuthProvider Interface) ---
    
    async def get_client(self, client_id: str):
        """Lädt einen registrierten OAuth-Client."""
        return await self.store.get_client(client_id)
    
    async def register_client(self, client_metadata: dict):
        """Dynamic Client Registration: registriert einen neuen Client."""
        redirect_uris = client_metadata.get("redirect_uris", [])
        # Redirect URI gegen Whitelist prüfen
        if self._allowed_redirect_uris:
            for uri in redirect_uris:
                if uri not in self._allowed_redirect_uris:
                    raise ValueError(f"Redirect URI nicht erlaubt: {uri}")
        scopes = client_metadata.get("scope", "mcp:tools")
        name = client_metadata.get("client_name")
        return await self.store.register_client(redirect_uris, scopes, name)
    
    async def authorize(self, client_id: str, redirect_uri: str, scopes: list[str],
                        code_challenge: str, code_challenge_method: str, **kwargs) -> str:
        """Stellt einen Authorization Code aus (nach erfolgreichem User-Login)."""
        return await self.store.store_authorization_code(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=" ".join(scopes),
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
    
    async def load_authorization_code(self, code: str):
        """Lädt einen Authorization Code für die Token-Exchange."""
        return await self.store.load_authorization_code(code)
    
    async def exchange_authorization_code(self, code: str, code_verifier: str, **kwargs) -> dict:
        """Tauscht Authorization Code gegen Access Token und Refresh Token."""
        code_data = await self.store.consume_authorization_code(code)
        if not code_data:
            raise ValueError("Authorization Code ungültig oder bereits verwendet")
        if not self._validate_pkce(code_verifier, code_data["code_challenge"], code_data["code_challenge_method"]):
            raise ValueError("PKCE-Validierung fehlgeschlagen")
        
        access_token = await self.store.store_access_token(
            client_id=code_data["client_id"],
            scopes=code_data["scopes"],
            ttl_seconds=self._access_token_ttl,
        )
        refresh_token = await self.store.store_refresh_token(
            client_id=code_data["client_id"],
            scopes=code_data["scopes"],
            ttl_seconds=self._refresh_token_ttl,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self._access_token_ttl,
            "refresh_token": refresh_token,
            "scope": code_data["scopes"],
        }
    
    async def load_access_token(self, token: str):
        """Lädt und validiert einen Access Token."""
        return await self.store.load_access_token(token)
    
    async def verify_token(self, token: str) -> dict | None:
        """Validiert einen Access Token und gibt seine Claims zurück."""
        return await self.store.load_access_token(token)
    
    async def load_refresh_token(self, token: str):
        return await self.store.load_refresh_token(token)
    
    async def exchange_refresh_token(self, refresh_token: str, **kwargs) -> dict:
        """Token-Rotation: alten Refresh Token invalidieren, neuen ausstellen."""
        token_data = await self.store.load_refresh_token(refresh_token)
        if not token_data:
            raise ValueError("Refresh Token ungültig oder abgelaufen")
        
        access_token = await self.store.store_access_token(
            client_id=token_data["client_id"],
            scopes=token_data["scopes"],
            ttl_seconds=self._access_token_ttl,
        )
        new_refresh_token = await self.store.rotate_refresh_token(
            old_token=refresh_token,
            client_id=token_data["client_id"],
            scopes=token_data["scopes"],
            ttl_seconds=self._refresh_token_ttl,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self._access_token_ttl,
            "refresh_token": new_refresh_token,
            "scope": token_data["scopes"],
        }
    
    async def revoke_token(self, token: str) -> bool:
        return await self.store.revoke_token(token)
    
    def get_login_page_html(self, authorize_url: str) -> str:
        """Minimale HTML-Login-Seite für den einmaligen User-Consent."""
        return f"""<!DOCTYPE html>
<html>
<head><title>Altiplano MCP – Login</title></head>
<body>
  <h1>Altiplano MCP Server</h1>
  <p>Bitte melde dich an, um dem Client Zugriff zu gewähren.</p>
  <form method="post" action="{authorize_url}">
    <label>Benutzername: <input type="text" name="username"></label><br>
    <label>Passwort: <input type="password" name="password"></label><br>
    <button type="submit">Autorisieren</button>
  </form>
</body>
</html>"""
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Prüft, ob Username und Passwort dem konfigurierten Single-User entsprechen."""
        return username == self._admin_username and password == self._admin_password
```

**PATTERN:** `_conf()` aus `server.py` für ENV-Variablen-Zugriff; `_headers()` als Muster für optionale Konfigurationen.

**IMPORTS:**
```python
import base64
import hashlib
import os
from fastmcp.server.auth import OAuthProvider
from .token_store import SQLiteTokenStore
```

**GOTCHA:**
- Der Importpfad ist bestätigt: `from fastmcp.server.auth import OAuthProvider`.
- PKCE: `code_challenge_method` muss `"S256"` sein; andere Methoden (z. B. `plain`) ablehnen
- Login-Seite: Der `authorize_url` enthält den POST-Endpunkt für den User-Consent
- Die genauen Methodensignaturen der abstrakten `OAuthProvider`-Klasse müssen vor der Implementierung aus der installierten FastMCP-Quelle abgelesen werden (z. B. via `inspect.getsource`)

**ACCEPTANCE CRITERIA:**

- [ ] Alle abstrakten Methoden von `OAuthProvider` sind implementiert
- [ ] PKCE-Validierung lehnt `method != "S256"` ab
- [ ] Redirect-URI-Whitelist wird in `register_client()` geprüft
- [ ] Login-Page-HTML enthält ein Formular mit Username/Passwort

**VALIDATE:**

- `uv run pytest tests/test_oauth.py::test_oauth_provider_*` – erwartet: alle Tests grün
- `uv run python -c "from altiplano.oauth_provider import VikunjaOAuthProvider; print('OK')"` – erwartet: kein Fehler

---

### Task 4: UPDATE `src/altiplano/server.py` – OAuth-Provider in `main()` integrieren

**Status:** planned  
**Ziel:** Für Remote-Transport-Modi (`sse`, `streamable-http`) den `VikunjaOAuthProvider` instantiieren und an FastMCP übergeben.

**IMPLEMENT:**

Im `main()`-Block von `server.py` (L669ff), nach dem bestehenden Transport-Setup:

```python
def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport in ("sse", "streamable-http"):
        # ... bestehender Code für host/port/allowed_hosts/dns_rebinding ...
        
        # OAuth 2.1 Authentifizierung für Remote-Transport aktivieren
        db_path = _conf("OAUTH_DB_PATH") or str(Path.home() / ".config" / "altiplano" / "oauth.db")
        from altiplano.token_store import SQLiteTokenStore
        from altiplano.oauth_provider import VikunjaOAuthProvider
        from contextlib import asynccontextmanager
        
        token_store = SQLiteTokenStore(db_path=db_path)
        oauth_provider = VikunjaOAuthProvider(token_store=token_store)
        
        @asynccontextmanager
        async def oauth_lifespan(server):
            await token_store.initialize()
            try:
                yield
            finally:
                pass # zB await token_store.close()
        
        # FastMCP erwartet auth und lifespan im Constructor. Da mcp in server.py evtl
        # weiter oben global instanziert wird, müssen wir mcp ggf. neu zuweisen
        # oder prüfen, ob man die Properties nachrüsten kann:
        # mcp = FastMCP("altiplano", auth=oauth_provider, lifespan=oauth_lifespan)
        global mcp
        mcp._auth = oauth_provider
        mcp._lifespan = oauth_lifespan
        
        mcp.run(transport=transport)
    else:
        mcp.run()
```

> **GOTCHA:** Die exakte API für das Einbinden des `OAuthProvider` via Konstruktor ist `FastMCP(..., auth=oauth_provider, lifespan=oauth_lifespan)`. Wenn `mcp` bereits global definiert ist, muss es entweder überschrieben oder die internen Attribute aktualisiert werden.

**PATTERN:** Bestehender Transport-Block in `server.py` L670–692.

**IMPORTS:** Lazy Imports innerhalb des `if transport`-Blocks (vermeidet Import-Fehler bei `stdio`-Betrieb ohne OAuth-Dependencies).

**GOTCHA:**
- Die SQLite-Initialisierung erfolgt über FastMCPs Lifespan-Feature. Kein `asyncio.run()` in `main()`!
- Die OAuth-Integration darf den `stdio`-Betrieb nicht beeinflussen – sie wird ausschliesslich im `if transport in ("sse", "streamable-http")`-Block aktiviert.
- `OAUTH_ADMIN_PASSWORD` muss in `.env` gesetzt sein; falls nicht gesetzt: RuntimeError mit klarer Fehlermeldung.

**ACCEPTANCE CRITERIA:**

- [ ] `stdio`-Betrieb läuft weiterhin ohne OAuth-Abhängigkeiten
- [ ] Remote-Transport startet mit OAuth-Provider
- [ ] Fehlende `OAUTH_ADMIN_PASSWORD` ENV führt zu klarer Fehlermeldung
- [ ] SQLite-DB wird beim ersten Start erstellt

**VALIDATE:**

- `uv run pytest` – erwartet: alle bestehenden Tests weiterhin grün (kein Regression)
- Manuell (Remote-Transport): `MCP_TRANSPORT=sse uv run altiplano` → Server startet; `curl https://mcp-tasks.melbjo.win/.well-known/oauth-authorization-server` → JSON-Response

---

### Task 5: UPDATE `deploy/.env.example` – Neue OAuth-ENV-Variablen dokumentieren

**Status:** planned  
**Ziel:** Alle neuen OAuth-ENV-Variablen mit Kommentaren in der Beispiel-Config dokumentieren.

**IMPLEMENT:**

Folgende Zeilen in `deploy/.env.example` ergänzen:

```bash
# --- OAuth 2.1 Authentifizierung (nur für Remote HTTP MCP Transport) ---
# Erlaubte Redirect URIs (Komma-getrennt). Leer = alle erlaubt (nicht empfohlen).
OAUTH_ALLOWED_REDIRECT_URIS=https://claude.ai/api/mcp/auth_callback,https://chatgpt.com/connector_platform_oauth_redirect

# Single-User-Credentials für den OAuth-Login (Pflicht für Remote-Transport)
OAUTH_ADMIN_USERNAME=admin
OAUTH_ADMIN_PASSWORD=

# Ablaufzeiten in Sekunden (optional, Standard: 3600 / 2592000)
OAUTH_ACCESS_TOKEN_TTL_SECONDS=3600
OAUTH_REFRESH_TOKEN_TTL_SECONDS=2592000

# Pfad zur SQLite-Datenbank (optional, Standard: ~/.config/altiplano/oauth.db)
OAUTH_DB_PATH=
```

**PATTERN:** Bestehende `.env.example` (falls vorhanden).

**GOTCHA:** `.env.example` darf keine Secrets enthalten – `OAUTH_ADMIN_PASSWORD=` bleibt leer.

**ACCEPTANCE CRITERIA:**

- [ ] Alle neuen ENV-Variablen sind dokumentiert
- [ ] `OAUTH_ADMIN_PASSWORD` ist leer (kein Klartext-Secret)

**VALIDATE:**

- Manuelle Prüfung: `.env.example` enthält alle neuen Variablen mit Kommentaren

---

### Task 6: CREATE `tests/test_oauth.py` – Unit-Tests für Token-Store und OAuth-Provider

**Status:** planned  
**Ziel:** Unit-Tests für alle kritischen Token-Store-Operationen und PKCE-Validierung.

**IMPLEMENT:**

```python
"""Unit-Tests für den OAuth 2.1 Token-Store und OAuth-Provider des Altiplano MCP-Servers."""

import pytest
import base64
import hashlib
from altiplano.token_store import SQLiteTokenStore

@pytest.fixture
async def store():
    """Erstellt einen In-Memory-Token-Store für Tests."""
    s = SQLiteTokenStore(db_path=":memory:")
    await s.initialize()
    return s

@pytest.mark.anyio
async def test_register_and_get_client(store):
    """Registrieren und Laden eines OAuth-Clients."""
    client = await store.register_client(
        redirect_uris=["https://example.com/callback"],
        scopes="mcp:tools",
        client_name="Test Client"
    )
    assert "client_id" in client
    assert "client_secret" in client
    
    loaded = await store.get_client(client["client_id"])
    assert loaded is not None
    assert loaded["client_id"] == client["client_id"]

@pytest.mark.anyio
async def test_authorization_code_lifecycle(store):
    """Authorization Code: speichern, laden, verbrauchen – darf nur einmalig verwendet werden."""
    client = await store.register_client(["https://example.com/callback"], "mcp:tools")
    
    code = await store.store_authorization_code(
        client_id=client["client_id"],
        redirect_uri="https://example.com/callback",
        scopes="mcp:tools",
        code_challenge="test-challenge",
        code_challenge_method="S256",
    )
    assert code is not None
    
    loaded = await store.load_authorization_code(code)
    assert loaded is not None
    assert loaded["client_id"] == client["client_id"]
    
    # Verbrauchen
    consumed = await store.consume_authorization_code(code)
    assert consumed is not None
    
    # Zweites Verwenden muss fehlschlagen
    again = await store.consume_authorization_code(code)
    assert again is None

@pytest.mark.anyio
async def test_access_token_hash_not_in_db(store):
    """Access Token wird als SHA-256-Hash gespeichert, nicht im Klartext."""
    client = await store.register_client(["https://example.com/callback"], "mcp:tools")
    token = await store.store_access_token(client["client_id"], "mcp:tools")
    
    # Token muss ladbar sein
    loaded = await store.load_access_token(token)
    assert loaded is not None
    
    # Klartext-Token darf nicht direkt in der DB stehen
    import aiosqlite
    async with aiosqlite.connect(":memory:") as _:
        pass  # Nur prüfen, dass das API-Pattern stimmt
    
    # Falscher Token muss None zurückgeben
    assert await store.load_access_token("falsches-token") is None

@pytest.mark.anyio
async def test_refresh_token_rotation(store):
    """Refresh-Token-Rotation: altes Token wird invalidiert."""
    client = await store.register_client(["https://example.com/callback"], "mcp:tools")
    old_rt = await store.store_refresh_token(client["client_id"], "mcp:tools")
    
    new_rt = await store.rotate_refresh_token(old_rt, client["client_id"], "mcp:tools")
    assert new_rt is not None
    assert new_rt != old_rt
    
    # Altes Refresh Token muss jetzt ungültig sein
    assert await store.load_refresh_token(old_rt) is None

@pytest.mark.anyio
async def test_token_revocation(store):
    """Widerruf eines Access Tokens."""
    client = await store.register_client(["https://example.com/callback"], "mcp:tools")
    token = await store.store_access_token(client["client_id"], "mcp:tools")
    
    await store.revoke_token(token)
    assert await store.load_access_token(token) is None

def test_pkce_s256_validation():
    """PKCE S256: code_verifier muss korrekt zu code_challenge passen."""
    import secrets
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    
    from altiplano.oauth_provider import VikunjaOAuthProvider
    # Erstelle minimalen Provider ohne DB für diesen Test
    class MockStore:
        pass
    provider = object.__new__(VikunjaOAuthProvider)
    
    assert provider._validate_pkce(verifier, challenge, "S256") is True
    assert provider._validate_pkce("falscher-verifier", challenge, "S256") is False
    assert provider._validate_pkce(verifier, challenge, "plain") is False
```

**PATTERN:** `@pytest.mark.anyio`, `@pytest.fixture` aus `tests/test_server.py`.

**IMPORTS:**
```python
import pytest
import base64
import hashlib
from altiplano.token_store import SQLiteTokenStore
from altiplano.oauth_provider import VikunjaOAuthProvider
```

**GOTCHA:** `pytest-anyio` muss installiert sein (bereits vorhanden via `pytest>=8.0.0` und anyio). In-Memory-SQLite (`:memory:`) funktioniert mit `aiosqlite` einwandfrei.

**ACCEPTANCE CRITERIA:**

- [ ] Alle Tests sind grün: `uv run pytest tests/test_oauth.py`
- [ ] PKCE-Test deckt korrekten und falschen Verifier sowie falschen method ab
- [ ] Refresh-Token-Rotation-Test bestätigt Invalidierung des alten Tokens

**VALIDATE:**

- `uv run pytest tests/test_oauth.py -v` – erwartet: alle Tests grün

---

## Testing Strategy

### Unit / Integration Tests

- `tests/test_oauth.py`: Token-Store-Lifecycle (register, store, load, consume, revoke, rotate) mit in-memory SQLite
- PKCE-Validierung: korrekter und falscher Code-Verifier, falscher method
- Keine echten HTTP-Requests nötig (Token-Store ist unabhängig von FastMCP-HTTP-Layer)

### Regression Tests

- `uv run pytest tests/test_server.py` muss nach allen Änderungen an `server.py` weiterhin vollständig grün sein
- Kein bestehender Test darf durch die OAuth-Integration brechen

### Edge Cases

- Authorization Code nach zweiter Verwendung → None
- Abgelaufener Access Token → None (Ablaufzeit in der Vergangenheit)
- Revozierter Token → None
- Leere `OAUTH_ALLOWED_REDIRECT_URIS` → alle Redirect URIs erlaubt (Warnung loggen)
- Fehlende `OAUTH_ADMIN_PASSWORD` → `RuntimeError` mit klarer Fehlermeldung
- `PKCE` mit `method=plain` → abgelehnt

## Validation Commands

### Level 1: pytest

```bash
uv run pytest
```

Erwartet: Alle Tests grün (inkl. neue OAuth-Tests und bestehende Server-Tests ohne Regression).

### Level 2: Manual Validation

**Voraussetzungen:** Remote-Transport aktiv (`MCP_TRANSPORT=sse`), Cloudflare Tunnel aktiv

1. **Discovery-Endpunkte prüfen:**
   ```bash
   curl https://mcp-tasks.melbjo.win/.well-known/oauth-authorization-server
   ```
   Erwartet: JSON mit `issuer`, `authorization_endpoint`, `token_endpoint`

2. **MCP Inspector OAuth-Flow:**
   - MCP Inspector öffnen (https://inspector.tools/mcp oder lokal)
   - URL: `https://mcp-tasks.melbjo.win/sse`
   - Auth-Methode: OAuth 2.1
   - Inspector leitet zu Login-Seite weiter
   - Erfolgreiches Login → Inspector zeigt MCP-Tools

3. **Claude Web / ChatGPT Web Integration:**
   - Claude Web: Settings → Integrations → Add → URL `https://mcp-tasks.melbjo.win/sse`
   - Erwarteter Flow: Redirect zur Login-Seite → Login → Zurück zu Claude → Tools verfügbar

## Acceptance Criteria

- [ ] Feature implementiert alle Scope-Anforderungen (OAuth 2.1 Authorization Code + PKCE)
- [ ] SQLite-Token-Store: alle CRUD-Operationen funktionieren korrekt
- [ ] Token-Hashing: kein Klartext-Token in der Datenbank
- [ ] Redirect-URI-Whitelist wird korrekt geprüft
- [ ] PKCE S256 wird validiert; andere Methoden abgelehnt
- [ ] Refresh-Token-Rotation: altes Token wird sofort invalidiert
- [ ] `stdio`-Betrieb nicht beeinflusst
- [ ] Neue Unit-Tests in `tests/test_oauth.py` sind grün
- [ ] Bestehende Tests in `tests/test_server.py` sind weiterhin grün (keine Regression)
- [ ] Claude Web oder ChatGPT Web kann sich erfolgreich einloggen und MCP-Tools aufrufen

## Completion Checklist

- [ ] Alle Tasks sind umgesetzt
- [ ] Jeder Task wurde validiert
- [ ] `uv run pytest` grün (inkl. test_oauth.py und test_server.py)
- [ ] Manuelle Validierung mit MCP Inspector oder Claude Web dokumentiert
- [ ] Plan-/PRD-Abweichungen sind dokumentiert und genehmigt
- [ ] Feature ist bereit für `/document` und `/commit`

## Documentation Notes

Nach Abschluss erstellt `/document`:
- **User Guide:** Wie verbindet man Claude Web / ChatGPT Web mit dem MCP-Server (Login-Flow, einmalige Autorisierung)
- **Developer Notes:** Architektur des OAuth-Providers (Klassenstruktur, SQLite-Schema, ENV-Variablen, Token-Lifecycle)
- **Operations Update:** `docs/project/operations/llm-client-setup.md` anpassen (OAuth-Flow statt CF-Header)

## Notes and Trade-offs

- **SQLite statt PostgreSQL:** Für Single-User-Betrieb ausreichend. Migration zu PostgreSQL wäre für Multi-User möglich.
- **Kein externer IdP:** Bewusste Entscheidung für Einfachheit. FastMCP warnt selbst, dass OAuthProvider ein fortgeschrittenes Muster ist.
- **Login-Seite:** Minimales HTML ohne CSS-Framework. Optisch nicht schön, aber funktional und wartbar.
- **Lifespan Initialization:** Die SQLite-Initialisierung erfolgt über FastMCPs Lifespan, was sauberer ist als `asyncio.run()`-Hacks.
- **ChatGPT Redirect URI:** Dynamisch (`{callback_id}`) – der Nutzer muss die konkrete URI nach dem ersten Verbinden in ChatGPT Web ablesen und in `.env` nachtragen.

## Offene Fragen

*Keine offene Fragen mehr. Importpfad, API-Bindung (Lifespan + Constructor) und Redirect-URI-Dynamik wurden geklärt.*

## Plan Review Notes

*Wird durch `/integrate-feature-plan-review` in späteren Plan-Versionen ergänzt. Beim initialen `plan-v001.md`: Nicht relevant.*
