# 1. Executive Summary
- **System:** Vikunja MCP Server (Altiplano-Fork)
- **Dokumentversion:** v012
- **Kurzbeschreibung:** Ein sicherer, leichtgewichtiger Model Context Protocol (MCP) Server, der als Schnittstelle zwischen KI-Agenten (wie Codex, Claude, ChatGPT) und einer selbst gehosteten Vikunja-Instanz fungiert.
- **Zweck:** KI-gestütztes Aufgabenmanagement in der persönlichen Vikunja-Instanz, um effizient Projekte zu pflegen, Aufgaben zu erfassen, zu priorisieren und zu verschieben.
- **MVP-Ziel:** Lokaler, sicherer Zugriff (via `stdio`) auf grundlegende Lese- und Schreiboperationen für Aufgaben (inkl. umfassendes Filtern via `search_tasks`, Daten, Kommentaren, direkte Label-Zuweisung beim Erstellen), Projekte (inkl. Project Identifier) und Labels in Vikunja, wobei sichergestellt ist, dass keine destruktiven Operationen (Löschen) durch die KI ausgeführt werden können. Optionaler Support für Cloudflare Access Service-Tokens (ausgehend zu Vikunja) und optimistische Konkurrenzsteuerung (Optimistic Locking) zur Vermeidung von 412-Fehlern. Update-Tools senden vollständige Pflichtfeld-Payloads (z.B. `title`), damit Teil-Updates nicht an fehlenden Vikunja-Pflichtfeldern scheitern.
- **Ausbaustufen:** Remote HTTP MCP-Endpunkt mit OAuth 2.1-Authentifizierung für Web-LLM-Clients, Kanban-Buckets, Dateianhänge, Task-Beziehungen, erweiterte Tools (Assignees), strikt abgesicherte Löschfunktionen sowie umfassendes globales Label-Management.

# 2. Änderungshistorie
| Version | Datum | Anlass | Kurzbeschreibung |
|---|---|---|---|
| v012 | 2026-06-30 | Neues Feature | Erweiterte Task-Suche (`search_tasks`) und Bucket-Abfrage (`get_bucket_tasks`), vollständiger Ersatz für `list_tasks`. |
| v011 | 2026-06-29 | Neues Feature | Support für die direkte Zuweisung von Labels (`label_ids`) beim Erstellen von Aufgaben (`create_task`) hinzugefügt. |
| v010 | 2026-06-29 | Neues Feature | Project Identifier Support für das Erstellen und Aktualisieren von Projekten hinzugefügt (MVP). |
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
- [x] Tasks: Detailansicht, Erstellen (inkl. direkter Label-Zuweisung über `label_ids`), Aktualisieren der Beschreibung/Status.
- [x] Erinnerungen: Gezieltes Setzen/Löschen von Erinnerungen.
- [x] Projekte: Erstellen und Anzeigen.
- [x] Kommentare: Ansehen, Hinzufügen.
- [x] Labels: Anzeigen, Hinzufügen, Entfernen (Zuweisungen zu Tasks).
- [x] Projekte: Farben, Beschreibung, Verschachtelung (`update_project`).
- [x] Project Identifier: Support in `create_project` und `update_project` (inklusive leeren des Identifiers).
- [x] Task Sicherheit: Dedizierte Tools (`complete_task`, `move_task_to_project`).
- [x] Optimistic Locking.
- [x] Testing: API-Mocks.
- [x] Tool-Payload-Korrektheit.

**Geplant für MVP (Neu in v012):**
- [ ] Erweiterte Task-Suche: Projektübergreifende globale Suche (`search_tasks`) mit detaillierten Filterparametern (ersetzt das bisherige `list_tasks`).
- [ ] Kanban Bucket Tasks: Abrufen der Tasks eines spezifischen Buckets in korrekter Reihenfolge (`get_bucket_tasks`).
- [ ] Entfernung Altlasten: `list_tasks` wird ersatzlos entfernt.

