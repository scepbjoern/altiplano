# 1. Executive Summary
- **System:** Vikunja MCP Server (Altiplano-Fork)
- **Dokumentversion:** v006
- **Kurzbeschreibung:** Ein sicherer, leichtgewichtiger Model Context Protocol (MCP) Server, der als Schnittstelle zwischen KI-Agenten (wie Codex, Claude, ChatGPT) und einer selbst gehosteten Vikunja-Instanz fungiert.
- **Zweck:** KI-gestütztes Aufgabenmanagement in der persönlichen Vikunja-Instanz, um effizient Projekte zu pflegen, Aufgaben zu erfassen, zu priorisieren und zu verschieben.
- **MVP-Ziel:** Lokaler, sicherer Zugriff (via `stdio`) auf grundlegende Lese- und Schreiboperationen für Aufgaben (inkl. Filtern, Daten, Kommentaren), Projekte und Labels in Vikunja, wobei sichergestellt ist, dass keine destruktiven Operationen (Löschen) durch die KI ausgeführt werden können. Optionaler Support für Cloudflare Access Service-Tokens und optimistische Konkurrenzsteuerung (Optimistic Locking) zur Vermeidung von 412-Fehlern. Update-Tools senden vollständige Pflichtfeld-Payloads (z.B. `title`), damit Teil-Updates nicht an fehlenden Vikunja-Pflichtfeldern scheitern.
- **Ausbaustufen:** Remote HTTP MCP-Endpunkt für ChatGPT, Kanban-Buckets, Dateianhänge, Task-Beziehungen und erweiterte Tools wie Personenzuweisungen (Assignees) für die spätere kollaborative Nutzung, sowie strikt abgesicherte Löschfunktionen.

# 2. Änderungshistorie
| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v006 | 2026-06-25 | Feature-Planung | "Task Löschen" zu "Allgemeines Löschen" (Tasks, Kommentare, Buckets) erweitert. |
| v006 | 2026-06-25 | Feature-Planung | Dateianhang-Feature für Remote-Homelab-Betrieb angepasst: Base64-Upload (<= 2MB), URL-Upload und Frontend-Links für manuelle Uploads bei > 2MB. Löschen von Anhängen aufgenommen. |
| v006 | 2026-06-25 | Datenmodell-Präzisierung | Bucket-Datenmodell (Kapitel 8/9) präzisiert: Buckets sind Objekte der Projekt-Kanban-View (nicht direkt am Projekt), mit Feldern `project_view_id` statt `project_id`, sowie `limit`/`count`/`position`. Gegen echte Vikunja-Instanz (v2.3.0) verifiziert. |
| v006 | 2026-06-24 | Fehlerkorrektur | Payload-Fix für `update_task`, `set_reminders`, `complete_task`, `move_task_to_project` (fehlendes Pflichtfeld `title`) sowie fehlende Felder (`description`, `identifier` in `list_projects`; `hex_color` in `create_project`) ergänzt |
| v005 | 2026-06-24 | Optimistic Locking | Optimistisches Sperren (updated-Zeitstempel) für Projekt- und Task-Updates eingeführt, um 412-Fehler zu vermeiden |
| v004 | 2026-06-24 | Cloudflare Access Support | Support für Cloudflare Service Token Header (CF-Access-Client-Id, CF-Access-Client-Secret) im MVP ergänzt |
| v003 | 2026-06-24 | PRD Update | Mocking-Setup als Chore-Feature an Priorität 1 hinzugefügt, um sicheres Testing zu gewährleisten |
| v002 | 2026-06-24 | Review Integration | Erkenntnisse aus r01 eingearbeitet (Datenmodell, Fehlerbehandlung, Tool-Abgrenzung) |
| v001 | 2026-06-24 | Initiale Erstellung | Erstes PRD erstellt und User-Feedback zu MVP/Medium-Features integriert |

# 3. Kontext und Einordnung
- **Prozess:** Persönliches Aufgabenmanagement über CLI/Web-basierte KI-Assistenten.
- **Abhängigkeiten:** Eigene Vikunja-Instanz (Version 2.3.0, ParadeDB/PostgreSQL).
- **Quellen:** Briefing-Dokument `docs/project/architecture/altiplano_vikunja_mcp_prd_briefing.md`.

