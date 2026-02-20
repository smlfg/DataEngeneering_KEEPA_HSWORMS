# Prüfungsfragen für dich

## Basics (musst du können)

### 1. Was ist dein System?
> **Antwort:** Ein Amazon-Preisüberwachungssystem. User legen Preis-Alarme an (ASIN + Zielpreis), das System checkt regelmäßig die Preise und sendet Alerts wenn der Preis fällt. Zusätzlich sucht es täglich die besten Deals.

### 2. Welche Technologien nutzt du?
> **Antwort:** FastAPI, PostgreSQL, Redis, Elasticsearch, Kafka, Docker

### 3. Wie fließen die Daten?
> **Antwort:** Keepa API → DealFinderAgent → Elasticsearch → API → User

---

## Elasticsearch (wichtig!)

### 4. Warum Elasticsearch statt PostgreSQL für Deals?
> **Antwort:** PostgreSQL hat keine gute Volltextsuche. Mit ES kann ich:
> - Fuzzy-Suche (findet "iphne" → "iphone")
> - Relevanz-Ranking (BM25)
> - Aggregations für Statistiken
> - Deutsche Stemmer (defragmentieren → deform)

### 5. Erklär den Elasticsearch-Index!
> **Antwort:** 
> - Index: `keeper-deals`
> - Analyzer: `deal_analyzer` mit german_stemmer
> - Felder: title (text + keyword), discount_percent (float), etc.
> - title^3 = 3x so wichtig wie description

### 6. Was ist eine Aggregation?
> **Antwort:** Zusammenfassung der Daten. Z.B. "zeig mir den durchschnittlichen Preis pro Kategorie" oder "wie viele Deals gibt es pro Rabatt-Stufe"

---

## Architektur

### 7. Warum async/await?
> **Antwort:** Während wir auf Keepa API warten (kann 2 Sekunden dauern), kann der Server andere Requests bearbeiten. Bessere Performance bei viele gleichzeitige User.

### 8. Warum Docker Compose?
> **Antwort:** Reproduzierbarkeit. Ein Befehl startet alles: DB, Cache, Search, API. Funktioniert auf jedem Rechner gleich.

### 9. Was ist der Unterschied zwischen Redis und PostgreSQL?
> **Antwort:** 
> - PostgreSQL = dauerhafte Speicherung (ACID)
> - Redis = temporärer Cache (sehr schnell, kann wegfallen)

---

## Prof-Herausforderungen

### 10. "Warum habt ihr kein Kafka genutzt?"
> **Antwort (diplomatisch):** Für unsere aktuelle Last ist direkte Verarbeitung einfacher. Aber Kafka ist im Stack enthalten (Docker-Container läuft) und die Architektur wäre damit entkoppelt: Producer → Topic → Consumer. Das wäre die nächste Verbesserung.

### 11. "Was wäre eure Next Step?"
> **Antwort:** Kafka-Integration für Event-Streaming, damit wir Preis-Updates asynchron verarbeiten können. Und Kibana-Dashboard für Visualisierung.

---

## Technische Details

### 12. Was macht der DealFinderAgent?
> 1. Fragt Keepa nach Deals
> 2. Filtert Dropshipper raus
> 3. Bewertet nach Rabatt + Rating
> 4. **Speichert in Elasticsearch** ← Kurswissen!
> 5. Generiert HTML-Report

### 13. Wie funktioniert die Suche in ES?
> ```json
> {
>   "multi_match": {
>     "query": "smartphone",
>     "fields": ["title^3", "description"],
>     "fuzziness": "AUTO"
>   }
> }
> ```
> - title^3 = 3x Gewichtung
> - fuzziness = findet Tippfehler

### 14. Was ist ein Index Template?
> **Antwort:** Eine Vorlage, die automatisch auf neue Indizes angewendet wird. Z.B.: "Alle Indizes, die mit 'logs-' anfangen, sollen 1 Primary Shard und 0 Replicas haben."

---

## Für die Demo

### Checkliste vor der Präsentation:
- [ ] `docker-compose ps` → alle Container grün
- [ ] `curl http://localhost:8000/health` → {"status": "healthy"}
- [ ] ES-Index existiert: `curl localhost:9200/keeper-deals`
- [ ] Demo-Query vorbereitet

### Dein Pitch (30 Sekunden):
> "Mein System ist ein Amazon-Preiswächter. User legen einen Zielpreis fest, ich überwache den Preis und sende Alerts. Zusätzlich suche ich täglich die besten Deals - diese speichere ich in Elasticsearch für schnelle Volltextsuche mit Fuzzy-Matching. Das zeigt die Kernkonzepte aus dem Data Engineering Kurs: Elasticsearch für Search, Docker für Deployment, Python für Integration."

---

## Notfall-Antworten

### "Ich hab das nicht implementiert..."
> "Das war eine Zeit-Frage. Der Kern (Elasticsearch-Suche) funktioniert. Das andere wäre die nächste Iteration."

### "Das ist ein Bug..."
> "Das ist mir bekannt. Es handelt sich um technische Schulden, die ich in der nächsten Version beheben würde."

### "Warum so kompliziert?"
> "Weil Data Engineering genau das erfordert: robuste, skalierbare Systeme. Mit FastAPI, ES und Docker folgen wir Best Practices."
