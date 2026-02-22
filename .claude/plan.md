# Plan: Kibana Auto-Load Dashboards

## Ziel

Beim `docker-compose up` sollen 2 fertige Kibana-Dashboards automatisch geladen werden -- ohne manuelles Klicken in der Kibana UI. Beim Prüfungs-Demo: Container starten → Kibana öffnen → Dashboards sind da.

## Architektur

```
kibana/
├── setup-kibana.sh          # Wartet auf Kibana, importiert NDJSON
└── saved_objects.ndjson     # Data Views + Visualisierungen + 2 Dashboards

docker-compose.yml
└── kibana-setup (neuer Service)  # Einmal-Job: importiert und beendet sich
```

**Warum ein Init-Service statt Volume-Mount?**
Kibana 8.x hat keinen Auto-Import-Ordner. Man muss die Saved Objects API (`/api/saved_objects/_import`) aufrufen. Ein kleiner Alpine-Container mit curl erledigt das.

---

## 2 Dashboards

### Dashboard 1: "Deal Overview"
Für `keeper-deals` Index:
- **Metric**: Gesamt-Deals (Count)
- **Metric**: Durchschnitts-Rabatt (Avg discount_percent)
- **Pie Chart**: Deals nach Domain (DE/UK/FR/IT/ES)
- **Bar Chart**: Top 10 Deals nach deal_score
- **Line Chart**: Deals über Zeit (date_histogram auf timestamp)
- **Data Table**: Letzte 20 Deals (title, current_price, discount_percent, domain, deal_score)

### Dashboard 2: "Price Monitor"
Für `keeper-prices` Index:
- **Metric**: Gesamt Price Events
- **Line Chart**: Preisverlauf über Zeit (avg current_price pro Tag)
- **Pie Chart**: Events nach Domain
- **Data Table**: Letzte 20 Preisänderungen (asin, current_price, price_change_percent, domain)

---

## Schritte

### Schritt 1: `kibana/saved_objects.ndjson` erstellen

NDJSON-Datei mit allen Saved Objects:
1. **Data View** `keeper-deals` (timeField: timestamp)
2. **Data View** `keeper-prices` (timeField: timestamp)
3. **6 Lens-Visualisierungen** für Deal Dashboard
4. **4 Lens-Visualisierungen** für Price Dashboard
5. **Dashboard** "Deal Overview" (referenziert die 6 Panels)
6. **Dashboard** "Price Monitor" (referenziert die 4 Panels)

Kibana 8.11 nutzt das Lens-Format für Visualisierungen. Jedes Saved Object ist eine JSON-Zeile im NDJSON.

### Schritt 2: `kibana/setup-kibana.sh` erstellen

```bash
#!/bin/bash
# Wartet bis Kibana erreichbar ist, importiert Saved Objects
KIBANA_URL="http://kibana:5601"
MAX_RETRIES=60

for i in $(seq 1 $MAX_RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KIBANA_URL/api/status")
  if [ "$STATUS" = "200" ]; then
    echo "Kibana is ready, importing dashboards..."
    curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
      -H "kbn-xsrf: true" \
      --form file=@/setup/saved_objects.ndjson
    echo "Dashboards imported successfully!"
    exit 0
  fi
  echo "Waiting for Kibana... ($i/$MAX_RETRIES)"
  sleep 5
done
echo "Kibana did not become ready in time"
exit 1
```

### Schritt 3: docker-compose.yml ergänzen

Neuer Service `kibana-setup`:
```yaml
kibana-setup:
  image: curlimages/curl:latest
  depends_on:
    - kibana
  volumes:
    - ./kibana:/setup
  entrypoint: ["/bin/sh", "/setup/setup-kibana.sh"]
  restart: "no"
```

Kein neuer langlebiger Container -- startet einmal, importiert, beendet sich. Zeigt in `docker-compose ps` als "Exit 0" an.

### Schritt 4: Verifikation

```bash
# 1. Rebuild + Restart
docker-compose up -d

# 2. Warten bis kibana-setup fertig ist
docker-compose logs kibana-setup  # → "Dashboards imported successfully!"

# 3. Kibana öffnen
# http://localhost:5601 → Hamburger Menu → Dashboard
# → "Deal Overview" und "Price Monitor" sollten sichtbar sein

# 4. Deal Dashboard hat Daten?
curl -s http://localhost:9200/keeper-deals/_count | python3 -c "import sys,json; print('Deals:', json.load(sys.stdin)['count'])"
```

### Schritt 5: FOR_SMLFLG.md dokumentieren

Neuer Abschnitt "Kibana Auto-Load Dashboards" mit Beschreibung der Dashboards und wie der Auto-Import funktioniert.

---

## Dateien

| Datei | Aktion | Beschreibung |
|-------|--------|-------------|
| `kibana/saved_objects.ndjson` | NEU | Alle Saved Objects (Data Views + Visualisierungen + Dashboards) |
| `kibana/setup-kibana.sh` | NEU | Init-Script das auf Kibana wartet und importiert |
| `docker-compose.yml` | EDIT | `kibana-setup` Service hinzufügen |
| `FOR_SMLFLG.md` | EDIT | Dashboard-Feature dokumentieren |

## Risiken

- **NDJSON-Format**: Kibana 8.11 Saved Objects haben ein spezifisches Format. Muss exakt stimmen, sonst Import-Fehler. → Wir bauen die NDJSON vorsichtig mit korrekten IDs und Referenzen.
- **Timing**: Kibana braucht ~30-60s zum Starten. Das Script wartet bis zu 5 Minuten (60 × 5s). Reicht locker.
- **Keine Daten beim ersten Start**: Dashboards sind leer wenn ES noch keine Deals hat. Das ist OK -- nach dem ersten Scheduler-Zyklus (~1h) kommen Daten rein.