# 4. Zielgruppen und Rollen
| Rolle | Beschreibung | Hauptbedürfnis | Berechtigungen im MVP |
|---|---|---|---|
| Eigennutzung (Personal User) | Alleiniger Nutzer der KI-Assistenten | Aufgaben via Chat-Interface erfassen und priorisieren, Projekte aufräumen | Lesen, Erstellen, Aktualisieren, Verschieben (kein Löschen) |
| KI-Client (Technischer Konsument) | LLM (ChatGPT, Claude, Codex) | Klar beschriebene MCP-Tools in Englisch, die vorhersehbare API-Calls ausführen | Tool-Aufrufe mit strikten Validierungen |
| Partnerin (Medium-Version) | Mitnutzerin der Vikunja-Instanz | Zuweisung von Aufgaben | Assignee-Operationen (Medium-Version) |

# 5. Problemstellung und Ziele
- **Problem:** Keine native Integration zwischen gängigen KI-Tools und der selbst gehosteten Vikunja-Instanz.
- **Ziel:** Nahtlose, sichere KI-Anbindung an Vikunja.
- **Produktprinzipien:**
  - Sicherheit vor Feature-Vollständigkeit (Token bleibt auf Server, keine automatisierten Lösch-Tools im MVP).
  - Keine client-seitige Filterlogik (Filterung geschieht durch Vikunja-API).
  - Tool-Beschreibungen im Code in Englisch für optimale LLM-Verarbeitung (Kommunikation im Chat bleibt Deutsch).
  - MVP fokussiert auf Eigennutzung lokal, Erweiterungen (Assignees, HTTP) folgen später, ohne jedoch bestehenden Code dafür rückbauen zu müssen.

# 6. Scope und Ausbaustufen

### MVP / Minimalversion
**Bereits im bestehenden Code implementiert:**
- [x] Tasks: Mehrere Tasks nach Filtern suchen (`list_tasks`), Detailansicht (`get_task`), Erstellen (`create_task` inkl. `start_date`, `end_date`, `due_date`, `priority`), Aktualisieren der Beschreibung/Status (`update_task`).
- [x] Erinnerungen: Gezieltes Setzen oder Löschen von Erinnerungen (`set_reminders`).
- [x] Projekte: Erstellen (`create_project` inkl. Verschachtelung) und rudimentäres Anzeigen (`list_projects`).
- [x] Kommentare: Ansehen, Hinzufügen (`add_comment`).
- [x] Labels: Anzeigen, Hinzufügen, Entfernen von Tasks.
- [x] Betrieb: Lokaler `stdio`-Modus via `uv run`.
- [x] Projekte: Farben (`hex_color`) bei `list_projects` in der Rückgabe.
- [x] Projekte: Tool zum Aktualisieren (`update_project`) inkl. Name, Beschreibung, Farbe und Verschachtelung (`parent_project_id`).
- [x] Task Sicherheit: Dedizierte Tools `complete_task` und `move_task_to_project`.
- [x] Optimistic Locking / Concurrency: Abfangen von 412-Fehlern (Precondition Failed) bei Updates von Projekten und Tasks durch Mitschicken des aktuellen `updated`-Zeitstempels.

**Neu zu implementieren / anzupassen für MVP:**
- [ ] Testing: Initiales Setup von API-Mocks (`httpx`) zur sicheren Ausführung lokaler Tests ohne echte Requests.
- [ ] Tool-Payload-Korrektheit: `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` müssen vor dem Update-Request den aktuellen Task per `GET` laden und das Pflichtfeld `title` (sowie ggf. weitere von Vikunja zwingend verlangte Felder) in den Payload übernehmen, analog zum bereits umgesetzten Muster in `update_project`. Ohne diese Korrektur kann ein Teil-Update (z.B. nur `description` oder `priority`) mit einem Vikunja-Fehler `2002 title: non zero value required` fehlschlagen.
- [ ] Projekte: `list_projects` um `description` und `identifier` in der Rückgabe ergänzen (Ausgabe bleibt schlank, aber vollständiger für Referenzierung durch den LLM-Client).
- [ ] Projekte: `create_project` um den Parameter `hex_color` ergänzen.

### Medium-Version
- [ ] Assignees: Personenzuweisungen aktiv nutzen (Code ist bereits vorhanden, fachliche Nutzung erst ab Einbezug der Partnerin).
- [ ] Kanban Buckets: Buckets innerhalb von Projekten erstellen, umbenennen und Tasks konkreten Buckets zuweisen.
- [ ] Dateianhänge: Dateien an bestehende Tasks anhängen (via Base64-String bis 2MB oder Download-URL) sowie Auflisten und Löschen von Anhängen. Für Dateien > 2MB wird ein Direktlink zum Task im Web-Frontend bereitgestellt.
- [ ] Betrieb: Remote HTTP MCP Endpunkt (Dockerisiert hinter Reverse Proxy) für ChatGPT Web/Mobile.
- [ ] Bulk-Limits: Harte technische Grenzen (max 5-10 Tasks) für Schreib-Aktionen (Updates/Moves). Lesezugriffe bleiben unlimitiert.

