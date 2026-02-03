# Data Engineering - Projekt Agenda & Abgabe

**Projekt:** Amazon Arbitrage Tracker
**Student:** Samuel
**Fach:** Data Engineering WS2025
**Letztes Update:** 2026-01-08

---

## 📋 Prüfungsleistung - Anforderungen

### 🎯 **Projektziel**
Entwicklung einer **End-to-End-Lösung** zur Erfassung, Verarbeitung und Speicherung von Daten, inklusive Beispielanalyse.

---

## 🏗️ **Die 3 Säulen des Projekts**

### **1. Scraping/Data Ingestion** ✅
- ✅ Daten müssen **periodisch** abgegriffen werden
- ⚠️ Scheduling idealerweise mit **Airflow** (oder ähnlich)
- **Mein Projekt:** Keepa API mit periodischem Polling (alle 5min)

### **2. Vorverarbeitung der Daten** ✅
- ✅ **Externe und umfangreiche** Vorverarbeitung
- **Mein Projekt:**
  - Enrichment Consumer (Keepa → normalisiert)
  - Arbitrage Detector (Margin-Berechnung)

### **3. Speicherung der Daten** ✅
- ✅ Speicherung in **sinnvoller Datenbank** für den Use Case
- ✅ **Einstellung und Optimierung** der Datenbank
- ✅ **Sinnvolles Deployment** mit entsprechenden Einstellungen
- **Mein Projekt:** Elasticsearch + Kafka

---

## 📊 **Zusätzliche Anforderungen**

### **Analyseteil** (nicht Data Engineering Kern, aber gefordert):
- ✅ Führe **Analysen** auf den verarbeiteten Daten durch
- **Optionen:**
  - Klassischer Analytics Use Case ✅ (mein Arbitrage Detection)
  - Such-Optimierung
  - Verarbeitung von Echtzeitdaten ✅ (Kafka Streaming)

---

## 📅 **Ablauf & Termine**

| Phase | Deadline | Status | Aktion |
|-------|----------|--------|--------|
| **Projektidee einreichen** | Ende Dezember 2025 | ⚠️ ÜBERFÄLLIG? | Dozent kontaktieren! |
| **Freigabe** | Nach Prüfung durch Projektleitung | ⏳ Warten | - |
| **Bearbeitungszeit** | Bis finaler Präsentationstermin (tbd) | 🔄 Läuft | Weiterarbeiten |
| **Abschlusspräsentation** | tbd (wird noch bekannt gegeben) | ⏳ Pending | Vorbereiten |

---

## 📦 **Abgabe & Bewertung - Komponenten**

### **1. Abschlusspräsentation** 🎤
- **Darstellung der getroffenen Entscheidungen**
- Warum Kafka? Warum Elasticsearch? Warum diese Architektur?
- Demo des Systems
- **TODO:** Präsentation vorbereiten (PowerPoint/Slides)

### **2. Code-Abgabe** 💻
- ✅ Muss in **zugänglichem Git Repository** vorliegen
- ✅ Vollständiger Source Code
- **Status:** ✅ Alles schon in Git (arbitrage-tracker/)

### **3. Einstellungen und Deployment** ⚙️
- ✅ **Alle Datenbank- und Deployment-Einstellungen als Code** verfügbar
- ✅ z.B. Skripte, docker-compose.yml, Elasticsearch mappings
- ❌ **Keine manuellen Änderungen** (z.B. via Kibana)
- **Status:**
  - ✅ docker-compose.yml vorhanden
  - ✅ ES Schema in docs/ definiert
  - ✅ Kafka Topics: via init-topics Service
  - ⚠️ Airflow fehlt noch (könnte kritisch sein!)

---

## ✅ **Status Check - Was ich schon habe**

