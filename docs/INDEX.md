# Dokumentation - CAS Altiplano Starter Kit

Diese Seite ist der zentrale Einstieg in die Dokumentation des Altiplano MCP-Servers. Sie trennt zwischen der Dokumentation des Starter Kits und der projektspezifischen Dokumentation.

## Was Kommt Wohin?

| Bereich | Pfad | Inhalt |
|---|---|---|
| Starter-Kit nutzen | `docs/starter-kit-usage/` | Anleitungen für Setup, PIV-Workflow, Testing und lokales Ausführen des MCP-Servers |
| Projektarchitektur | `docs/project/architecture/` | Gesamtarchitektur, Prozessübersichten und Kontextdokumente |
| PRDs | `docs/project/prds/` | Product Requirements Documents für einzelne IT-Systeme oder Komponenten |
| PRD-Reviews | `docs/project/prd-reviews/` | Review- und Integrationsdateien zu PRD-Versionen |
| PRD-Updates | `docs/project/prd-updates/` | Update-Dateien zu manuellen oder fachlich ausgelösten PRD-Versionen |
| Feature-Artefakte | `docs/project/features/` | Pro Feature ein Unterordner mit versionierten Plänen (`plan-v001.md`, `plan-v002.md`), Reviews und Dokumentationen |
| Entscheidungen | `docs/project/decisions/` | Architektur- oder Fachentscheide, z.B. Tool-Design oder API-Mappings |
| Betrieb und Demo | `docs/project/operations/` | Projektspezifische Demo-, Setup-, ENV- oder Betriebsnotizen |

## Einstieg

| Dokument | Inhalt |
|---|---|
| [`../README.md`](../README.md) | Setup in 5 Schritten |
| [`starter-kit-usage/GETTING_STARTED.md`](starter-kit-usage/GETTING_STARTED.md) | Starter Kit für eigenes Projekt anpassen |
| [`starter-kit-usage/PIV-WORKFLOW.md`](starter-kit-usage/PIV-WORKFLOW.md) | Plan -> Implement -> Validate mit Agent Skills |
| [`../KILO_INSTRUCTIONS.md`](../KILO_INSTRUCTIONS.md) | Coding-Guide für Kilo Code |
| [`../AGENTS.md`](../AGENTS.md) | Projektkontext |

## Technische Guides

| Dokument | Inhalt |
|---|---|
| [`starter-kit-usage/TESTING.md`](starter-kit-usage/TESTING.md) | Unit- und Integrationstests mit pytest ausführen |
| [`starter-kit-usage/MCP_LOCAL_SETUP.md`](starter-kit-usage/MCP_LOCAL_SETUP.md) | MCP-Server lokal ausführen und mit Claude Desktop oder CLI-Tools testen |

## Projektdokumentation

Diese Ordner sind am Anfang bewusst leer und werden im Projektverlauf gefüllt.

| Ordner | Erwartete Dateien |
|---|---|
| `docs/project/architecture/` | Architektur- und Prozessübersichten |
| `docs/project/prds/` | PRDs (erstellt mit `/create-prd`) |
| `docs/project/prd-reviews/` | Review-Dateien (erstellt mit `/review-prd` und `/integrate-prd-review`) |
| `docs/project/prd-updates/` | Update-Dateien (erstellt mit `/update-prd`) |
| `docs/project/features/[feature-name]/` | Feature-Pläne (erstellt mit `/plan-feature`, `/review-feature-plan`, etc.) |
| `docs/project/decisions/` | Architekturentscheidungen (ADRs) |
| `docs/project/operations/` | Demo-Checklisten und Betriebsnotizen |