### Extended-/Luxus-Version
- [ ] Allgemeines Löschen (Tasks, Kommentare, Buckets): Destruktive Delete-Operationen für unbenötigte Tasks, Kommentare und Kanban-Buckets, welche zwingend an einen separaten, expliziten Bestätigungs-Step des Users gebunden sein müssen.
- [ ] Task-Beziehungen: Relationen zwischen Tasks (z. B. Subtasks, Blockaden) abbilden.
- [ ] Inbox Capture Workflows, Natural Language Task Parser.
- [ ] Eigene UI-Komponente (ChatGPT Connector).

### Out of Scope
- [ ] Ungeprüftes/stilles Löschen von Daten durch die KI.
- [ ] Archivierung von Projekten über `update_project`.
- [ ] `identifier` als setzbarer Parameter bei `create_project`/`update_project` (read-only/serverseitig generiertes Feld in Vikunja; wird nur im Response ausgegeben, nicht als Eingabeparameter angeboten).
- [ ] Eigene Benutzerverwaltung (wird an Vikunja delegiert).
- [ ] Rewrite in Next.js / Node.js in Phase 1.
- [ ] Verwendung von absoluten lokalen Dateipfaden für Anhänge (da LLM-Client und Remote-Server kein gemeinsames Dateisystem besitzen).

# 7. User Stories
| ID | User Story | Ausbaustufe | Demo-Bezug / Erfolgskriterium |
|---|---|---|---|
| US-1 | Als Nutzer möchte ich eine Liste meiner Projekte inkl. Verschachtelung, Farbe, Beschreibung und Kennung sehen, um den Überblick zu behalten. | MVP | `list_projects` gibt Farbe, `parent_project_id`, `description` und `identifier` zurück. |
| US-2 | Als Nutzer möchte ich Projektnamen, Beschreibungen und Farben via KI korrigieren können. | MVP | KI aktualisiert via `update_project` erfolgreich ein Projekt. |
| US-3 | Als Nutzer möchte ich gefiltert mehrere Tasks abrufen und per KI neue Aufgaben mit Fälligkeiten/Prios erstellen. | MVP | `list_tasks` und `create_task` verarbeiten die Parameter. |
| US-4 | Als Nutzer möchte ich Aufgaben kommentieren, die Beschreibung anpassen und Tasks in ein anderes Projekt verschieben, ohne dass das Update an einem fehlenden Pflichtfeld scheitert. | MVP | `update_task`, `add_comment` und `move_task_to_project` funktionieren auch bei Teil-Updates (z.B. nur `description`), ohne `2002`-Fehler. |
| US-5 | Als Nutzer möchte ich Kanban Buckets anlegen und Tasks dorthin schieben. | Medium | API Call für Bucket-Zuweisung klappt. |
| US-6 | Als Nutzer möchte ich Dateien an Tasks anhängen (bis 2MB direkt via Base64, ansonsten per Download-URL oder manuellem Upload via Direktlink) sowie Anhänge auflisten und löschen. | Medium | Dateianhänge sind in Vikunja UI sichtbar, können gelistet und gelöscht werden. |
| US-7 | Als Nutzer möchte ich veraltete Tasks, Kommentare und Kanban-Buckets komplett löschen können, aber mit einer Sicherheits-Bestätigung. | Extended | `delete_task`, `delete_comment` und `delete_bucket` verlangen explizites "Ja". |
| US-8 | Als Administrator möchte ich, dass der MCP-Server Verbindungen über ein Cloudflare Access Service Token authentifizieren kann. | MVP | Der Server übergibt die konfigurierten Header `CF-Access-Client-Id` und `CF-Access-Client-Secret` bei API-Requests. |

