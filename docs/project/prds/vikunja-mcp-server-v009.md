# 1. Executive Summary
- **System:** Vikunja MCP Server (Altiplano-Fork)
- **Dokumentversion:** v009
- **Kurzbeschreibung:** Ein sicherer, leichtgewichtiger Model Context Protocol (MCP) Server, der als Schnittstelle zwischen KI-Agenten (wie Codex, Claude, ChatGPT) und einer selbst gehosteten Vikunja-Instanz fungiert.
- **Zweck:** KI-gestütztes Aufgabenmanagement in der persönlichen Vikunja-Instanz, um effizient Projekte zu pflegen, Aufgaben zu erfassen, zu priorisieren und zu verschieben.
- **MVP-Ziel:** Lokaler, sicherer Zugriff (via `stdio`) auf grundlegende Lese- und Schreiboperationen für Aufgaben (inkl. Filtern, Daten, Kommentaren), Projekte und Labels in Vikunja, wobei sichergestellt ist, dass keine destruktiven Operationen (Löschen) durch die KI ausgeführt werden können. Optionaler Support für Cloudflare Access Service-Tokens (ausgehend zu Vikunja) und optimistische Konkurrenzsteuerung (Optimistic Locking) zur Vermeidung von 412-Fehlern. Update-Tools senden vollständige Pflichtfeld-Payloads (z.B. `title`), damit Teil-Updates nicht an fehlenden Vikunja-Pflichtfeldern scheitern.
- **Ausbaustufen:** Remote HTTP MCP-Endpunkt mit OAuth 2.1-Authentifizierung für Web-LLM-Clients, Kanban-Buckets, Dateianhänge, Task-Beziehungen, erweiterte Tools (Assignees), strikt abgesicherte Löschfunktionen sowie umfassendes globales Label-Management.

# 2. Änderungshistorie
| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v009 | 2026-06-25 | Neues Feature | Globales Label Management (Erstellen, Aktualisieren, Löschen) in Ausbaustufe Extended als eigenständiges Feature hinzugefügt. |
| v008 | 2026-06-25 | Fehlerkorrektur / Architektur-Widerspruch | OAuth-2.1-Strategie korrigiert: Statt Eigenbau-Authorization-Server übernimmt Cloudflare MCP Server Portal (Managed OAuth). |
| v007 | 2026-06-25 | Neues Feature | OAuth 2.1-Authentifizierung (FastMCP OAuthProvider + SQLite-Token-Store) ergänzt. |
| v006 | 2026-06-25 | Feature-Planung | „Task Löschen" zu „Allgemeines Löschen" (Tasks, Kommentare, Buckets) erweitert. Dateianhänge und Bucket-Modell präzisiert. |
| v005 | 2026-06-24 | Optimistic Locking | Optimistisches Sperren (updated-Zeitstempel) eingeführt. |
| v004 | 2026-06-24 | Cloudflare Access Support | Support für Cloudflare Service Token Header ergänzt. |
| v003 | 2026-06-24 | PRD Update | Mocking-Setup als Chore-Feature hinzugefügt. |
| v002 | 2026-06-24 | Review Integration | Erkenntnisse aus r01 eingearbeitet. |
| v001 | 2026-06-24 | Initiale Erstellung | Erstes PRD erstellt. |

# 3. Kontext und Einordnung
- **Prozess:** Persönliches Aufgabenmanagement über CLI/Web-basierte KI-Assistenten.
- **Abhängigkeiten:** Eigene Vikunja-Instanz (Version 2.3.0, ParadeDB/PostgreSQL).
- **Quellen:** Briefing-Dokument `docs/project/architecture/altiplano_vikunja_mcp_prd_briefing.md`.

# 4. Zielgruppen und Rollen
| Rolle | Beschreibung | Hauptbedürfnis | Berechtigungen im MVP |
|---|---|---|---|
| Eigennutzung (Personal User) | Alleiniger Nutzer der KI-Assistenten | Aufgaben via Chat-Interface erfassen und priorisieren, Projekte aufräumen | Lesen, Erstellen, Aktualisieren, Verschieben (kein Löschen) |
| KI-Client (Technischer Konsument) | LLM (ChatGPT, Claude, Codex, Gemini) | Klar beschriebene MCP-Tools in Englisch, die vorhersehbare API-Calls ausführen | Tool-Aufrufe mit strikten Validierungen |
| Partnerin (Medium-Version) | Mitnutzerin der Vikunja-Instanz | Zuweisung von Aufgaben | Assignee-Operationen (Medium-Version) |

