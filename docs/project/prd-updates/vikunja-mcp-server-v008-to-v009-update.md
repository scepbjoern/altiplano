# PRD Update: vikunja-mcp-server v008 -> v009

## Metadaten

| Feld | Wert |
|---|---|
| Ausgangs-PRD | `docs/project/prds/vikunja-mcp-server-v008.md` |
| Neue PRD-Version | `docs/project/prds/vikunja-mcp-server-v009.md` |
| Ausgangsversion | `v008` |
| Zielversion | `v009` |
| Anlass | `Neues Feature` |
| Datum | `2026-06-25` |
| Auslöser | `Menschlich angestossen` |

## Kurzfazit

Ein neues Feature für das "Globale Label Management" wurde hinzugefügt. Bisher konnten Labels nur gelistet und zu Tasks zugewiesen werden. Zukünftig können Labels (Name, Farbe, Beschreibung) auch komplett neu angelegt, aktualisiert und gelöscht werden. Da das allgemeine Löschen (von Tasks, etc.) bereits umgesetzt wurde, wird das Label-Management als ganzheitliches Feature in der Ausbaustufe "Extended" gebündelt (inklusive `delete_label` mit Sicherheits-Bestätigung).

## Bestätigte Änderungsvorschau

| Bereich | Änderung | Begründung | Auswirkung |
|---|---|---|---|
| **Metadaten / Historie** | Version `v009` hinzugefügt. | Versionierung für das neue Feature. | `vikunja-mcp-server-v009.md` und Update-Datei erstellt. |
| **Scope (Extended)** | `Globales Label Management` (Erstellen, Aktualisieren, Löschen) als neues Feature aufgenommen. | Alles rund um Labels bleibt in einem Feature gebündelt. | Klarer Entwicklungsauftrag in der Extended-Stufe. |
| **User Stories** | `US-10` ergänzt. | Fachliche Begründung des neuen Features. | - |
| **Feature-Kandidaten** | Neuer Kandidat "Globales Label Management" (Prio 10) eingefügt. | Vorbereitung für die Umsetzung. | Bereit für `/plan-feature`. |

## Änderungen in der neuen PRD-Version

- `Dokumentversion` auf `v009` erhöht.
- `## Änderungshistorie` um Eintrag für `v009` ergänzt.
- `## 6. Scope und Ausbaustufen`: Unter `Extended-/Luxus-Version` den Punkt "Globales Label Management" (Erstellen, Aktualisieren, Löschen inkl. Bestätigung) eingefügt.
- `## 7. User Stories`: `US-10` hinzugefügt.
- `## 8. Kernfunktionen`: Neue Funktion "Globales Label Management" (Ausbaustufe: Extended) hinzugefügt.
- `## 15. Feature-Kandidaten`: "Globales Label Management" hinzugefügt.

## Nicht geänderte oder bewusst ausgesparte Punkte

- Die bestehende "Labelverwaltung" (Zuweisung zu Tasks) im MVP wurde nicht verschoben, da sie bereits implementiert ist.

## Offene Fragen und Annahmen

- Annahme: Die Vikunja API unterstützt bei Updates (`POST /labels/{id}`) dieselben Felder wie beim Erstellen. Wird bei Implementierung geprüft.

## Auswirkungen auf Feature-Pläne

| Feature-Plan | Betroffenheit | Begründung | Empfohlener nächster Schritt |
|---|---|---|---|
| `docs/project/features/allgemeines-loeschen/plan-v001.md` | `nein` | Das allgemeine Löschen ist gemäss TASKS.md bereits abgeschlossen. Das Label-Löschen wird als Teil des neuen Label-Features umgesetzt. | Nicht relevant |

## Empfehlung für den nächsten Schritt

Die neue PRD-Version und diese Update-Datei sollten nun committed werden. Anschliessend kann mit `/plan-feature Globales Label Management` der konkrete Implementierungsplan für die neuen Label-Tools erstellt werden.
