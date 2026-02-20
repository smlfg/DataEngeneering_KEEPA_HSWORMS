Übung 2 - Elasticsearch 2
1. Index Templates
1. Erstellen Sie ein Index Template:
Konfigurieren Sie ein Template, das automatisch auf alle Indizes angewendet wird,
deren Name mit logs- beginnt.
Das Template soll folgende Eigenschaften haben:
1 Primärshard und 1 Replikat.
Ein Mapping, das ein Feld timestamp als date und ein Feld
message als text definiert.
Verwenden Sie die Index Template API.
2. Validieren Sie das Template:
Erstellen Sie einen neuen Index logs-2024 und überprüfen Sie, ob das
Template korrekt angewendet wurde.

2. Rollovers
1. Erstellen Sie einen Rollover Index:
Legen Sie einen Index logs-000001 an und fügen Sie Daten hinzu.
Nutzen Sie die Rollover API um einen Rollover auf dem erstellten Index
durchzuführen.
2. Testen Sie den Rollover:
Verifizieren Sie, dass der neue Index logs-000002 erstellt wurde.
Lesen Sie zum Thema Index Lifecycle Management und beschreiben Sie kurz in
ihren eigenen Worten was ILM ist.

3. Alias
1. Alias-Konfiguration:
Erstellen Sie zwei Indizes: data-2024 und data-archive .

Fügen Sie einen Alias all-data hinzu, der beide Indizes umfasst.
Fügen Sie Dokumente zu beiden Indizes hinzu und verwenden Sie den Alias, um
alle Daten abzufragen.

4. Ingest Pipelines
1. Pipeline erstellen:
Konfigurieren Sie eine Ingest Pipeline, die:
Ein Feld timestamp aus dem JSON-Dokument in das Format
yyyy-MM-dd umwandelt.
Ein neues Feld processed_at mit dem aktuellen Timestamp hinzufügt.
Ein Feld message in Großbuchstaben umwandelt.
2. Pipeline testen:
Erstellen Sie einen Index processed-logs .
Laden Sie Dokumente über die Pipeline in den Index und überprüfen Sie die
Ergebnisse.