| Komponente | Status | Details |
|------------|--------|---------|
| **Data Ingestion** | ✅ Complete | Producer (Keepa API) |
| **Periodisches Scraping** | ✅ Complete | Polling alle 5min |
| **Scheduling Tool** | ❌ Missing | ⚠️ Sollte Airflow sein! |
| **Vorverarbeitung** | ✅ Complete | Enrichment + Arbitrage |
| **Datenbank** | ✅ Complete | Elasticsearch optimiert |
| **Message Queue** | ✅ Complete | Kafka mit 3 Topics |
| **Deployment** | ✅ Complete | docker-compose.yml |
| **Code Repository** | ✅ Complete | Git vorhanden |
| **Analyseteil** | ✅ Complete | Arbitrage Detection |
| **Echtzeitdaten** | ✅ Complete | Kafka Streaming |
| **Tests** | ⚠️ Partial | Nur 3 Unit Tests |
| **Dokumentation** | ⚠️ Partial | Basis vorhanden |

---

## 🔴 **KRITISCHE TODOs (Sofort erledigen!)**

### **1. Projektidee offiziell einreichen** 🚨
- **Deadline:** Ende Dezember (möglicherweise schon vorbei!)
- **Action:**
  - [ ] Dozent per E-Mail kontaktieren
  - [ ] Projektbeschreibung einreichen
  - [ ] Freigabe einholen
- **Priorität:** HÖCHSTE

### **2. Airflow/Scheduling Tool hinzufügen** 🚨
- **Warum:** Folien sagen explizit "idealerweise mit Airflow"
- **Aktuell:** Producer läuft als Docker Service (suboptimal)
- **Action:**
  - [ ] Airflow zu docker-compose.yml hinzufügen
  - [ ] DAG erstellen für periodisches Scraping
  - [ ] Producer-Logik in Airflow Task migrieren
- **Priorität:** SEHR HOCH
- **Geschätzte Zeit:** 4-6 Stunden

---

## 🟡 **WICHTIGE TODOs (Diese Woche)**

### **3. Tests erweitern**
- **Aktuell:** Nur 3 Unit Tests
- **Ziel:** Mindestens 50% Coverage
- **Action:**
  - [ ] Unit Tests für alle Worker
  - [ ] Integration Tests (Kafka → ES)
  - [ ] E2E Test (kompletter Flow)
- **Priorität:** HOCH
- **Geschätzte Zeit:** 6-8 Stunden

### **4. Deployment-Dokumentation**
- **Aktuell:** README vorhanden, aber nicht detailliert genug
- **Action:**
  - [ ] DEPLOYMENT.md erstellen
  - [ ] Alle Einstellungen dokumentieren
  - [ ] Schritt-für-Schritt Anleitung
  - [ ] Troubleshooting Guide
- **Priorität:** HOCH
- **Geschätzte Zeit:** 2-3 Stunden

### **5. Präsentation vorbereiten**
- **Für:** Abschlusspräsentation
- **Action:**
  - [ ] Architektur-Diagramm erstellen
  - [ ] Entscheidungsbegründungen dokumentieren
  - [ ] Live-Demo vorbereiten
  - [ ] PowerPoint/Slides erstellen
- **Priorität:** MITTEL-HOCH
- **Geschätzte Zeit:** 4-6 Stunden

---

## 🟢 **OPTIONALE TODOs (Nice to have)**

### **6. Code Quality verbessern**
- [ ] Linting (flake8/ruff) ausführen
- [ ] Type Hints überprüfen (mypy)
- [ ] Code Complexity messen
- [ ] Docstrings vervollständigen
- **Geschätzte Zeit:** 3-4 Stunden

### **7. Monitoring hinzufügen**
- [ ] Prometheus Metriken
- [ ] Grafana Dashboard
- [ ] Alerting bei Fehlern
- **Geschätzte Zeit:** 6-8 Stunden

### **8. Performance Optimierung**
- [ ] Elasticsearch Query-Optimierung
- [ ] Kafka Tuning
- [ ] Caching-Layer (Redis?)
- **Geschätzte Zeit:** 4-6 Stunden

---

## 📊 **Aktueller Projekt-Score**

