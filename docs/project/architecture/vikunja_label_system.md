# Vikunja Label-System

Ziel dieses Label-Systems ist, Aufgaben in Vikunja nicht über zu viele Projekte oder unscharfe Labels zu organisieren, sondern über wenige, klar unterscheidbare Label-Familien.

Es gibt drei Label-Typen:

```text
@ = Kontext / Ort / Werkzeug
# = Aufwand / Grösse
! = Energie / Konzentration
```

Damit beantworten die Labels drei praktische Fragen:

1. **Wo oder womit kann ich diese Aufgabe erledigen?**
2. **Wie gross ist die Aufgabe ungefähr?**
3. **Braucht die Aufgabe besonders wenig oder besonders viel mentale Energie?**

Die meisten Aufgaben müssen nicht zwingend alle drei Label-Typen erhalten. Besonders die Energie-Labels sollen sparsam verwendet werden.

---

## 1. Kontext-Labels: `@`

Kontext-Labels beschreiben, **wo**, **womit** oder **unter welchen äusseren Bedingungen** eine Aufgabe erledigt werden kann oder sinnvollerweise erledigt werden soll.

Finale Kontext-Labels:

```text
@anywhere
@online
@home
@partner
@work
@gym
@outdoor
@city
@winti
@zh
@car
@train
@walk
```

### Bedeutung der Kontext-Labels

| Label | Bedeutung |
|---|---|
| `@anywhere` | Geht überall; keine besonderen Hilfsmittel nötig |
| `@online` | Internet nötig; Smartphone, Tablet oder Computer reichen grundsätzlich aus |
| `@home` | Nur oder sinnvollerweise zu Hause erledigbar |
| `@partner` | Nur oder sinnvollerweise bei der Partnerin zu Hause erledigbar |
| `@work` | Am Arbeitsplatz erledigbar oder dort sinnvoll |
| `@gym` | Im Fitnesszentrum erledigbar oder gewünscht |
| `@outdoor` | Draussen, in der Natur, beim Spazieren oder unterwegs im Freien |
| `@city` | In der Stadt allgemein erledigbar |
| `@winti` | In Winterthur erledigbar oder dort sinnvoll |
| `@zh` | In Zürich erledigbar oder dort sinnvoll |
| `@car` | Auto nötig oder deutlich sinnvoller mit Auto |
| `@train` | Im Zug oder öffentlichen Verkehr machbar |
| `@walk` | Beim Gehen oder Spazieren machbar |

### Hinweise zu Shopping-Kontexten

Ein allgemeines Label wie `@shop` wird bewusst nicht verwendet, weil es zu generisch wäre und sich mit einem Projekt oder Subprojekt `Shopping` überschneiden würde.

Shopping sollte primär über Projekte oder Subprojekte organisiert werden, zum Beispiel:

```text
Shopping
  Online
  Haushalt
  Kleidung
  Drogerie
  Technik
  Geschenke
  Lebensmittel
  Baumarkt
```

Für die Ausführung reichen dann meist vorhandene Kontext-Labels wie:

```text
@online
@city
@winti
@zh
@car
```

Spezifische Shop-Labels wie `@amazon`, `@ikea`, `@apotheke` oder `@baumarkt` sollten nur ergänzt werden, wenn sich später zeigt, dass diese Orte oder Anbieter regelmässig als eigener Kontext gebraucht werden.

---

## 2. Aufwand / Grösse: `#`

Aufwands-Labels beschreiben nicht exakt die Dauer, sondern die **Grösse** einer Aufgabe. Die Logik orientiert sich an T-Shirt-Grössen.

Finale Aufwand-Labels:

```text
#xs
#s
#m
#l
```

### Bedeutung der Aufwand-Labels

| Label | Bedeutung | Grobe Orientierung |
|---|---|---:|
| `#xs` | Mini-Aufgabe, sofort machbar | ca. 1–10 Minuten |
| `#s` | Kleine Aufgabe, passt in eine kurze freie Lücke | ca. 10–30 Minuten |
| `#m` | Normale Aufgabe mit spürbarem Aufwand | ca. 30–90 Minuten |
| `#l` | Grössere Aufgabe, braucht einen bewussten Arbeitsblock | ca. 1.5–3 Stunden |

### Prinzip

