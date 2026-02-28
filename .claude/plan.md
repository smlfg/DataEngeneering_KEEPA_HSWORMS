# Plan: Kibana Auto-Load Dashboards

## Ziel

Beim `docker-compose up` sollen 2 fertige Kibana-Dashboards automatisch geladen werden -- ohne manuelles Klicken in der Kibana UI. Beim Prüfungs-Demo: Container starten → Kibana öffnen → Dashboards sind da.

## Aktueller Stand (verifiziert)

- Kibana 8.11.0 läuft, aber **komplett leer** (keine Data Views, keine Dashboards)
- 2 ES-Indices: `keeper-prices` (10 Felder) + `keeper-deals` (16 Felder + German Stemming)
- `keeper-deals` hat Custom Analyzer `deal_analyzer` + Completion für Autocomplete
- Keine Init-Scripts, keine NDJSON-Exports vorhanden
- `docs/ELASTICSEARCH.md` beschreibt manuelle Setup-Schritte

## Architektur

```
kibana/
├── setup-kibana.sh          # Wartet auf Kibana, importiert NDJSON
└── saved_objects.ndjson     # Data Views + Visualisierungen + 2 Dashboards

docker-compose.yml
└── kibana-setup (neuer Service)  # Einmal-Job: importiert und beendet sich
```

**Warum ein Init-Service statt Volume-Mount?**
Kibana 8.x hat keinen Auto-Import-Ordner. Man muss die Saved Objects API (`/api/saved_objects/_import`) aufrufen. Ein kleiner curl-Container erledigt das.

---

## 2 Dashboards

### Dashboard 1: "Deal Overview" (`keeper-deals`)

| Panel | Typ | Konfiguration |
|-------|-----|---------------|
| Gesamt-Deals | Metric | Count of documents |
| Durchschnitts-Rabatt | Metric | avg(discount_percent) |
| Deals nach Domain | Pie Chart | Terms agg auf `domain` |
| Discount-Verteilung | Histogram | Histogram auf `discount_percent`, interval=10 |
| Deals über Zeit | Line Chart | date_histogram auf `timestamp`, interval=1d |
| Letzte 20 Deals | Data Table | title, current_price, discount_percent, domain, deal_score, sortiert nach timestamp desc |

### Dashboard 2: "Price Monitor" (`keeper-prices`)

| Panel | Typ | Konfiguration |
|-------|-----|---------------|
| Gesamt Price Events | Metric | Count of documents |
| Preisverlauf | Line Chart | date_histogram auf `timestamp`, Y=avg(current_price) |
| Events nach Domain | Pie Chart | Terms agg auf `domain` |
| Letzte 20 Preisänderungen | Data Table | asin, product_title, current_price, price_change_percent, domain |

---

## Schritte

### Schritt 1: `kibana/saved_objects.ndjson` erstellen

NDJSON-Datei mit allen Saved Objects im Kibana 8.11 Lens-Format:
1. **Data View** `keeper-deals` (timeField: timestamp)
2. **Data View** `keeper-prices` (timeField: timestamp)
3. **6 Lens-Visualisierungen** für Deal Dashboard
4. **4 Lens-Visualisierungen** für Price Dashboard
5. **Dashboard** "Deal Overview" (referenziert die 6 Panels)
6. **Dashboard** "Price Monitor" (referenziert die 4 Panels)

### Schritt 2: `kibana/setup-kibana.sh` erstellen

```bash
#!/bin/sh
KIBANA_URL="http://kibana:5601"
MAX_RETRIES=60

for i in $(seq 1 $MAX_RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KIBANA_URL/api/status")
  if [ "$STATUS" = "200" ]; then
    echo "Kibana is ready, importing dashboards..."
    curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
      -H "kbn-xsrf: true" \
      --form file=@/setup/saved_objects.ndjson
    echo ""
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

```yaml
kibana-setup:
  image: curlimages/curl:8.5.0
  depends_on:
    - kibana
  volumes:
    - ./kibana:/setup:ro
  entrypoint: ["/bin/sh", "/setup/setup-kibana.sh"]
  restart: "no"
```

Kein neuer langlebiger Container -- startet einmal, importiert, beendet sich (Exit 0).

### Schritt 4: Verifikation

```bash
docker-compose up -d
docker-compose logs -f kibana-setup  # → "Dashboards imported successfully!"
# http://localhost:5601 → Dashboard → "Deal Overview" / "Price Monitor"
```

### Schritt 5: FOR_SMLFLG.md dokumentieren

Neuer Abschnitt "Kibana Auto-Load Dashboards".

---

## Dateien

| Datei | Aktion | Beschreibung |
|-------|--------|-------------|
| `kibana/saved_objects.ndjson` | NEU | Alle Saved Objects (Data Views + Visualisierungen + Dashboards) |
| `kibana/setup-kibana.sh` | NEU | Init-Script: wartet auf Kibana, importiert NDJSON |
| `docker-compose.yml` | EDIT | `kibana-setup` Service hinzufügen |
| `FOR_SMLFLG.md` | EDIT | Dashboard-Feature dokumentieren |

## Delegation

- **NDJSON-Generierung:** OpenCode MCP (Sonnet) — das ist die komplexeste Datei, ~200 Zeilen NDJSON mit exakten Kibana 8.11 Saved Object IDs
- **setup-kibana.sh:** Direkt (triviales Shell-Script)
- **docker-compose.yml Edit:** Direkt (5 Zeilen)
- **FOR_SMLFLG.md:** Direkt

## Risiken

- **NDJSON-Format**: Kibana 8.11 Saved Objects haben ein spezifisches Format. Muss exakt stimmen → Gemini vorher nach aktuellem Format fragen
- **Timing**: Script wartet bis 5 Minuten (60 × 5s). Reicht locker.
- **Keine Daten beim ersten Start**: Dashboards sind leer bis erste Deals kommen. OK -- zeigt bei Prüfung die Struktur.