### Medium-Version
- [ ] Assignees: Personenzuweisungen aktiv nutzen.
- [ ] Kanban Buckets: Buckets innerhalb von Projekten erstellen, umbenennen (Tasks abrufen wurde in den MVP vorgezogen).
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
| US-3 | Als Nutzer möchte ich Tasks gefiltert und **projektübergreifend** suchen sowie erstellen. | MVP | `search_tasks` (global) verarbeitet Filterparameter (z.B. `done`, `title_contains`, Priorität) korrekt und `create_task` verarbeitet `label_ids`. |
| US-4 | Als Nutzer möchte ich Aufgaben kommentieren und updaten, ohne Payload-Fehler. | MVP | Keine `2002`-Fehler bei Teil-Updates. |
| US-5 | Als Nutzer möchte ich Kanban Buckets anlegen. | Medium | API Call für Bucket-Zuweisung klappt. |
| US-6 | Als Nutzer möchte ich Dateien anhängen. | Medium | Dateianhänge sind sichtbar. |
| US-7 | Als Nutzer möchte ich veraltete Tasks komplett löschen, mit Bestätigung. | Extended | Löschen verlangt explizites „Ja". |
| US-8 | Als Administrator möchte ich Cloudflare Access Service Token nutzen. | MVP | Header `CF-Access-*` werden gesendet. |
| US-9 | Als Nutzer möchte ich den MCP-Server über Web-LLMs (OAuth 2.1) nutzen. | Medium | OAuth-Flow via Cloudflare Portal läuft durch. |
| US-10 | Als Nutzer möchte ich globale Labels anlegen, umbenennen und löschen können. | Extended | `create_label`, `update_label` und `delete_label` verarbeiten die Änderungen (mit Bestätigung beim Löschen). |
| US-11 | Als Nutzer möchte ich beim Erstellen/Aktualisieren eines Projekts einen Identifier setzen können. | MVP | `create_project` / `update_project` akzeptieren `identifier`. |
| US-12 | Als Nutzer möchte ich Tasks eines bestimmten Buckets (Kanban-Spalte) abrufen. | MVP | `get_bucket_tasks` liefert die Tasks in der korrekten Kanban-Reihenfolge. |

# 8. Kernfunktionen
| Funktion | Beschreibung | Ausbaustufe | Priorität | Rollen / Konsumenten | Hinweise |
|---|---|---|---|---|---|
| Projektverwaltung | Lesen, Erstellen und Aktualisieren von Projekten, inklusive Project Identifier. | MVP | Must | Personal User | - |
| Taskverwaltung | Suchen (projektübergreifend via `search_tasks`), Erstellen, Aktualisieren, Verschieben, Erledigen. | MVP | Must | Personal User | `list_tasks` entfällt zugunsten von `search_tasks`. |
| Labelverwaltung (Zuweisung) | Labels listen und zu Tasks hinzufügen/entfernen. | MVP | Should | Personal User | Direkte Zuweisung auch via `create_task`. |
| Globales Label Management | Labels global erstellen, aktualisieren und löschen (inkl. Bestätigung). | Extended | Could | Personal User | - |
| Cloudflare Access (ausgehend) | Authentifizierung gegenüber Vikunja über Service Token. | MVP | Must | System-Admin | - |
| Bucket-Verwaltung | Kanban Buckets erstellen/verwalten (`list_buckets`) sowie deren Tasks abfragen (`get_bucket_tasks`). | Medium/MVP | Could | Personal User | Task-Abfrage ist MVP. |
| Anhangsverwaltung | Anhänge zu Tasks listen, hinzufügen und löschen. | Medium | Should | Personal User | - |
| Remote HTTP MCP | Docker-Setup und HTTP-Transport. | Medium | Must | KI-Client (Web) | - |
| OAuth 2.1 Authentifizierung | Cloudflare MCP Server Portal als Auth-Server. | Medium | Must | KI-Client (Web) | - |