| Anforderung | Status | Score | Gewichtung |
|-------------|--------|-------|------------|
| Data Ingestion | ✅ Complete | 100% | 15% |
| Periodisches Scraping | ✅ Complete | 100% | 10% |
| Scheduling Tool (Airflow) | ❌ Missing | 0% | 15% ⚠️ |
| Vorverarbeitung | ✅ Complete | 100% | 15% |
| Datenbank-Setup | ✅ Complete | 100% | 15% |
| Deployment as Code | ✅ Complete | 90% | 10% |
| Git Repository | ✅ Complete | 100% | 5% |
| Analyseteil | ✅ Complete | 100% | 10% |
| Tests | ⚠️ Partial | 30% | 5% |
| Dokumentation | ⚠️ Partial | 70% | 5% |
| **GESAMT** | | **~78%** | |

**Einschätzung:** Mit Airflow → ~93%+ möglich! 🎯

---

## 🎯 **Priorisierter Wochenplan**

### **Woche 1 (Diese Woche):**
**Montag-Dienstag:**
- [ ] Dozent kontaktieren (Projektidee einreichen)
- [ ] Docker zum Laufen bringen
- [ ] System testen mit Test-Daten

**Mittwoch-Donnerstag:**
- [ ] Airflow hinzufügen
- [ ] DAG für Scraping erstellen
- [ ] Producer in Airflow migrieren

**Freitag-Sonntag:**
- [ ] Tests schreiben (Ziel: 50% Coverage)
- [ ] DEPLOYMENT.md erstellen

### **Woche 2:**
**Montag-Mittwoch:**
- [ ] Code aufräumen (Linting, Types)
- [ ] Dokumentation vervollständigen

**Donnerstag-Sonntag:**
- [ ] Präsentation erstellen
- [ ] Live-Demo vorbereiten
- [ ] Architektur-Diagramme

---

## 📋 **Präsentations-Vorbereitung**

### **Folien-Struktur (Vorschlag):**

**1. Intro (2 Min)**
- Projektziel
- Business Case (Arbitrage-Opportunities)

**2. Architektur (5 Min)**
- Architektur-Diagramm
- Komponenten-Übersicht
- Datenfluss

**3. Technische Entscheidungen (5 Min)**
- **Warum Kafka?**
  - Event-driven Architecture
  - Entkopplung der Services
  - At-least-once Garantien
- **Warum Elasticsearch?**
  - Full-text Search
  - Aggregationen für Analytics
  - Real-time Indexing
- **Warum Docker Compose?**
  - Reproduzierbares Environment
  - Easy Deployment
  - Service Orchestration

**4. Implementierung (5 Min)**
- 5 Worker (Producer, Consumer, Arbitrage, API, Dashboard)
- 4000+ LOC
- Poetry für Dependencies
- Kafka Topics & Message Flow

**5. Demo (5 Min)**
- Live-System zeigen
- Dashboard mit Opportunities
- Kibana (ES Queries)
- Kafka Topics anschauen

**6. Learnings & Ausblick (3 Min)**
- Was gut lief
- Herausforderungen
- Mögliche Erweiterungen

**Total: ~25 Min + 5 Min Fragen**

---

## 🎓 **Entscheidungsbegründungen (für Präsentation)**

### **Architektur-Entscheidungen:**

**1. Microservices statt Monolith**
- **Warum:** Separation of Concerns, unabhängige Skalierung
- **Vorteil:** Jeder Worker kann separat entwickelt/deployed werden

**2. Event-Driven Architecture (Kafka)**
- **Warum:** Asynchrone Verarbeitung, Resilienz
- **Vorteil:** Services müssen nicht online sein, Messages werden gepuffert

**3. Elasticsearch als Datenbank**
- **Warum:** Such-Anforderungen, Aggregationen, Real-time
- **Alternative:** PostgreSQL wäre zu langsam für Full-text Search

**4. Docker Compose statt Kubernetes**
- **Warum:** Einfacheres Setup, ausreichend für Projekt-Scope
- **Trade-off:** Weniger Production-ready, aber für Uni-Projekt okay

**5. Poetry statt pip**
- **Warum:** Besseres Dependency Management, Lock-Files
- **Vorteil:** Reproduzierbare Builds

---

## 📞 **Kontakte & Ressourcen**