# 8. Kernfunktionen
| Funktion | Beschreibung | Ausbaustufe | Priorität | Rollen / Konsumenten | Hinweise |
|---|---|---|---|---|---|
| Projektverwaltung | Lesen, Erstellen und Aktualisieren (Farbe, Parent, Titel) von Projekten. | MVP | Must | Personal User | `update_project` vorhanden. `list_projects`/`create_project` müssen `description`/`identifier`/`hex_color` vollständig abdecken. |
| Taskverwaltung | Suchen (Filter), Erstellen, Aktualisieren, Verschieben, Erledigen. | MVP | Must | Personal User | Inkl. Prioritäten, Daten und Reminder. `complete_task` als eigener Wrapper. Alle Update-Tools müssen vor dem Schreiben per `GET` die Pflichtfelder (insb. `title`) laden, damit Teil-Updates nicht an Vikunja-Validierung scheitern. |
| Labelverwaltung | Labels listen und zu Tasks hinzufügen. | MVP | Should | Personal User | Bereits im Code. |
| Cloudflare Access | Authentifizierung des ausgehenden HTTP-Clients über Service Token. | MVP | Must | System-Admin | Optional über env-Variablen / config-Datei konfigurierbar. |
| Bucket-Verwaltung | Kanban Buckets innerhalb von Projekt-Kanban-Views erstellen/verwalten. | Medium | Could | Personal User | Buckets sind View-Objekte, nicht direkt am Projekt. |
| Lokaler Betrieb | Starten via `stdio` für Codex / Claude Desktop. | MVP | Must | KI-Client | Credentials via ENV. |
| Anhangsverwaltung | Auflisten, Hinzufügen (Base64 oder Download-URL) und Löschen von Dateianhängen zu Tasks. | Medium | Should | Personal User | Keine lokalen Pfade. Limitierung von Base64 auf 2MB. Frontend-Links bei Überschreitung. |

# 9. Daten und Statusmodell
Es werden im System ausschliesslich echte Produktivdaten genutzt, weshalb keine Seed-Daten existieren.

| Objekt | Zweck | Wichtige Felder | Beziehungen / Status | Relevanz für Ausbaustufe |
|---|---|---|---|---|
| Project | Ordnerstruktur für Tasks | `id`, `identifier`, `title`, `description`, `hex_color`, `parent_project_id`, `is_archived` | Enthält Tasks. Kann verschachtelt sein. | MVP |
| Bucket | Kanban-Spalten (via ProjectView) | `id`, `project_view_id`, `title`, `limit`, `count`, `position` | Ordnet Tasks innerhalb einer Projekt-Kanban-View an. | Medium |
| Task | Die eigentliche Aufgabe | `id`, `identifier`, `project_id`, `bucket_id`, `title`, `description`, `done`, `priority`, `start_date`, `due_date`, `reminders` | Gehört zu Project/Bucket, hat Labels/Comments. | MVP |
| Label | Kategorisierung | `id`, `title`, `hex_color` | Verknüpft mit Tasks. | MVP |

# 10. Schnittstellen und Umsysteme
| System / Schnittstelle | Richtung | Art | Zweck | MVP-Verhalten | spätere Ausbaustufe |
|---|---|---|---|---|---|
| Vikunja Instanz | ausgehend | REST API (`https://tasks.melbjo.win/api/v1`) | Persistenz und Logik | echt (Produktivdaten) | - |
| Cloudflare Access Gateway | ausgehend | HTTP Header-Auth | Absicherung der API | optional (Service-Token-Header) | - |
| MCP Client | eingehend | MCP Protocol | Anbindung von Claude/Codex | `stdio` lokal | HTTP Remote MCP |

# 11. Architektur und technische Leitplanken

### Brownfield / Starter Kit Kontext
Das Projekt ist ein Brownfield-Fork von `aichholzer/altiplano`. Der technische Stack ist durch `pyproject.toml` vorgegeben.

**Starter Kit Nutzung (Inventarliste für `/adapt-to-project`):**
| Baustein | Status | Bemerkung |
|---|---|---|
| MCP Server (FastMCP) | genutzt | Haupt-Framework. |
| HTTP-Client (httpx) | genutzt | Kommunikation mit Vikunja-API. |
| pytest | genutzt | Für Unit- und Integrationstests. |

**Demo-Inhalte, die für dieses Projekt nicht relevant sind:**
- Keine. Der bestehende Basiscode (inkl. Assignees, Reminder etc.) is funktional wertvoll und wird vollständig beibehalten, auch wenn einige Features (wie Assignees) fachlich erst in der Medium-Phase aktiv durch den Nutzer verwendet werden. Es findet kein Rückbau von nützlichen Features statt.

