# Was noch fehlt

## 1. Ziel dieser Datei
Diese Datei uebersetzt die Anforderungen aus `Anforderungen fuer Data Engineering.md` und den Ist-Stand aus `Stand des Projekts.md` in konkrete, priorisierte Aufgaben bis zur sicheren Pruefungsabgabe.

## 2. Gap-Matrix (Anforderung -> Luecke -> Massnahme)

| ID | Anforderung | Ist-Stand | Luecke | Konkrete Massnahme | Prioritaet | Aufwand | Abnahmekriterium |
|---|---|---|---|---|---|---|---|
| G1 | M1 End-to-End-Nachweis | Technisch vorhanden | Kein durchgaengiger Demo-Nachweis als Script/Runbook | Ein "Demo-Runbook" erstellen (Start, Datenfluss, erwartete Outputs) | P0 | S | Eine dritte Person kann den Flow ohne Rueckfragen starten |
| G2 | M4 Vorverarbeitung | Teilweise vorhanden | Deal-Scoring/Filter arbeitet mit inkonsistenten Feldnamen | Feldschema vereinheitlichen (`snake_case` vs `camelCase`) + Tests anpassen | P0 | M | Deal-Suche liefert reproduzierbar gefilterte/rankte Ergebnisse |
| G3 | M8 Einstellungen als Code | Groesstenteils vorhanden | Setup-Schritte und env-Konfiguration nicht praezise genug dokumentiert | `README` um "Quickstart + env + test + scheduler" erweitern | P0 | S | Frischer Clone laeuft mit dokumentierten Schritten |
| G4 | M10 Entscheidungen praesentieren | Teilweise | Architektur- und Trade-off-Erklaerung nicht kompakt aufbereitet | 1-seitiges Architekturblatt + 10-Minuten-Sprechskript erstellen | P0 | S | Praesentation ohne Improvisation moeglich |
| G5 | M6 DB-Optimierung | Teilweise | Optimierungsentscheidungen nicht explizit begruendet | Kurze DB-Decision-Section (Indexe, Historie, Query-Pfade, Grenzen) | P1 | S | Jede DB-Entscheidung ist fachlich begruendet |
| G6 | Betriebsqualitaet | Teilweise | Testausfuehrung in Umgebung nicht gesichert | Venv aufsetzen, Dependencies installieren, Testlauf dokumentieren | P1 | S | `pytest` laeuft und Ergebnis ist dokumentiert |
| G7 | Notification-Zuverlaessigkeit | Risiko | "success" auch ohne realen SMTP-Versand moeglich | Versandstatus semantisch korrigieren + Fallback klar kennzeichnen | P1 | M | Kein False-Positive-"versendet" mehr |
| G8 | Wahlpfad sauber begruenden | Noch offen | Unklar, ob Fokus Analytics/Suche/Echtzeit explizit genannt wird | Fokus offiziell auf "periodisches Monitoring + API-Analytics" festlegen | P1 | S | Ein Satz "Unser Pruefungspfad ist ..." in Doku + Vortrag |
| G9 | Uebungsnaehe (Elasticsearch/Kafka) | Gering | Uebungsinhalte nur indirekt im Projekt | Optional: kleines Appendix-Mapping "Welche Uebungsprinzipien wurden umgesetzt?" | P2 | M | Zusatzfolie/Abschnitt vorhanden |

## 3. Priorisierte Abarbeitung

## P0 (muss vor Abgabe fertig sein)
1. **Demo-Runbook erstellen (G1)**  
   Inhalt:
   - Voraussetzungen
   - Startkommandos
   - Testdaten anlegen
   - Erwartete API-Responses
   - Nachweis, dass Scheduler Alerts erzeugt
2. **Deal-Feldschema fixen (G2)**  
   Ziel:
   - Einheitliche Felder in Deal-Pipeline
   - Kein Informationsverlust durch Namensmismatch
3. **README/Setup reproduzierbar machen (G3)**  
   Ziel:
   - Ein neuer Rechner kann es starten
4. **Praesentationspaket erstellen (G4)**  
   Ziel:
   - Architektur, Entscheidungen, Trade-offs in 10 Minuten klar

## P1 (sollte vor Praesentation erledigt sein)
1. DB-Optimierungsbegruendung (G5)
2. Testausfuehrung stabilisieren und dokumentieren (G6)
3. Notification-Semantik verbessern (G7)
4. Wahlpfad explizit festlegen und begruenden (G8)

## P2 (nice-to-have / Bonus)
1. Explizites Mapping auf Elasticsearch-/Kafka-Uebungsinhalte (G9)
2. Kleine Zusatzanalyse oder Dashboard als Pluspunkt

## 4. 7-Tage-Abschlussplan (pruefungsorientiert)

### Tag 1: Stabiler Projektstart
- Venv/Dependencies final aufsetzen.
- System lokal oder per Docker vollstaendig starten.
- Basis-Healthchecks dokumentieren.

**DoD:** Start und Grundfunktionen sind reproduzierbar.

### Tag 2: End-to-End-Demo absichern
- Demo-Flow von Watch-Anlage bis Alert-Endpunkt durchspielen.
- Demo-Runbook schreiben.

**DoD:** Ein durchgaengiger Ablauf ist schriftlich und praktisch verifiziert.

### Tag 3: Kritischen Deal-Pfad korrigieren
- Feldnamen konsistent machen.
- Relevante Agent/API-Tests aktualisieren.

**DoD:** Deal-Suche liefert logisch konsistente Resultate.

### Tag 4: Deployment und Konfiguration haerten
- README Quickstart finalisieren.
- `.env.example` auf Vollstaendigkeit pruefen.
- Scheduler-Start und App-Start als Standardprozess festhalten.

**DoD:** Vollstaendige Betriebsanleitung ist vorhanden.

### Tag 5: Qualitaetsnachweise
- Testlauf ausfuehren und Ergebnisse festhalten.
- DB-Entscheidungen/Optimierung als Kurzkapitel dokumentieren.

**DoD:** Es gibt technische Nachweise fuer Stabilitaet und Designentscheidungen.

### Tag 6: Praesentation vorbereiten
- 10-Minuten-Storyline finalisieren.
- 5 typische Prueferfragen vorbereiten.
- Backup-Demo (Screenshots/API-Responses) erzeugen.

**DoD:** Praesentation ist probegehalten.

### Tag 7: Generalprobe und Freeze
- Vollstaendiger Durchlauf: Start -> Demo -> Vortrag.
- Letzte Fehlerkorrekturen.
- Abgabe-Checkliste final abhaken.

**DoD:** Abgabestand ist eingefroren und belastbar.

## 5. Praesentations-Checkliste (Kurzfassung)

1. Problem und Nutzen in 30 Sekunden.
2. Datenquelle und periodische Erfassung klar zeigen.
3. Vorverarbeitungsschritte konkret benennen.
4. Speicherung + Datenmodell begruenden.
5. Deployment als Code live/verifizierbar zeigen.
6. Ein reales End-to-End-Beispiel vorfuehren.
7. Grenzen und naechste Schritte ehrlich benennen.

## 6. Mindestkriterien fuer "voller Erfolg"
Das Projekt gilt als voll erfolgreich fuer die Pruefung, wenn:
1. Alle MUSS-Kriterien (M1-M10) mit Artefakten nachweisbar sind.
2. Die End-to-End-Demo ohne manuelle Sonderwege funktioniert.
3. Du jede zentrale Architekturentscheidung fachlich begruenden kannst.
4. Die praesentierte Version reproduzierbar ist (Code + Config + Deployment).
