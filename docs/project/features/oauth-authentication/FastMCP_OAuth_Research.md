# Recherche: OAuth 2.1 Integration -- Offene technische Fragen

## Frage 1: FastMCP `OAuthProvider`

### Befund

Der **öffentliche Importpfad** ist:

``` python
from fastmcp.server.auth import OAuthProvider
```

Die Implementierung liegt in `src/fastmcp/server/auth/auth.py`.

Der Constructor von `OAuthProvider` (v2.14.3) lautet sinngemäss:

``` python
class OAuthProvider(...):
    def __init__(
        self,
        *,
        base_url,
        issuer_url=None,
        service_documentation_url=None,
        client_registration_options=None,
        revocation_options=None,
        required_scopes=None,
    ):
        ...
```

Die abstrakten OAuth-Methoden (über `OAuthAuthorizationServerProvider`)
sind:

-   `get_client(...)`
-   `register_client(...)`
-   `authorize(...)`
-   `load_authorization_code(...)`
-   `exchange_authorization_code(...)`
-   `load_refresh_token(...)`
-   `exchange_refresh_token(...)`
-   `load_access_token(...)`
-   `revoke_token(...)`

`verify_token()` wird von FastMCP bereits implementiert und delegiert
intern auf `load_access_token()`.

Die empfohlene Einbindung lautet:

``` python
provider = MyOAuthProvider(...)
mcp = FastMCP("altiplano", auth=provider)
```

Nicht dokumentiert sind:

-   `mcp.run(..., auth=provider)`
-   `mcp.auth = provider`

### Quellen

-   FastMCP Quellcode: `src/fastmcp/server/auth/auth.py`
-   MCP Python SDK: `src/mcp/server/auth/provider.py`
-   https://gofastmcp.com/servers/auth/authentication

### Empfehlung

Eine eigene `AltiplanoOAuthProvider`-Klasse implementieren und über den
Constructor an `FastMCP(..., auth=provider)` übergeben.

------------------------------------------------------------------------

## Frage 2: ChatGPT Web Redirect URI

### Befund

Für neue ChatGPT-Connectoren lautet die Redirect URI:

    https://chatgpt.com/connector/oauth/{callback_id}

Die Callback-ID ist **pro Connector dynamisch**.

Die frühere URI

    https://chatgpt.com/connector_platform_oauth_redirect

ist laut OpenAI nur noch für Legacy-Apps vorgesehen.

OpenAI verwendet:

-   Authorization Code Flow
-   PKCE (S256)
-   RFC8707 `resource` Parameter

### Quellen

-   https://developers.openai.com/apps-sdk/build/auth

### Empfehlung

1.  Connector in ChatGPT anlegen.
2.  Angezeigte Redirect URI übernehmen.
3.  Exakt auf dem OAuth-Server whitelisten.
4.  Alternativ (wenn unterstützt) nur das Muster

```{=html}
<!-- -->
```
    https://chatgpt.com/connector/oauth/*

zulassen.

------------------------------------------------------------------------

## Frage 3: `asyncio.run()` und FastMCP

### Befund

`mcp.run()` startet intern selbst einen Event Loop (über `anyio.run()`).

Ein vorheriges

``` python
asyncio.run(token_store.initialize())
```

führt **nicht automatisch** zu einem "nested event loop"-Fehler, da
beide Aufrufe nacheinander erfolgen.

Allerdings empfiehlt sich dies architektonisch nicht, weil Ressourcen
häufig an den Event Loop gebunden sind.

FastMCP besitzt dafür einen offiziellen **Lifespan-Mechanismus**.

### Quellen

-   FastMCP `server.py`
-   https://gofastmcp.com/servers/lifecycle

### Empfehlung

Den SQLite-Token-Store im Lifespan initialisieren:

``` python
@asynccontextmanager
async def lifespan(server):
    await token_store.initialize()
    try:
        yield
    finally:
        await token_store.close()

mcp = FastMCP(
    "altiplano",
    auth=auth,
    lifespan=lifespan,
)
```

Alternativ vollständig async:

``` python
async def main():
    await token_store.initialize()
    try:
        await mcp.run_async(...)
    finally:
        await token_store.close()

asyncio.run(main())
```

## Gesamtfazit

Für einen produktionsreifen FastMCP-OAuth-Server empfiehlt sich:

-   `from fastmcp.server.auth import OAuthProvider`
-   `FastMCP(..., auth=provider)`
-   eigener OAuthProvider mit SQLite-Token-Store
-   Initialisierung über den Lifespan-Mechanismus
-   dynamische ChatGPT-Redirect-URIs pro Connector whitelisten
-   Authorization Code + PKCE vollständig implementieren.