# 12. Security, Datenschutz und Compliance
- **Authentication:** Token wird über `.env` (oder `~/.config/altiplano/env`) eingelesen und **nie** in Logs, Konsolenausgaben oder an den Client weitergegeben.
- **Cloudflare Access Authentication:** Optionale Authentifizierung per Cloudflare Service Tokens, falls sich die Vikunja-Instanz hinter Cloudflare Zero Trust/Access befindet. Die Header `CF-Access-Client-Id` und `CF-Access-Client-Secret` werden optional aus der Konfiguration geladen und mitgesendet.
- **Autorisierung:** Der Token sollte in Vikunja minimal provisioniert sein. Der MCP-Server bietet im MVP **keine** Delete-Endpunkte an. Sollte der Token für gewisse Aktionen keine Rechte besitzen, findet keine proaktive Rechte-Prüfung statt; die Fehlerbehandlungsstrategie greift.
- **Fehlerbehandlungsstrategie:** API-Fehler (wie z. B. 401 Unauthorized, 404 Not Found, 2002 fehlendes Pflichtfeld) werden abgefangen und als klarer, strukturierter Text oder JSON (z.B. `{"error": "Task not found"}`) an das LLM zurückgegeben, damit die KI reagieren kann statt einfach abzustürzen.
- **Logging-Strategie:** Im MVP wird auf eigene Logging-Dateien verzichtet. Fehler und Ausgaben erfolgen direkt via MCP-Protokoll an den Client.
- **Destruktive Aktionen (Extended):** Sollte in Zukunft ein Lösch-Tool eingebaut werden, wird dieses strikt an einen manuellen Bestätigungs-Ablauf im Client gekoppelt.
- **Daten:** Bei riskanten Schreibaktionen (wie Verschieben) müssen eindeutige Ziel-IDs verlangt werden. Bei unklaren Projektnamen soll das LLM nachfragen.

# 13. Demo-Szenarien und Erfolgskriterien
| Szenario | Ablauf kurz | Abgedeckte User Stories | Ausbaustufe | Erfolgskriterium |
|---|---|---|---|---|
| Projekte aufräumen | KI liest Projekte, User bittet um Korrektur von Farben/Namen, KI updatet. | US-1, US-2 | MVP | Projekte haben danach saubere Namen und Farben in Vikunja. |
| Inbox Processing | User nennt 3 Todos, KI erstellt diese in Vikunja (inkl. Prio/Fälligkeit). | US-3 | MVP | Tasks sind im Inbox-Projekt inkl. Metadaten sichtbar. |
| Tasks pflegen | User kommentiert Task X, passt nur die Beschreibung an und verschiebt ihn in Projekt Y. | US-4 | MVP | Task ist im neuen Projekt, Beschreibung und Kommentare sind aktuell; das Teil-Update schlägt nicht an einem fehlenden Pflichtfeld fehl. |
| Cloudflare Access Bypass | MCP-Server führt Befehl aus, umgeht CF-Access-Sperre mittels Service Token. | US-8 | MVP | API-Calls gelingen trotz vorgeschaltetem Cloudflare Access Schutz. |
| Kanban-Ansicht strukturieren | User bittet, in Projekt Z Kanban-Spalten (Buckets) anzulegen und Tasks einzuordnen. | US-5 | Medium | Buckets existieren und Tasks liegen in der korrekten Spalte. |
| Anhänge verwalten | User bittet, eine Datei (entweder als Base64 <=2MB oder per Download-URL) anzuhängen, Anhänge zu listen oder zu löschen. | US-6 | Medium | Datei ist als Anhang verfügbar, wird gelistet oder gelöscht. Bei lokalen Dateien >2MB wird ein Direktlink zum Task ausgegeben. |
| Absicherung Löschung | User fordert das Löschen von Task X, einem Kommentar oder einem Bucket. | US-7 | Extended | Tool verlangt explizite Bestätigung, erst danach wird gelöscht. |