Die Labels sind bewusst grob. Beim Erfassen einer Aufgabe muss nicht exakt geschätzt werden, ob etwas 45, 60 oder 90 Minuten dauert. Es reicht die Einschätzung:

```text
Ist das eher XS, S, M oder L?
```

Alles, was grösser als `#l` wirkt, sollte eher nicht als einzelne Aufgabe behandelt werden. In diesem Fall ist es wahrscheinlich ein Projekt, ein Subprojekt oder eine Aufgabe mit mehreren Subtasks.

Beispiel:

```text
Task: Steuererklärung machen
```

Besser aufteilen in:

```text
- Unterlagen zusammensuchen
- Lohnausweis prüfen
- Versicherungsnachweise suchen
- Abzüge grob sammeln
- Steuerformular ausfüllen
- Final prüfen
```

Die einzelnen Subtasks können dann wieder passende Aufwand-Labels wie `#s`, `#m` oder `#l` erhalten.

---

## 3. Energie / Konzentration: `!`

Energie-Labels markieren nur besondere Fälle. Die meisten Aufgaben erhalten **kein** Energie-Label.

Finale Energie-Labels:

```text
!easy
!focus
```

### Bedeutung der Energie-Labels

| Label | Bedeutung |
|---|---|
| `!easy` | Besonders einfach; geht auch müde, nebenbei oder mit wenig mentaler Energie |
| `!focus` | Braucht Konzentration, Musse, Ruhe oder einen klaren Kopf |

### Prinzip

Energie-Labels werden sparsam eingesetzt:

```text
Kein Energie-Label = normale Aufgabe
!easy             = besonders leicht zugänglich
!focus            = braucht bewusst Konzentration
```

So bleibt die Label-Liste übersichtlich und die Energie-Labels dienen wirklich als Signal.

---

## Finale Label-Liste

### Kontext

```text
@anywhere
@online
@home
@partner
@work
@gym
@outdoor
@city
@winti
@zh
@car
@train
@walk
```

### Aufwand / Grösse

```text
#xs
#s
#m
#l
```

### Energie / Konzentration

```text
!easy
!focus
```

---

## Beispielhafte Anwendung

### Kurze Online-Admin-Aufgabe

```text
Task: Krankenkasse wegen Rechnung kontaktieren
Labels: @online, #s, !easy
```

### Konzeptarbeit zu Hause

```text
Task: Konzept für Altiplano-Features skizzieren
Labels: @home, #m, !focus
```

### Leichte Aufgabe im Zug

```text
Task: Artikel im Zug lesen
Labels: @train, #s, !easy
```

### Kreative Arbeit mit Konzentration

```text
Task: Songidee weiterentwickeln
Labels: @home, #m, !focus
```

### Reflexion beim Spazieren

```text
Task: Ferienidee beim Spazieren durchdenken
Labels: @walk, @outdoor, #s, !easy
```

### Einkauf mit Ortsbezug

```text
Task: Wanderschuhe in Zürich anprobieren
Labels: @zh, @city, #m
```

### Aufgabe mit Auto-Kontext

```text
Task: Sperrige Dinge entsorgen
Labels: @car, #m
```

---

## Praktische Filterideen

### Sehr kurze Aufgaben

```text
done = false && labels in #xs
```

### Kurze Aufgaben für freie Lücken

```text
done = false && labels in #xs, #s
```

### Online machbare Aufgaben

```text
done = false && labels in @online
```

### Einfache Aufgaben mit wenig Energie

```text
done = false && labels in !easy
```

### Fokus-Aufgaben

```text
done = false && labels in !focus
```

### Aufgaben für den Zug

```text
done = false && labels in @train
```

### Aufgaben für Spaziergänge

```text
done = false && labels in @walk
```

### Aufgaben in Zürich

```text
done = false && labels in @zh
```

---

## Grundregel

Das Label-System soll helfen, schnell zu beantworten:

```text
Was kann ich jetzt hier, mit der verfügbaren Zeit und meiner aktuellen Energie sinnvoll erledigen?
```

Deshalb gilt:

- `@` beschreibt den Kontext.
- `#` beschreibt die grobe Grösse.
- `!` markiert besondere Energieanforderungen.
- Nicht jede Aufgabe braucht jedes Label.
- Zu grosse Aufgaben werden aufgeteilt statt mit noch grösseren Labels versehen.
