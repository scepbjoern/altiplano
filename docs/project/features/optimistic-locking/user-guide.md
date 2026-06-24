# User Guide: Optimistic Locking Support

## Was ist Optimistic Locking?
Wenn die KI Änderungen an Projekten oder Aufgaben vornimmt (z. B. den Titel anpasst, eine Fälligkeit setzt oder ein Projekt verschiebt), vergleicht die Vikunja-API die Version der Ressource, die der KI vorliegt, mit dem aktuellen Zustand in der Datenbank. Dies geschieht über einen eindeutigen Zeitstempel (`updated`).

Sollten die Versionen voneinander abweichen (weil z. B. jemand anderes die Aufgabe im Web-Interface geändert hat) oder der Zeitstempel gänzlich fehlen, antwortet die API mit dem Fehler `412 Precondition Failed`.

## Was ändert sich für dich?
- **Keine 412-Fehler mehr bei Updates:** Die KI liest vor jeder Änderung automatisch den aktuellen Status der Aufgabe oder des Projekts ein und schickt den korrekten Zeitstempel mit. Dadurch laufen Updates stabil durch.
- **Robustere Integration:** Selbst wenn du parallel im Web-Interface arbeitest, kann die KI die Daten ohne unnötige Abbrüche aktualisieren (es sei denn, es liegt ein echter Datenkonflikt vor, bei dem die KI dann eine entsprechende Fehlermeldung erhält, anstatt stumm Daten zu überschreiben).

## Beispiel: Projekt verschieben
Wenn du der KI sagst: 
> "Verschiebe mein Projekt 'Triage' ins Root-Verzeichnis."

Wird das Projekt nun fehlerfrei von `parent_project_id: 24` auf `parent_project_id: 0` aktualisiert, da der MCP-Server den aktuellen `updated`-Zeitstempel ermittelt und mitsendet.