### **Dozent:**
- **Name:** [TODO: Namen eintragen]
- **E-Mail:** [TODO: E-Mail eintragen]
- **Sprechstunde:** [TODO: Zeiten eintragen]

### **Nützliche Links:**
- **Kafka Docs:** https://kafka.apache.org/documentation/
- **Elasticsearch Docs:** https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- **Airflow Docs:** https://airflow.apache.org/docs/
- **Docker Compose:** https://docs.docker.com/compose/

### **Projekt-Repositories:**
- **Main Repo:** ~/Dokumente/WS2025/DataEnge/arbitrage-tracker/
- **Dokumentation:** ~/Dokumente/WS2025/DataEnge/arbitrage-tracker/MultiAgentDokumentation/

---

## ⏰ **Zeitplan bis Abgabe**

### **Kritischer Pfad:**
```
Heute (Tag 0):
└─> Dozent kontaktieren ✉️
    └─> Docker zum Laufen bringen 🐳
        └─> System testen ✅
            (2-3 Stunden)

Tag 1-2:
└─> Airflow hinzufügen 🔄
    └─> DAG erstellen
        └─> Testen
            (8-10 Stunden)

Tag 3-4:
└─> Tests schreiben 🧪
    └─> DEPLOYMENT.md
        (8-10 Stunden)

Tag 5-7:
└─> Präsentation erstellen 📊
    └─> Demo vorbereiten
        └─> Üben!
            (10-12 Stunden)

GESAMT: ~30-35 Stunden Arbeit
```

---

## 🚨 **Risikoanalyse**

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Projektidee nicht genehmigt | Mittel | Hoch | Früh beim Dozent melden |
| Airflow Integration schwierig | Mittel | Mittel | Tutorials nutzen, einfach halten |
| Docker startet nicht | Gering | Hoch | Bereits gelöst ✅ |
| Zeit reicht nicht | Mittel | Hoch | Priorisieren: Airflow > Tests > Rest |
| Demo schlägt fehl | Gering | Hoch | Mehrfach testen, Backup-Plan |

---

## ✅ **Definition of Done (für Abgabe)**

**Das Projekt ist abgabebereit wenn:**

- [ ] Projektidee vom Dozent genehmigt
- [ ] Alle 3 Säulen implementiert (Scraping, Vorverarbeitung, Speicherung)
- [ ] Airflow für Scheduling integriert
- [ ] Mindestens 50% Test Coverage
- [ ] DEPLOYMENT.md vollständig
- [ ] Code in Git Repository
- [ ] docker-compose.yml funktioniert einwandfrei
- [ ] Alle Einstellungen als Code (keine manuellen Änderungen)
- [ ] Präsentation vorbereitet (Slides + Demo)
- [ ] System läuft stabil für Demo

---

## 📝 **Notizen & offene Fragen**

### **Fragen an Dozent:**
- [ ] Ist Projektidee noch rechtzeitig? (Deadline war Ende Dez)
- [ ] Ist Airflow Pflicht oder "idealerweise"?
- [ ] Wann ist der Präsentationstermin?
- [ ] Wie lange soll die Präsentation sein?
- [ ] Git Repository: Privat oder Public?

### **Technische Fragen:**
- [ ] Keepa API Key: Kostenlos oder bezahlt?
- [ ] Wie viele Test-ASINs für Demo?
- [ ] Soll System 24/7 laufen für Demo?

---

## 🎯 **Erfolgs-Kriterien**

**Projekt ist erfolgreich wenn:**
- ✅ Note >= 1.7 (Ziel: 1.3 oder besser)
- ✅ System läuft stabil
- ✅ Demo überzeugt
- ✅ Alle Anforderungen erfüllt
- ✅ Gelernt: Kafka, Elasticsearch, Docker, Microservices

---

## 🔄 **Version History**

| Datum | Version | Änderungen |
|-------|---------|------------|
| 2026-01-08 | 1.0 | Initial Agenda erstellt |

---

**Letztes Update:** 2026-01-08 18:00
**Nächstes Review:** Nach Dozenten-Feedback
**Status:** 🟡 In Progress - Kritische TODOs pending
