# E-Mail an Professor Heyl - Projektidee Data Engineering

---

## 📧 **Option 1: Formell & Ausführlich**

**Betreff:** Projektidee für Data Engineering Prüfungsleistung - Nachträgliche Einreichung

---

Sehr geehrter Professor Heyl,

ich wende mich an Sie bezüglich der Prüfungsleistung im Modul Data Engineering (WS 2025/26).

Leider habe ich die Deadline zur Einreichung der Projektidee Ende Dezember versäumt. Ich möchte Sie bitten, meine Projektidee nachträglich zu prüfen und freizugeben.

**Projektbeschreibung:**

**Titel:** Amazon Arbitrage Price Tracker - End-to-End Data Pipeline

**Ziel:**
Entwicklung einer automatisierten End-to-End-Lösung zur Erfassung, Verarbeitung und Analyse von Produktpreisen über europäische Amazon-Marktplätze zur Identifikation von Arbitrage-Möglichkeiten.

**Die drei Säulen:**

1. **Data Ingestion / Scraping:**
   - Periodische Abfrage der Keepa API für Produktpreise
   - Überwachung von QWERTZ-Tastaturen auf amazon.de, .it, .es, .uk, .fr
   - Scheduling über Airflow DAGs (geplant)
   - Polling-Intervall: 5 Minuten

2. **Vorverarbeitung:**
   - Kafka-basierte Event-Streaming-Architektur
   - Enrichment Consumer: Normalisierung und Transformation der Rohdaten
   - Arbitrage Detector: Berechnung von Margen und Profit-Potentialen
   - Multi-Marketplace-Vergleich mit Währungsumrechnung

3. **Speicherung:**
   - Elasticsearch als primäre Datenbank
   - Optimiertes Index-Mapping für Full-Text-Search und Aggregationen
   - Kafka Topics für Event-Streaming (3 Topics: raw data, enriched data, alerts)
   - Deployment via Docker Compose mit vollständiger Infrastruktur-as-Code

**Analyseteil:**
- Real-time Arbitrage Detection (Klassischer Analytics Use Case)
- Streamlit Dashboard für Visualisierung der Opportunities
- REST API (FastAPI) für programmatischen Zugriff
- Historische Preistrend-Analysen

**Technologie-Stack:**
- Apache Kafka 7.5 (Message Queue)
- Elasticsearch 8.11 (Datenbank)
- Apache Airflow (Scheduling - in Implementierung)
- Python 3.11 (FastAPI, Streamlit)
- Docker Compose (Deployment)

**Aktueller Stand:**
Das Projekt ist bereits zu ca. 80% implementiert:
- Alle 5 Microservices entwickelt (~4000 LOC)
- Docker Compose Setup vollständig
- Kafka- und Elasticsearch-Konfigurationen als Code
- Git Repository mit vollständiger Dokumentation

**Noch ausstehend:**
- Integration von Apache Airflow für Scheduling
- Erweiterung der Test-Coverage
- Finalisierung der Deployment-Dokumentation

Ich bin mir bewusst, dass die reguläre Deadline verstrichen ist, und bitte um Verständnis für die verspätete Einreichung. Das Projekt ist bereits weit fortgeschritten und ich bin zuversichtlich, es fristgerecht zur Präsentation fertigstellen zu können.

Könnten Sie mir bitte mitteilen, ob eine nachträgliche Freigabe möglich ist und wann der finale Präsentationstermin stattfinden wird?

Für Rückfragen stehe ich Ihnen gerne zur Verfügung. Bei Bedarf kann ich Ihnen auch gerne bereits jetzt einen Einblick in den aktuellen Stand des Projekts geben.

Mit freundlichen Grüßen
Samuel

---

## 📧 **Option 2: Kompakt & Direkt**

**Betreff:** Projektidee Data Engineering - Amazon Arbitrage Tracker

---

Sehr geehrter Professor Heyl,

ich möchte meine Projektidee für die Data Engineering Prüfungsleistung nachträglich einreichen und um Freigabe bitten.

