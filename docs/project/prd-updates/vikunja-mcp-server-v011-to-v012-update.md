# PRD Update: v011 -> v012

**Datum:** 2026-06-30
**Anlass:** Neues Feature / Scope-Anpassung
**Ausgangs-PRD:** `docs/project/prds/vikunja-mcp-server-v011.md`
**Neues PRD:** `docs/project/prds/vikunja-mcp-server-v012.md`

## 1. Zusammenfassung der Änderungen
Ersatz des bisherigen projektbezogenen `list_tasks`-Tools durch eine leistungsstarke, projektübergreifende `search_tasks`-Suche, die den globalen `/api/v1/tasks`-Endpunkt der Vikunja-API nutzt. Ergänzung eines `get_bucket_tasks`-Tools, um Tasks für spezifische Kanban-Buckets korrekt und in der richtigen Reihenfolge abzurufen. Das bestehende Tool `list_tasks` wird ersatzlos entfernt.

## 2. Anpassungen im Scope und den Zielen
* **MVP-Erweiterung:** Die projektübergreifende Suche (`search_tasks`) und die Abfrage von Bucket-Tasks (`get_bucket_tasks`) werden in den MVP-Scope aufgenommen, um die Usability drastisch zu verbessern. 
* **MVP-Entfernung:** Das Tool `list_tasks` wird komplett entfernt.

## 3. Auswirkungen auf Rollen und User Stories
* **US-3 angepasst:** Die Task-Suche ist nun explizit projektübergreifend.
* **US-12 (Neu):** Nutzer können gezielt nach Tasks innerhalb eines bestimmten Kanban-Buckets in einem Projekt fragen, wobei die Kanban-Reihenfolge bewahrt wird.

## 4. Auswirkungen auf Architektur und Datenmodell
Das Datenmodell bleibt unverändert. Die Änderungen betreffen primär die Art, wie die Vikunja-REST-API abgefragt wird (Nutzung globaler Task-Endpunkte vs. projektbezogener Endpunkte).

## 5. Offene Fragen und Annahmen (Neu)
Zur Vorbereitung auf die Implementierung wurden 9 offene Detailfragen in Abschnitt 14 des PRDs aufgenommen:
* Zuverlässigkeit von `title ~ '...'` und `labels in 1,2,3` in der Vikunja API.
* Semantik für Array-Suchen ("any" vs. "all").
* Maximalwerte für Paginierung (`per_page`).
* Ermittlung der Kanban-View-ID und Umgang mit Projekten ohne Kanban-View.
* Standard-Zeitzone (`filter_timezone`) und Verhalten bei Datumsangaben (strikt vs. inklusiv).

Diese offenen Fragen müssen beim Erstellen des Feature-Plans technisch validiert werden.

## 6. Betroffene Feature-Pläne
Da keine unabgeschlossenen Feature-Pläne existieren, die auf das alte `list_tasks`-Tool aufbauen, sind keine aktiven Pläne betroffen. 
Der nächste logische Schritt ist die Ausführung von `/plan-feature "Erweiterte Task-Suche und Bucket-Tasks"`, um die neuen Anforderungen aus diesem PRD-Update in einen ausführbaren Entwicklungsplan zu übersetzen.