# 14. Risiken, Annahmen und offene Fragen
| Typ | Beschreibung | Auswirkung | Umgang |
|---|---|---|---|
| Risiko | Unbeabsichtigtes Überschreiben von Task-Daten bei Updates. | Hoch | `update_task` und `update_project` dürfen nur die spezifisch übergebenen Parameter per PATCH/POST ändern, nicht das ganze Objekt ersetzen. |
| Risiko | 412 Precondition Failed-Fehler bei Updates wegen fehlendem Optimistic Locking. | Hoch | Alle Update-Tools müssen vorab einen GET-Request machen, um den aktuellen `updated`-Zeitstempel abzufragen und mitzusenden. |
| Risiko | Vikunja verlangt vermutlich `title` als Pflichtfeld bei jedem Task-Update (`POST /tasks/{id}`), analog zum bereits bestätigten Verhalten bei Projekten. Fehlt es, schlägt der Request mit `2002 title: non zero value required` fehl. | Hoch | `update_task`, `set_reminders`, `complete_task` und `move_task_to_project` müssen vorab per `GET` den aktuellen Task laden und `title` (Basis aus dem aktuellen Zustand) in den Payload übernehmen, bevor Änderungen überlagert werden — analog zum bereits umgesetzten Muster in `update_project`. **Annahme, noch nicht gegen die echte Vikunja-Instanz validiert.** |
| Annahme | Vikunja API unterstützt Update von Projekt-Farbe (`hex_color`). | Mittel | Doku/Code prüfen. Falls nicht unterstützt, Scope anpassen. |
| Annahme | Vikunja API Handling von `move_task_to_project`. | Mittel | Existiert ein dedizierter Endpunkt, oder reicht ein POST auf den Task mit neuer `project_id`? Bei der Implementierung prüfen. |
| Annahme | Tool-Beschreibungen in Englisch sind für LLMs effizienter, während der Chat auf Deutsch abläuft. | Niedrig | Beschreibungen werden konsequent in Englisch verfasst. |
| Offene Frage (nicht Teil dieses Fixes) | `update_project` sendet `is_archived` nicht im Basis-Payload mit. Falls Vikunja bei `POST /projects/{id}` Full-Replace-Semantik anwendet, könnte ein Update den Archivierungsstatus unbeabsichtigt zurücksetzen. | Mittel | Separat prüfen (nicht Teil des aktuellen Fixes); bei Bestätigung als eigenständige Korrektur einplanen. |

# 15. Feature-Kandidaten für plan-feature
| Feature-Kandidat | Kurzbeschreibung | Etappe | Abhängigkeiten | Priorität |
|---|---|---|---|---|
| Testing & API-Mocks | Setup von sauberen `httpx`-Mocks für lokale, sichere Testausführung ohne echte API-Calls. | MVP (Chore) | pytest, httpx. | 1 |
| Cloudflare Access Support | Support für Cloudflare Service Token Header (CF-Access-Client-Id, CF-Access-Client-Secret) im MVP. | MVP (Enhancement) | httpx, server.py. | 1b |
| Optimistic Locking | Abfangen von 412-Fehlern bei Updates durch Mitschicken des `updated`-Zeitstempels (Projekte und Tasks). | MVP | httpx, server.py. | 1c |
| Task- & Projekt-Tool-Fixes | Payload-Fix für `update_task`/`set_reminders`/`complete_task`/`move_task_to_project` (Pflichtfeld `title`) sowie Ergänzung von `description`/`identifier` in `list_projects` und `hex_color` in `create_project`. | MVP (Bug Fix) | httpx, server.py. | 1d |
| `update_project` Tool | Neues Tool zum Ändern von Projektname, Farbe und Verschachtelung. | MVP | Vikunja API. | 2 |
| Projekt-Ausbau | `list_projects` um Farbrückgabe ergänzen. | MVP | Vikunja API. | 3 |
| Task Sicherheits-Tools | Dediziertes `complete_task` (Convenience-Wrapper) und `move_task_to_project`. | MVP | Task-Methoden. | 4 |
| Kanban Buckets | Tools für Buckets (`create_bucket`, `update_bucket`) und Task-Zuweisung. | Medium | Vikunja API. | 5 |
| Dateianhänge | Tools für Dateianhänge (`list_task_attachments`, `delete_task_attachment`, `get_task_frontend_url`, `upload_task_attachment_base64`, `upload_task_attachment_from_url`). | Medium | Vikunja API (Multipart-Form). | 6 |
| Remote HTTP MCP | Docker-Setup und HTTP-Transport (SSE) einrichten. | Medium | Reverse Proxy, Auth. | 7 |
| Allgemeines Löschen | Tools zum Löschen von Tasks, Kommentaren und Buckets mit striktem zweistufigen Bestätigungs-Pattern. | Extended | Bestätigungs-Pattern. | 8 |
| Task-Beziehungen | Tool zum Setzen von Relationen (Parent/Child, Blockaden). | Extended | Vikunja API. | 9 |

# 16. Appendix
- **Vikunja Version:** 2.3.0
- **API Endpunkte:** Die API nutzt eigene Konventionen (z. B. `PUT` für das Erstellen von Ressourcen, `POST` für Updates). Dies muss bei der Implementierung neuer Tools beachtet werden.
