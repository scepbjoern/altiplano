# Developer Notes: Dateianhänge

## Überblick

Das Feature implementiert den Upload, Download, die Auflistung und das Löschen von Dateianhängen an Vikunja-Aufgaben über das Model Context Protocol. Es optimiert den Dateitransfer für Umgebungen, in denen MCP-Server und Client getrennte Dateisysteme nutzen.

## Referenzen

- Plan: `docs/project/features/dateianhaenge/plan-v002.md`
- PRD: `docs/project/prds/vikunja-mcp-server-v006.md`

## Betroffene Dateien

| Datei | Zweck / Änderung |
|---|---|
| `src/altiplano/server.py` | Implementierung der Tools, Import von `base64`, Header-Workaround in `_request` für Multipart-Form-Uploads. |
| `tests/test_server.py` | Registrierungstests, Unittests mit Mocks für API-Anfragen und httpx-Downloads. |
| `TASKS.md` | Feature-Index-Aktualisierung. |

## Architektur und Datenfluss

1. **Header-Bypass in `_request`**:
   Vikunja erwartet Multipart-Uploads als `multipart/form-data` mit einem dynamisch generierten Boundary-Parameter im Header. Da `_headers()` standardmäßig `"Content-Type": "application/json"` setzt, würde das Überschreiben durch HTTPX blockiert. In `_request` wird der `Content-Type`-Header entfernt, wenn `files` in den Keyword-Argumenten enthalten ist. HTTPX setzt daraufhin automatisch den korrekten Multipart-Header inklusive Boundary.
2. **Base64-Upload**:
   Der Base64-String wird mittels `base64.b64decode` dekodiert und als In-Memory-Bytes-Tupel (`(filename, file_bytes)`) an das `files`-Argument von `_request` übergeben.
3. **URL-Download-Upload**:
   Der Server instanziiert einen temporären `httpx.AsyncClient`, um die Datei von einer öffentlichen URL herunterzuladen (unter Beachtung von Redirects), und leitet den Payload als In-Memory-Multipart an Vikunja weiter.

## Datenmodell und API-Mapping

- **list_task_attachments**:
  Mappt `GET /tasks/{task_id}/attachments` auf ein schlankes MCP-Response-Format. Wenn das Feld `file` vorhanden ist (Standard in Vikunja), werden Dateiname und Dateigröße daraus ausgelesen, andernfalls wird auf die Fallbacks `name` und `size` zurückgegriffen.
- **upload_task_attachment_base64 / upload_task_attachment_from_url**:
  Mappt auf `PUT /tasks/{task_id}/attachments` mit einem Multipart-Body: `{"files": (filename, file_bytes)}`.
- **delete_task_attachment**:
  Mappt auf `DELETE /tasks/{task_id}/attachments/{attachment_id}`.
- **get_task_frontend_url**:
  Berechnet den Link durch Abschneiden von `/api/v1` von `VIKUNJA_URL` und Anhängen von `/tasks/{task_id}`.

## Validierung und Tests

| Prüfung | Ergebnis / Hinweis |
|---|---|
| `test_mcp_initialization` | Prüft die erfolgreiche Tool-Registrierung aller 5 neuen MCP-Tools. |
| `test_tool_list_task_attachments` | Mockt `_request` und prüft das korrekte Metadaten-Mapping. |
| `test_tool_delete_task_attachment` | Verifiziert den DELETE-Aufruf für Anhänge. |
| `test_tool_get_task_frontend_url` | Verifiziert die korrekte URL-Berechnung. |
| `test_tool_upload_task_attachment_base64` | Testet erfolgreichen Base64-Upload und die 2 MB-Grenzenvalidierung. |
| `test_tool_upload_task_attachment_from_url` | Mockt `httpx.AsyncClient` für den Download und prüft die Weiterleitung an die Vikunja-API. |

Befehl zum Ausführen der Tests:
```bash
uv run pytest
```

## Betriebs- und Setup-Hinweise

- Für den Download externer Ressourcen muss das Hostsystem, auf dem der MCP-Server läuft, ausgehende HTTP/HTTPS-Verbindungen erlauben.
- Es wurden keine neuen Konfigurationsvariablen eingeführt.

## Wartungshinweise

- **Gotcha**: Bei künftigen Änderungen an `_headers()` oder `_request` darf der Workaround zum Entfernen von `Content-Type` bei Multipart-Anfragen (`files in kwargs`) nicht entfernt werden.

## Bekannte Einschränkungen

- **Token-Größe**: Der Base64-Upload ist strikt auf 2 MB begrenzt. Der Faktor 0.75 bei der Prüfung (`len(content_base64) * 0.75 > 2 * 1024 * 1024`) schätzt die tatsächliche Binärgröße im Speicher vor dem Dekodieren ab.
