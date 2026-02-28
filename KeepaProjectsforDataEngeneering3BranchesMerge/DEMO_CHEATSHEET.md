# Prüfungs-Demo Cheat Sheet — Keeper System

## 1. System starten (falls nicht läuft)

```bash
cd ~/DataEngeeneeringKEEPA/KeepaProjectsforDataEngeneering3BranchesMerge
docker-compose up -d
```

**Sag dem Prof:** "Mein System besteht aus 7 Docker-Containern die zusammen die Pipeline bilden."

---

## 2. Alle Container zeigen

```bash
docker-compose ps
```

**Sag dem Prof:** "Hier sehen Sie alle 7 Container:
- **db** — PostgreSQL, meine Source of Truth mit ACID-Garantien
- **kafka + zookeeper** — Event Streaming, entkoppelt Producer von Consumern
- **elasticsearch + kibana** — Full-Text Suche und Dashboards
- **app** — FastAPI Web Server mit REST-Endpoints
- **scheduler** — Das Herzstück, prüft Preise alle 6h und sammelt Deals jede Stunde"

---

## 3. Health-Check (zeigt dass alles läuft)

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

**Sag dem Prof:** "Der Health-Check zeigt den Status aller Services auf einen Blick."

---

## 4. Token-Status (Rate Limiting erklären)

```bash
curl -s http://localhost:8000/api/v1/tokens | python3 -m json.tool
```

**Sag dem Prof:** "Die Keepa API hat ein Token-System: 20 Tokens pro Minute. Mein Token Bucket Algorithmus stellt sicher, dass ich das Limit nicht überschreite. Wenn die Tokens leer sind, wartet das System asynchron — es blockiert nicht."

---

## 5. Aktive Watches zeigen

```bash
curl -s "http://localhost:8000/api/v1/watches?user_id=a0000000-0000-0000-0000-000000000001" | python3 -m json.tool
```

**Sag dem Prof:** "Das sind meine aktiven Price Watches. Jeder Watch hat eine ASIN und einen Zielpreis. Der Scheduler prüft alle 6h ob der aktuelle Preis unter den Zielpreis gefallen ist."

---

## 6. Neuen Watch erstellen (LIVE!)

```bash
curl -s -X POST "http://localhost:8000/api/v1/watches?user_id=a0000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B09V3KXJPB", "target_price": 50.00}' | python3 -m json.tool
```

**Sag dem Prof:** "Ich erstelle jetzt live einen neuen Watch. Die ASIN ist eine Amazon-Produkt-ID, 10 Zeichen. Der Zielpreis ist 50 Euro. Das wird in PostgreSQL gespeichert."

---

## 7. Einzelnen Preis-Check (LIVE!)

```bash
curl -s -X POST http://localhost:8000/api/v1/price/check \
  -H "Content-Type: application/json" \
  -d '{"asin": "B09V3KXJPB"}' | python3 -m json.tool
```

**Sag dem Prof:** "Hier frage ich live die Keepa API ab. Das Ergebnis wird dreifach geschrieben — das ist mein Triple-Write Pattern: PostgreSQL, Kafka und Elasticsearch gleichzeitig."

---

## 8. Kafka Topics zeigen

```bash
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

**Sag dem Prof:** "Das sind meine Kafka Topics: price-updates und deal-updates. Jede Preisänderung wird als Event an Kafka gesendet. Separate Consumer verarbeiten diese Events unabhängig."

---

## 9. Kafka Messages mitlesen (LIVE!)

```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic price-updates \
  --from-beginning --max-messages 3
```

**Sag dem Prof:** "Hier sehen Sie die tatsächlichen Events in Kafka. Jedes Event enthält ASIN, Preis, Zeitstempel. Consumer können diese Events lesen und weiterverarbeiten."

---

## 10. Elasticsearch Deals durchsuchen

```bash
curl -s 'http://localhost:9200/keeper-deals/_search?pretty&size=3'
```

**Sag dem Prof:** "Elasticsearch indexiert alle Deals als JSON-Dokumente. Die Stärke: Full-Text Suche — ich kann nach 'mechanical keyboard' suchen und bekomme sofort alle passenden Deals."

---

## 11. Elasticsearch Aggregationen

```bash
curl -s http://localhost:8000/api/v1/deals/aggregations | python3 -m json.tool
```

**Sag dem Prof:** "Aggregationen zeigen mir Statistiken über alle Deals: Durchschnittspreis, Anzahl pro Kategorie, Top-Rabatte. Das ist Analytics auf den Daten."

---

## 12. Preis-Historie für ein Produkt

```bash
curl -s http://localhost:8000/api/v1/prices/B09V3KXJPB/history | python3 -m json.tool
```

**Sag dem Prof:** "Hier sehen Sie die Preisentwicklung über Zeit. Jeder Datenpunkt wurde bei einem Scheduler-Zyklus erfasst."

---

## 13. Kibana Dashboard öffnen

Browser: **http://localhost:5601**

→ Discover → `keeper-deals*` oder `keeper-prices*`

**Sag dem Prof:** "Kibana visualisiert die Elasticsearch-Daten. Hier sehen Sie Deals nach Rabatt sortiert, Preistrends über Zeit, und die gesammelten Keyboards."

---

## 14. Scheduler Logs zeigen

```bash
docker-compose logs --tail=30 scheduler
```

**Sag dem Prof:** "Die Scheduler-Logs zeigen den letzten Zyklus: wie viele Watches geprüft, wie viele Preisänderungen, wie viele Events an Kafka gesendet, wie viele in Elasticsearch indexiert."

---

## 15. PostgreSQL Daten zeigen

```bash
docker-compose exec db psql -U postgres -d keeper -c \
  "SELECT asin, target_price, current_price, status FROM watched_products LIMIT 5;"
```

**Sag dem Prof:** "PostgreSQL ist meine Source of Truth. Alle Watches mit aktuellem Preis und Status sind hier relational gespeichert."

---

## Die 3 Prof-Fragen (auswendig!)

### "Warum Kafka UND PostgreSQL?"
"PostgreSQL speichert den **State** — was ist der aktuelle Preis. Kafka streamt die **Events** — was ist passiert. PostgreSQL gibt ACID-Garantien. Kafka gibt lose Kopplung und die Möglichkeit, neue Consumer hinzuzufügen ohne bestehenden Code zu ändern."

### "Wie funktioniert das Rate Limiting?"
"Token Bucket: 20 Tokens pro Minute. Jeder API-Call kostet Tokens. Wenn leer, wartet mein Code asynchron. Ein asyncio Lock verhindert Race Conditions bei parallelen Requests."

### "Was wenn Kafka ausfällt?"
"Graceful Degradation. Der Scheduler loggt eine Warnung und läuft weiter. Preise werden weiterhin in PostgreSQL geschrieben. Nur die Kafka-Events gehen verloren. Wenn Kafka wieder da ist, fließen neue Events normal. Das ist eine bewusste Design-Entscheidung für Einfachheit."

---

## Architektur in einem Satz

"Mein System monitort Amazon-Keyboard-Preise über die Keepa API, schreibt jede Preisänderung in drei Systeme gleichzeitig — PostgreSQL, Kafka und Elasticsearch — und benachrichtigt User per Email, Telegram oder Discord wenn der Preis unter ihren Zielpreis fällt."