# 5. Problemstellung und Ziele
- **Problem:** Keine native Integration zwischen gängigen KI-Tools und der selbst gehosteten Vikunja-Instanz.
- **Ziel:** Nahtlose, sichere KI-Anbindung an Vikunja – lokal und remote.
- **Produktprinzipien:**
  - Sicherheit vor Feature-Vollständigkeit.
  - Keine client-seitige Filterlogik (durch Vikunja-API).
  - Tool-Beschreibungen im Code in Englisch.
  - MVP fokussiert auf Eigennutzung lokal.

# 6. Scope und Ausbaustufen

### MVP / Minimalversion
**Bereits im bestehenden Code implementiert:**
- [x] Tasks: Mehrere Tasks suchen, Detailansicht, Erstellen, Aktualisieren der Beschreibung/Status.
- [x] Erinnerungen: Gezieltes Setzen/Löschen von Erinnerungen.
- [x] Projekte: Erstellen und Anzeigen.
- [x] Kommentare: Ansehen, Hinzufügen.
- [x] Labels: Anzeigen, Hinzufügen, Entfernen (Zuweisungen zu Tasks).
- [x] Projekte: Farben, Beschreibung, Verschachtelung (`update_project`).
- [x] Task Sicherheit: Dedizierte Tools (`complete_task`, `move_task_to_project`).
- [x] Optimistic Locking.
- [x] Testing: API-Mocks.
- [x] Tool-Payload-Korrektheit.

### Medium-Version
- [ ] Assignees: Personenzuweisungen aktiv nutzen.
- [ ] Kanban Buckets: Buckets innerhalb von Projekten erstellen, umbenennen.
- [ ] Dateianhänge: Dateien an Tasks anhängen (Base64/URL).
- [ ] Remote HTTP MCP: Remote-Endpunkt für Web-LLM-Clients.
- [ ] OAuth 2.1-Authentifizierung: Cloudflare MCP Server Portal als Authorization Server.

### Extended-/Luxus-Version
- [ ] Allgemeines Löschen (Tasks, Kommentare, Buckets): Destruktive Delete-Operationen mit expliziter Bestätigung.
- [ ] **Globales Label Management**: Vollständiges globales Verwalten von Labels (Erstellen, Aktualisieren, sowie Löschen inkl. Sicherheitsbestätigung).
- [ ] Task-Beziehungen: Relationen zwischen Tasks (z. B. Subtasks, Blockaden).
- [ ] Inbox Capture Workflows, Natural Language Task Parser.
- [ ] Eigene UI-Komponente.

### Out of Scope
- [ ] Ungeprüftes/stilles Löschen von Daten durch die KI.
- [ ] Eigene Benutzerverwaltung (wird an Vikunja delegiert).

# 7. User Stories
| ID | User Story | Ausbaustufe | Demo-Bezug / Erfolgskriterium |
|---|---|---|---|
| US-1 | Als Nutzer möchte ich eine Liste meiner Projekte sehen. | MVP | `list_projects` gibt vollständige Details zurück. |
| US-2 | Als Nutzer möchte ich Projekte via KI korrigieren. | MVP | KI aktualisiert via `update_project`. |
| US-3 | Als Nutzer möchte ich gefiltert Tasks abrufen und erstellen. | MVP | `list_tasks` und `create_task` verarbeiten die Parameter. |
| US-4 | Als Nutzer möchte ich Aufgaben kommentieren und updaten, ohne Payload-Fehler. | MVP | Keine `2002`-Fehler bei Teil-Updates. |
| US-5 | Als Nutzer möchte ich Kanban Buckets anlegen. | Medium | API Call für Bucket-Zuweisung klappt. |
| US-6 | Als Nutzer möchte ich Dateien anhängen. | Medium | Dateianhänge sind sichtbar. |
| US-7 | Als Nutzer möchte ich veraltete Tasks komplett löschen, mit Bestätigung. | Extended | Löschen verlangt explizites „Ja". |
| US-8 | Als Administrator möchte ich Cloudflare Access Service Token nutzen. | MVP | Header `CF-Access-*` werden gesendet. |
| US-9 | Als Nutzer möchte ich den MCP-Server über Web-LLMs (OAuth 2.1) nutzen. | Medium | OAuth-Flow via Cloudflare Portal läuft durch. |
| US-10 | Als Nutzer möchte ich globale Labels (Name, Farbe, Beschreibung) anlegen, umbenennen und löschen können, um meine Task-Kategorisierung anzupassen. | Extended | `create_label`, `update_label` und `delete_label` verarbeiten die Änderungen (mit Bestätigung beim Löschen). |

