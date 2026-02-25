# Session Log — Keeper System

---

## Session 2026-02-22 — Deep Dive: Docs, Config-Fixes, Keepa API Wahrheit, System laeuft

**Ziel:** Projekt verstehen, Docs fact-checken, Config-Probleme fixen, System zum Laufen bringen

**Erledigt:**
- [x] Alle 11 Docs gelesen + Gemini Fact-Check (16/20 Claims korrekt)
- [x] 7 Config-Probleme gefunden & gefixt (.env, docker-compose, Dockerfile, requirements.txt)
- [x] 3 "HIGH priority" Bugs aus project-deep-dive.md als FALSE POSITIVES entlarvt
- [x] Token-Sync Bug gefixt (dict vs. Dataclass Mismatch in keepa_api.py)
- [x] Retry-Logik mit Exponential Backoff in keepa_api.py eingebaut
- [x] Performance-Fix: asyncio.gather() + Semaphore(5) statt sequentielle Loops
- [x] kibana/ Ordner (setup-kibana.sh + saved_objects.ndjson) ins Repo committed
- [x] FOR_SMLFLG.md, CODE_REVIEW.md, project-deep-dive.md, PRUEFUNGSVORBEREITUNG.md aktualisiert
- [x] System-Check: 7/7 Container Up, alle Services healthy, 266/266 Tests passing

**Offene Punkte:**
- [ ] Remaining uncommitted changes (6 files: .gitignore, keepa_api.py, keepa_client.py, docker-compose.yml, scrape_amazon_asins.py, FOR_SMLFLG.md)
- [ ] KEEPA_API_LEARNINGS.md existiert aber Inhalt nicht verifiziert
- [ ] Batch-Query Optimierung (keepa_api.py queried noch einzelne ASINs, koennte 10-40er Batches)
- [ ] Keepa Starter Plan buchen ($10/Monat) — Free-Tier zu knapp fuer 500 ASINs

**Entscheidungen:**
- Redis ignorieren: War nie genutzt, Dependencies entfernt
- Scan-Intervall bei 3600s (1h) belassen: Reicht fuer Starter Plan
- FALSE POSITIVES dokumentieren statt loeschen: Wertvoll fuer Pruefungsvorbereitung ("Was sieht aus wie ein Bug, ist aber keiner?")

**Key Learnings (fuer /learn):**
- `keepa` Python Library: `api.status` ist ein Dataclass, KEIN dict — nirgends dokumentiert
- Keepa API hat 6 Endpoints, aber `/deals` gibt 404 auf Starter/Free Plan
- `discover_eu_qwertz_asins.py` beweist: Batch-Queries mit 40+ ASINs funktionieren via REST
- Docker internal Kafka Port ist 29092, external ist 9092 — .env muss den internen nutzen
- Code in `Input/` Ordner ist Referenzmaterial vom 3-Branch-Merge, wird nie importiert