**Projekt:** Amazon Arbitrage Price Tracker

**Kurzbeschreibung:**
End-to-End Data Pipeline zur automatisierten Erfassung und Analyse von Produktpreisen über europäische Amazon-Marktplätze (DE, IT, ES, UK, FR) zur Identifikation von Arbitrage-Möglichkeiten.

**Erfüllung der Anforderungen:**
1. **Scraping:** Keepa API (periodisch, geplant via Airflow)
2. **Vorverarbeitung:** Kafka Event-Streaming + Enrichment + Arbitrage-Berechnung
3. **Speicherung:** Elasticsearch mit optimiertem Index-Mapping
4. **Analyseteil:** Real-time Arbitrage Detection + Streamlit Dashboard

**Tech-Stack:** Kafka, Elasticsearch, Airflow, FastAPI, Docker Compose, Python

**Stand:** ~80% implementiert (4000+ LOC, Git Repository, Docker Setup)

Ist eine nachträgliche Freigabe möglich? Wann ist der Präsentationstermin?

Mit freundlichen Grüßen
Samuel

---

## 📧 **Option 3: Kurz & Unkompliziert (falls ihr per Du seid)**

**Betreff:** Projektidee Data Engineering

---

Hallo Professor Heyl,

ich habe leider die Deadline für die Projektidee verpasst und möchte diese nachträglich einreichen:

**Amazon Arbitrage Price Tracker** - automatisierte Data Pipeline für Preisvergleiche über EU Amazon-Märkte.

- Scraping: Keepa API (Airflow)
- Processing: Kafka + Enrichment + Arbitrage Detection
- Storage: Elasticsearch
- Frontend: Streamlit Dashboard

Das Projekt ist schon zu ~80% fertig (4000 LOC, Docker Setup, Git Repo).

Ist eine nachträgliche Freigabe möglich?

Viele Grüße
Samuel

---

## 📎 **Optional: Anhänge/Links**

Falls du direkt Code/Doku zeigen willst:

```
**Git Repository:** [Link zu GitHub/GitLab falls vorhanden]

**Dokumentation:**
- ARCHITECTURE.md (System-Architektur)
- AGENDA.md (Projekt-Planung)
- docs/ (API Contracts, Kafka Schemas, ES Mappings)

**Aktueller Stand:**
- 22 Python-Dateien
- 5 Microservices (Producer, Consumer, Arbitrage, API, Dashboard)
- Vollständiges Docker Compose Setup
```

---

## 💡 **Empfehlung:**

Ich würde **Option 1 (Formell & Ausführlich)** empfehlen, weil:
- ✅ Zeigt dass du das Projekt ernst nimmst
- ✅ Erklärt alle 3 Säulen klar
- ✅ Zeigt dass du schon weit bist (80% fertig)
- ✅ Professionell aber nicht übertrieben

**Anpassen solltest du noch:**
- [ ] Deine E-Mail Signatur
- [ ] Eventuelle Matrikelnummer
- [ ] Falls ihr per Du seid: "Sie" → "Du" ändern

---

## ✅ **Checklist vor dem Absenden:**

- [ ] Betreff aussagekräftig?
- [ ] Rechtschreibung geprüft?
- [ ] Alle wichtigen Infos drin?
- [ ] Höflich aber nicht unterwürfig?
- [ ] Konkrete Frage am Ende? (Freigabe möglich? Termin?)
- [ ] Kontaktdaten in Signatur?

---

## 🎯 **Was du nach dem Absenden tust:**

1. ⏰ **48h warten** auf Antwort
2. 📧 Falls keine Antwort: Freundliche Erinnerung
3. ✅ Bei Freigabe: Weiter am Projekt arbeiten (Airflow!)
4. ❌ Bei Ablehnung: Nach Alternativen fragen

---

**Speicherort dieser Vorlage:**
`~/Dokumente/WS2025/DataEnge/arbitrage-tracker/EMAIL_AN_PROF_HEYL.md`