# 8. Kernfunktionen
| Funktion | Beschreibung | Ausbaustufe | Priorität | Rollen / Konsumenten | Hinweise |
|---|---|---|---|---|---|
| Projektverwaltung | Lesen, Erstellen und Aktualisieren von Projekten. | MVP | Must | Personal User | - |
| Taskverwaltung | Suchen, Erstellen, Aktualisieren, Verschieben, Erledigen. | MVP | Must | Personal User | - |
| Labelverwaltung (Zuweisung) | Labels listen und zu Tasks hinzufügen/entfernen. | MVP | Should | Personal User | Bereits im Code. |
| Globales Label Management | Labels global erstellen, aktualisieren und löschen (inkl. Bestätigung). | Extended | Could | Personal User | Neues Feature, gebündelt. |
| Cloudflare Access (ausgehend) | Authentifizierung gegenüber Vikunja über Service Token. | MVP | Must | System-Admin | - |
| Bucket-Verwaltung | Kanban Buckets erstellen/verwalten. | Medium | Could | Personal User | - |
| Anhangsverwaltung | Anhänge zu Tasks listen, hinzufügen und löschen. | Medium | Should | Personal User | - |
| Remote HTTP MCP | Docker-Setup und HTTP-Transport. | Medium | Must | KI-Client (Web) | - |
| OAuth 2.1 Authentifizierung | Cloudflare MCP Server Portal als Auth-Server. | Medium | Must | KI-Client (Web) | - |

# 9. Daten und Statusmodell
| Objekt | Zweck | Wichtige Felder | Beziehungen / Status | Relevanz für Ausbaustufe |
|---|---|---|---|---|
| Project | Ordnerstruktur für Tasks | `id`, `title`, `hex_color`, `parent_project_id` | Enthält Tasks. | MVP |
| Bucket | Kanban-Spalten | `id`, `project_view_id`, `title`, `limit` | Ordnet Tasks. | Medium |
| Task | Die eigentliche Aufgabe | `id`, `title`, `done`, `priority` | Gehört zu Project. | MVP |
| Label | Kategorisierung | `id`, `title`, `hex_color`, `description` | Verknüpft mit Tasks, global existent. | MVP / Extended |

# 10. Schnittstellen und Umsysteme
| System / Schnittstelle | Richtung | Art | Zweck | MVP-Verhalten | spätere Ausbaustufe |
|---|---|---|---|---|---|
| Vikunja Instanz | ausgehend | REST API | Persistenz und Logik | echt (Produktivdaten) | - |
| Cloudflare Access | ausgehend | HTTP Header | Absicherung Vikunja | optional | - |
| MCP Client (lokal) | eingehend | MCP Protocol / stdio | Anbindung Clients | `stdio` lokal | - |
| MCP Client (remote) | eingehend | HTTP SSE | Anbindung Web-Clients | - | OAuth 2.1 |

# 11. Architektur und technische Leitplanken
### Brownfield / Starter Kit Kontext
Das Projekt ist ein Brownfield-Fork von `aichholzer/altiplano`.
- MCP Server (FastMCP), HTTP-Client (httpx), pytest werden genutzt.

# 12. Security, Datenschutz und Compliance
- Keine automatisierten Lösch-Tools im MVP. `delete_label` wandert wie alle Destructive Actions in einen Bestätigungs-Step (Extended).
- Token-Sicherheit via ENV-Variablen und Cloudflare Service Tokens.

# 13. Demo-Szenarien und Erfolgskriterien
Siehe US-1 bis US-10. Erfolgreiche Ausführung der neuen Label-Tools ohne Datenverlust oder ungewollte Löschungen.

# 14. Risiken, Annahmen und offene Fragen
| Typ | Beschreibung | Auswirkung | Umgang |
|---|---|---|---|
| Annahme | Vikunja API unterstützt bei Updates (`POST /labels/{id}`) dieselben Felder wie beim Erstellen. | Mittel | Bei der Implementierung verifizieren. |
| Risiko | Destruktive Aktionen (Löschen von Labels) beeinflussen evtl. viele historische Tasks. | Mittel | Zwingender Bestätigungs-Prompt in `delete_label`. |

# 15. Feature-Kandidaten für plan-feature
| Feature-Kandidat | Kurzbeschreibung | Etappe | Abhängigkeiten | Priorität |
|---|---|---|---|---|
| Task- & Projekt-Fixes | Payload-Fixes und Ergänzungen. | MVP | - | 1 |
| Allgemeines Löschen | Löschen von Tasks, Kommentaren, Buckets. | Extended | Bestätigungs-Pattern. | 8 |
| Task-Beziehungen | Relationen zwischen Tasks. | Extended | Vikunja API. | 9 |
| Globales Label Management | Tools für Labels (`create_label`, `update_label`, `delete_label` inkl. Bestätigung). | Extended | Vikunja API, Bestätigungs-Pattern. | 10 |

# 16. Appendix
- **Vikunja Version:** 2.3.0