**Next Steps:**
1. Restliche 6 Files committen (Quick Win #1 von vorhin)
2. `docker compose restart scheduler` nach keepa_api.py Fix testen
3. Kibana Dashboard oeffnen (localhost:5601) und Deals visuell checken
4. Pruefungsvorbereitung: FOR_SMLFLG.md durchlesen, Architektur erklaeren koennen

**Stimmung:** Starke Session — System laeuft, Bugs gefixt, Wahrheit gefunden

---

## Session 2026-02-23 — 3 Quick Wins: Mehr ASINs + Bessere Detection + Orchestrator-Run

**Ziel:** Mismatch-Detection verbessern (30% → 50%+), neue ASIN-Quellen anbinden (Bestseller + Product Finder)

**Erledigt:**
- [x] Quick Win 3: `description`/`features`-Felder in `validate_asins()` + `detect_layout()` integriert (0 Token-Kosten)
- [x] Quick Win 1: `get_bestsellers()` + `search_categories()` in `keepa_client.py` eingebaut
- [x] Quick Win 2: `product_finder()` Endpoint in `keepa_client.py` (POST mit JSON-Filtern)
- [x] Neues Script: `scripts/discover_bestseller_keyboards.py` (3-Step Discovery + Dedup + Seed-Update)
- [x] Orchestrator-Run komplett: 1,633 ASINs × 5 Domains validiert → **3,781 Records, 1,366 confirmed mismatches**
- [x] /learn Session: Alle Kernkonzepte dokumentiert (Multi-Layer Detection, Confidence Waterfall)

**Ergebnis vorher → nachher:**
- Records: 2,110 → 3,781 (+79%)
- Confirmed Mismatches: 582 → 1,366 (+135%)
- Detection-Rate: ~30% → ~46%

**Offene Punkte:**
- [ ] `discover_bestseller_keyboards.py` noch nicht gelaufen (wuerde weitere 500-3000 ASINs bringen)
- [ ] Rate Limiting brutal: 100 Errors, Run dauerte 165 min statt ~30. Batch-Size oder Delay anpassen?
- [ ] **Scope-Frage:** Aktuell nur QWERTZ-aus-DE-im-Ausland. System kann aber JEDE Richtung (AZERTY in DE, UK-Layout in FR, etc.) — `EXPECTED_LAYOUT` Dict + `classify_mismatch()` unterstuetzen das bereits. Seed-Daten und Discovery sind aber DE-fokussiert.

**Entscheidungen:**
- Quick Win 3 zuerst (0 Kosten, sofort messbar), dann 1+2 (neue Endpoints)
- `detect_layout_title` umbenannt zu `detect_layout_text` (semantisch korrekt, prueft jetzt mehr als Titel)
- Batch-Size bei 50 ASINs belassen — war aggressiv genug fuer 429er, aber Retry fing es auf

**Samuels Scope-Frage (wichtig fuer naechste Session):**
Aktuell: QWERTZ-Keyboards die auf .co.uk/.fr/.it/.es verkauft werden → Mismatch weil falsches Layout fuer den Markt. Das System KANN aber bidirektional: AZERTY auf .de, UK-Layout auf .it, etc. Technisch muesste man: (1) AZERTY/UK/IT/ES Seed-ASINs sammeln, (2) Discovery-Scripts pro Layout-Typ laufen lassen, (3) `classify_mismatch()` arbeitet schon bidirektional — jedes detected_layout ≠ expected_layout ist ein Mismatch. Skalierung: Eine DB (Postgres ist da) mit Layout-Tag pro ASIN, dann Cross-Market-Query statt CSV-Flatfiles.

**Next Steps:**
1. Rate-Limiting-Strategie verbessern (laengerer Sleep zwischen Batches ODER kleinere Batches)
2. `discover_bestseller_keyboards.py` ausfuehren wenn Token-Budget erholt
3. Scope-Entscheidung: Bei QWERTZ bleiben oder Multi-Layout-Discovery aufbauen?
4. Ergebnisse in Postgres/ES laden statt nur CSV (fuer Kibana-Dashboards)

**Stimmung:** Produktive Session — Detection-Rate fast verdoppelt, System skaliert

---

## Session 2026-02-23 — Over-Engineering Audit + Abgabe-Repo mit 30 Einzelcommits

**Ziel:** Ehrliches Audit des Projekts + abgabefertiges GitHub-Repo erstellen

**Erledigt:**
- [x] Over-Engineering Audit geschrieben (docs/OVER_ENGINEERING_AUDIT.md) — was zu viel ist, was okay ist, Framing fuer Prof
- [x] Einmal-Scripts nach scripts/archive/ verschoben (4 Dateien, ~2500 LOC aus dem Blickfeld)
- [x] Unnoetige Docs nach docs/archive/ verschoben (4 Dateien)
- [x] docs/INDEX.md aktualisiert mit Archive-Sektion
- [x] Neues Repo geklont: KeepaArbitrage_DataEngeneering_HS-WORMS_SamuelFLG-ClaudeCode
- [x] 30 Einzelcommits — jede Datei mit beschreibender Message ("Was tut diese Datei?")
- [x] Git push + Tag v1.0-abgabe gesetzt
- [x] Samuel hat Git gelernt: clone, add, commit, push, tag, log

**Entscheidungen:**
- Neues Repo statt altes reparieren: Sauberer, kein force-push noetig
- Prompts-Ordner NICHT gepusht: Agent-Prompts waren Vibe-Coding-Artefakt, nie genutzt
- Keine Code-Aenderungen vor Pruefung: Funktioniert > perfekt, Risiko vermeiden

**Offene Punkte:**
- [ ] Docker-Check (alle 8 Container hochfahren + Health Checks) — optional aber empfohlen
- [ ] Tests im neuen Repo ausfuehren (sollten 266 passed sein)

**Next Steps:**
1. Optional: `cd ~/abgabe && docker compose up -d` + Health Checks
2. Pruefungsvorbereitung: PRUEFUNGSVORBEREITUNG.md + OVER_ENGINEERING_AUDIT.md durchlesen
3. "Ist das nicht zu viel?" Antwort vorbereiten (Framing: ambitioniert, nicht over-engineered)

**Stimmung:** Starke Session — Projekt abgabefertig, Git gelernt, ehrliche Reflexion

---

## Session 2026-02-25 — PriceCheck-Ausfall diagnostiziert & Nightwatch gefixt

**Ziel:** PriceCheck-System (seit 22.02 down) diagnostizieren und reparieren, Nightwatch-Monitoring fixen

**Erledigt:**
- [x] Container-Autopsie: Alle 7/8 Services bereits online (jemand hat sie vor ~25h hochgefahren)
- [x] Scheduler laeuft: 31 PriceChecks erfolgreich, 10 Price Changes, Daten in Kafka+ES
- [x] `05_token_budget.sh` gefixt: Token-Parser las `keepa_tokens.tokens_available` (existiert nicht), jetzt top-level `tokens_available` → "200" statt "?"
- [x] `01_deal_collector_health.sh` gefixt: `--format json` nicht supported in docker-compose v1, jetzt `grep "up"` → "running" statt "unknown"
- [x] `10_morning_report.sh` 5 Bugs gefixt: Container-Count (7/5→7/8), Stats-Duplikat, Error-Count "0\n0", Kafka-Status, Keepa API false-positive
- [x] Dead-Man's-Switch eingebaut: Warnung wenn Health-Log >12h alt (haette den 40h-Ausfall erkannt)

**Offene Punkte:**
- [ ] `test_run.log` enthaelt Keepa API Key in Klartext-URLs — .gitignore pruefen
- [ ] `src/scheduler.py` Z.283-301: breites `except Exception` verschluckt Fehler (niedrig)
- [ ] Scheduler wurde SIGKILL(137) — Ursache unklar, restart: unless-stopped greift aber

**Entscheidungen:**
- Kein Code-Rebuild noetig: Container waren schon online, nur Monitoring war blind
- docker-compose v1 (1.29.2) bleibt: Kein Upgrade noetig, Scripts angepasst

**Next Steps:**
1. .gitignore pruefen ob test_run.log ausgeschlossen ist
2. Nightwatch-Crons verifizieren (crontab -l) ob alle 10 Jobs laufen
3. Morgen MORNING_REPORT.md checken — sollte jetzt saubere Zahlen zeigen

**Stimmung:** Guter Diagnostik-Tag — System lief schon, Monitoring war das eigentliche Problem

---

## Session 2026-02-25 — Doc-Update nach PriceCheck-Outage + Projekt-Healthcheck

**Ziel:** 6 Aenderungen der Outage-Session (keeper-metrics, systemd→Docker, Watchdog, _ensure_connections, Token-Metriken, Kibana) in alle Docs nachziehen

**Erledigt:**
- [x] FOR_SMLFLG.md: 11 Edits (Summary, 3 Indices, Docker-only, saved objects 14→29, ASCII-Diagramme)
- [x] ARCHITECTURE.md: 4 Edits (keeper-metrics im Diagramm, 4 Dashboards, _ensure_connections)
- [x] ELASTICSEARCH.md: 5 Edits (neue keeper-metrics Sektion, Mapping, Methoden-Tabelle, Datenfluss)
- [x] KEEPA_API.md: Neue Sektion "Token Metrics (Observability)" mit _log_token_metric() Doku
- [x] PIPELINE_FLOW.md: 5 Edits (keepa-deals→keeper-deals Fix, Phase 0b, Phase 7, Arbitrage korrigiert)
- [x] Test gefixt: `test_creates_indices_when_not_existing` assert 2→3 (keeper-metrics Index)
- [x] Projekt-Healthcheck: 7/7 Container Up, 3 ES-Indices green, 292/292 Tests, API healthy

**Entscheidungen:**
- keepa-arbitrage existiert nicht als ES-Index → Pipeline-Flow-Doku korrigiert (in-memory + log)
- Alter `keepa-deals` Index (1758 Docs, systemd-Zombie) noch nicht geloescht — User-Entscheidung

**Next Steps:**
1. Optional: `keepa-deals` Zombie-Index loeschen (`curl -X DELETE localhost:9200/keepa-deals`)
2. Optional: PydanticDeprecatedSince20 Warning fixen (ConfigDict statt class Config)
3. Uncommitted Changes committen (25 Files, +1140/-6685 Lines)

**Stimmung:** Saubere Maintenance-Session — Docs aktuell, Tests gruen, System healthy
