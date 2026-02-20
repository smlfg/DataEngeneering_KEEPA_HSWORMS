# Stand des Projekts

## 1. Projektueberblick (Ist-Zustand)
Das Projekt ist ein Keepa-gestuetztes Preis-Monitoring- und Deal-Finder-System fuer Amazon-Produkte.  
Kernidee:
- Nutzer legen Watch-Listen mit ASIN und Zielpreis an.
- Ein Scheduler prueft periodisch aktuelle Preise.
- Bei Preisabfall werden Alerts erzeugt und ueber Kanaele versendet.
- Zusaetzlich gibt es eine Deal-Suche mit Filterkriterien.

Technisch basiert das Projekt auf:
- FastAPI fuer die API-Schicht
- SQLAlchemy (async) + PostgreSQL fuer Persistenz
- Keepa API als externe Datenquelle
- Docker Compose fuer Deployment

## 2. Architektur und Hauptkomponenten

### 2.1 API-Schicht
- `KeepaProjectsforDataEngeneering3BranchesMerge/src/api/main.py`
- Endpunkte u. a.:
  - `GET /health`
  - `GET/POST/DELETE /api/v1/watches`
  - `POST /api/v1/price/check`
  - `POST /api/v1/price/check-all`
  - `POST /api/v1/deals/search`
  - `GET /api/v1/tokens`
  - `GET /api/v1/rate-limit`

### 2.2 Datenquelle und Verarbeitung
- `KeepaProjectsforDataEngeneering3BranchesMerge/src/services/keepa_api.py`
- Enthalten:
  - Keepa-Client
  - Token-Bucket-Rate-Limiting
  - Produktabfrage und Deal-Suche

### 2.3 Persistenz
- `KeepaProjectsforDataEngeneering3BranchesMerge/src/services/database.py`
- Async-Modelle fuer:
  - `users`
  - `watched_products`
  - `price_history`
  - `price_alerts`
  - `deal_filters`
  - `deal_reports`

### 2.4 Scheduling / Orchestrierung
- `KeepaProjectsforDataEngeneering3BranchesMerge/src/scheduler.py`
- Periodische Preispruefung (Standard 6h)
- Alert-Erzeugung und Alert-Dispatch
- Taegliche Deal-Reports (jede 4. Scheduler-Runde)

### 2.5 Notification
- `KeepaProjectsforDataEngeneering3BranchesMerge/src/services/notification.py`
- Implementiert:
  - E-Mail Versand (SMTP-basiert)
  - Telegram/Discord Versandmethoden vorhanden

### 2.6 Deployment
- `KeepaProjectsforDataEngeneering3BranchesMerge/docker-compose.yml`
- Services:
  - `app` (API)
  - `db` (PostgreSQL)
  - `redis`
  - `scheduler`

## 3. Datenfluss (so funktioniert das System)

### Flow A: Price Watch
1. User legt Watch ueber API an (`POST /api/v1/watches`).
2. API validiert ASIN und Zielpreis.
3. API fragt aktuellen Preis ueber Keepa ab.
4. Watch wird in der DB gespeichert.
5. Scheduler laeuft periodisch und prueft aktive Watches.
6. Bei Preis <= Zielpreis wird Alert in DB angelegt.
7. Dispatcher sendet Benachrichtigung (je nach Kanal-Konfiguration).

### Flow B: Deal Search
1. Client sendet Filter (`POST /api/v1/deals/search`).
2. API ruft Keepa Deal-Search auf.
3. API filtert/rankt Ergebnisse.
4. Top-Deals werden als API-Response geliefert.

## 4. Abgleich gegen Pruefungsanforderungen (Reifegrad)

| MUSS-ID | Anforderung | Aktueller Stand | Evidenz | Reifegrad |
|---|---|---|---|---|
| M1 | End-to-End-Erfassung/Verarbeitung/Speicherung | Pipeline vorhanden, lauffaehiges Grundgeruest | `src/api/main.py`, `src/scheduler.py`, `src/services/database.py` | **Teilweise bis Erfuellt** |
| M2 | Daten laden | Keepa API-Integration vorhanden | `src/services/keepa_api.py` | **Erfuellt** |
| M3 | Periodisches Laden/Scheduling | Scheduler vorhanden (6h), auch als Container | `src/scheduler.py`, `docker-compose.yml` | **Erfuellt** |
| M4 | Umfangreiche Vorverarbeitung | Vorhanden (Filter, Scoring, Formatierung), aber inkonsistent | `src/agents/deal_finder.py`, `src/agents/price_monitor.py` | **Teilweise** |
| M5 | Sinnvolle Speicherung | PostgreSQL + historisierte Preisdaten + Alerts | `src/services/database.py` | **Erfuellt** |
| M6 | DB-Einstellungen/Optimierung | Basis vorhanden (Indizes), aber keine tiefe Optimierungsdoku | `src/services/database.py`, `src/config.py` | **Teilweise** |
| M7 | Deployment mit Einstellungen | Dockerfile + Compose vorhanden | `Dockerfile`, `docker-compose.yml` | **Erfuellt** |
| M8 | Einstellungen als Code | Grossteils gegeben, aber praezise Repro-Anleitung fehlt | `.env.example`, Compose, Config | **Teilweise bis Erfuellt** |
| M9 | Zugaengliches Git-Repo | Lokal vorhanden, externer Nachweis/Readme-Setup muss finalisiert werden | Repo-Struktur | **Teilweise** |
| M10 | Praesentation der Entscheidungen | Fachliche Erklaerungen nur teilweise dokumentiert | README + interne Notizen | **Teilweise** |

## 5. Kritische technische Punkte (wichtig fuer Verstehen und Praesentation)
1. Feldnamen-Inkonsistenz im Deal-Pfad:
   - `deal_finder.py` nutzt stark `camelCase`-Felder (`currentPrice`, `discountPercent`),
   - Keepa-Service liefert ueberwiegend `snake_case` (`current_price`, `discount_percent`).
   - Risiko: Fehlende oder ungenaue Deal-Bewertung/Filterung.
2. Versandlogik:
   - E-Mail ist implementiert, aber bei fehlender SMTP-Konfiguration wird aktuell "success" zurueckgegeben, obwohl nichts versendet wird.
3. Test- und Betriebsreife:
   - Es existieren viele Tests (`tests/`), aber die lokale Ausfuehrung war in der aktuellen Shell mangels installiertem `pytest` nicht moeglich.

## 6. Was du aktuell schon gut erklaeren kannst (Praesentationskern)
1. End-to-End-Idee: Externe Preisdaten -> Business-Logik -> Speicherung -> Alerts.
2. Warum Keepa: valide Produkt-/Preisquelle fuer Amazon-Use-Case.
3. Warum Postgres: strukturierte, persistente Speicherung mit Historie.
4. Warum Scheduler: periodische Datenabgriffe als Kern einer DE-Pipeline.
5. Warum Docker Compose: reproduzierbares Deployment als Code.

## 7. Gesamtbewertung (Ist)
- Das Projekt ist **funktional nah an pruefungsreif**.
- Der Kern-Use-Case (periodische Datenerfassung + Speicherung + API) ist vorhanden.
- Fuer eine sichere Pruefung fehlen vor allem:
  - methodische Nachweisbarkeit pro Muss-Kriterium,
  - Schliessen kritischer Inkonsistenzen im Deal-/Notification-Pfad,
  - klare praesentationsreife Dokumentation der Entscheidungen.