# 9. Daten und Statusmodell
| Objekt | Zweck | Wichtige Felder | Beziehungen / Status | Relevanz für Ausbaustufe |
|---|---|---|---|---|
| Project | Ordnerstruktur für Tasks | `id`, `title`, `hex_color`, `parent_project_id`, `identifier` | Enthält Tasks. | MVP |
| Bucket | Kanban-Spalten | `id`, `project_view_id`, `title`, `limit` | Ordnet Tasks. | Medium |
| Task | Die eigentliche Aufgabe | `id`, `title`, `done`, `priority` | Gehört zu Project / Bucket. | MVP |
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
Siege US-1 bis US-12. Erfolgreiche Ausführung der neuen Tools ohne Datenverlust oder ungewollte Löschungen.
Project Identifier Updates via `update_project` (inklusive leeren) dürfen andere Felder (`title`, `description` etc.) nicht überschreiben.
`create_task` verarbeitet `label_ids`, hängt die Labels direkt beim Erstellen an und gibt bei einem ungültigen Label einen klaren Teilfehler aus, während die Aufgabe dennoch erstellt wird.
`search_tasks` kombiniert `filter` und strukturierte Parameter korrekt (mit `&&`) und weicht bei isolierter Nutzung von `text` auf `s` aus.

# 14. Risiken, Annahmen und offene Fragen
| Typ | Beschreibung | Auswirkung | Umgang |
|---|---|---|---|
| Annahme | Vikunja API unterstützt bei Updates (`POST /labels/{id}`) dieselben Felder wie beim Erstellen. | Mittel | Bei der Implementierung verifizieren. |
| Risiko | Destruktive Aktionen (Löschen von Labels) beeinflussen evtl. viele historische Tasks. | Mittel | Zwingender Bestätigungs-Prompt in `delete_label`. |
| Offene Frage | Unterstützt Vikunja `title ~ '...'` und `description ~ '...'` zuverlässig im globalen Task-Filter? | Hoch | Im Feature-Plan (`/plan-feature`) für `search_tasks` klären und API testen. |
| Offene Frage | Unterstützt Vikunja `labels in 1,2,3` und `assignees in 1,2,3` exakt in dieser Syntax? | Hoch | Im Feature-Plan klären und API testen. |
| Offene Frage | Soll `label_ids` und `assignee_ids` "any" oder "all" bedeuten? | Mittel | Im Feature-Plan fachlich und technisch festlegen. |
| Offene Frage | Welche Maximalwerte gelten für `per_page`? | Gering | Im Feature-Plan evaluieren. |
| Offene Frage | Wie wird die Kanban-View eines Projekts für `get_bucket_tasks` zuverlässig erkannt und wie reagiert das System auf Projekte ohne Kanban-View? | Mittel | Fallback und Error-Handling im Plan definieren. |
| Offene Frage | Soll `filter_timezone` defaultmässig auf `Europe/Zurich` gesetzt werden? | Gering | Im Feature-Plan evaluieren. |
| Offene Frage | Sollen Parameter wie `before/after` strikt (`<` / `>`) oder inklusiv (`<=` / `>=`) interpretiert werden? | Mittel | Im Feature-Plan festlegen (Vorschlag im Prompt: strikt). |

# 15. Feature-Kandidaten für plan-feature
| Feature-Kandidat | Kurzbeschreibung | Etappe | Abhängigkeiten | Priorität |
|---|---|---|---|---|
| Erweiterte Task-Suche und Bucket-Tasks | Implementierung von `search_tasks` (global) und `get_bucket_tasks`, sowie Entfernung von `list_tasks`. | MVP | - | 1 |
| Labels in create_task | `label_ids` als optionalen Parameter für direkte Label-Zuweisung unterstützen. (Abgeschlossen) | MVP | - | 2 |
| Allgemeines Löschen | Löschen von Tasks, Kommentaren, Buckets. | Extended | Bestätigungs-Pattern. | 8 |
| Task-Beziehungen | Relationen zwischen Tasks. | Extended | Vikunja API. | 9 |
| Globales Label Management | Tools für Labels (`create_label`, `update_label`, `delete_label` inkl. Bestätigung). | Extended | Vikunja API, Bestätigungs-Pattern. | 10 |

# 16. Appendix
- **Vikunja Version:** 2.3.0
