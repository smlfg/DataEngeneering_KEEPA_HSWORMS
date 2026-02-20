<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Ich habe Keepa API zugang

was kann ich damit machen

gib 5 Idee vorschläge

Perfekt! Mit der Keepa API hast du Zugriff auf eine massive Datenbank mit über 5 Milliarden Amazon-Produkten. Hier sind **5 konkrete Ideen**, die du mit der API realisieren kannst:

***

## **5 praktische Ideen für deine Keepa API**

### **1️⃣ Automatischer Preis-Monitoring-Bot**

**Was du machst:** Du erstellst ein Programm, das kontinuierlich Produkte überwacht und dich benachrichtigt, wenn Preise unter einen bestimmten Wert fallen.

**Warum das funktioniert:** Die API liefert Preisverlaufsdaten in Echtzeit. Du könntest z.B. automatisch überprüfen, ob eine Playstation unter €350 sinkt.

**Das Prinzip dahinter:** APIs ermöglichen "automatisierte Abfragen" – statt manuell die Website zu besuchen, fragst du die Daten programmgesteuert ab und reagierst automatisch.

***

### **2️⃣ Profitable Produkte für Amazon-Reselling finden**

**Was du machst:** Ein Tool, das Kategorie nach den besten Verkäufern durchsucht, analysiert, welche Produkte stabile Preise \& hohe Verkaufsranks haben.

**Warum das funktioniert:** Mit der API kannst du auf Bestseller-Listen, Verkaufsrang und Preistrends zugreifen – genau das, was du für Arbitrage brauchst.

**Das Prinzip dahinter:** Die API speichert Verkaufshistorie (Sales Rank). Wenn ein Produkt über Monate hinweg gute Ränge hält, ist es konsistent nachgefragt.

***

### **3️⃣ Automatisiertes Dashboard / Verkäufer-Cockpit**

**Was du machst:** Du integrierst Keepa-Daten in dein eigenes Dashboard (z.B. mit Google Sheets, Notion oder einer Web-App).

**Warum das funktioniert:** Die API liefert alle Daten strukturiert – Preisverlauf, Lagerbestände, Anzahl Konkurrenten. Das kannst du alles automatisch visualisieren.

**Das Prinzip dahinter:** Statt 10 Browser-Tabs offen zu haben, bekommst du alles an einer Stelle. Das spart Zeit und Fehler beim manuellen Tracken.

***

### **4️⃣ Wettbewerbsanalyse-Tool für deine Amazon-Nische**

**Was du machst:** Automatisch alle Konkurrenzprodukte in deiner Kategorie tracken: Preise, Bewertungen, Verkaufsränge, wann Amazon selbst Lagerbestand hat.

**Warum das funktioniert:** Die API zeigt, wann Amazon OUT OF STOCK geht – genau dann kannst du deine Preise erhöhen!

**Das Prinzip dahinter:** Wenn Amazon nicht liefert, gibt es weniger Konkurrenz. Das ist eine große Chance für höhere Margen – und Keepa zeigt dir genau diese Momente.

***

### **5️⃣ Lead-Generator für Schnäppchenjäger (Arbitrage-Tool)**

**Was du machst:** Ein Bot, der täglich die besten Deals findet (z.B. Produkte mit >30% Preisrückgang in den letzten 7 Tagen) und diese per E-Mail / Telegram versendet.

**Warum das funktioniert:** Keepa hat historische Daten – du kannst mit der `deals()`-Funktion der API aktuelle Preisstürze abfragen und filtern.

**Das Prinzip dahinter:** Schnäppchen entstehen, wenn Preise fallen. Mit programmierter Automatisierung findest du diese bevor sie jeder andere sieht – das ist der Vorteil der API gegenüber manueller Recherche.

***

## **💡 Dein Lerntipp zum Behalten:**

Die **Keepa API ist keine Magie** – denk daran: Eine API ist nur ein strukturierter Weg, um Daten zu fragen. Statt "Ich öffne Keepa.com und schaue per Hand nach Daten" fragst du das Programm automatisiert: *"Gib mir alle Daten für diese ASIN!"*

**Merkhilfe:** **API = Automatisierter Pizzabestellung ähnlich** 🍕

- Ohne API: Du gehst zur Pizzeria hin, wartest, sprichst mit dem Verkäufer
- Mit API: Du schickst eine SMS ("2x Margherita"), und die Bestellung kommt automatisch verarbeitet

Das Geheimnis: Wähle eine Idee aus, die **dein Problem löst** (z.B. "Ich brauche jeden Tag neue Deals"). Dann bist du automatisch motiviert, sie zu bauen – und du wirst sie nicht vergessen, weil sie einen echten Nutzen hat! 🎯

Was interessiert dich am meisten – eher technisch oder Business-orientiert?
<span style="display:none">[^1_1][^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_2][^1_3][^1_4][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.campixx.de/tool/amazon/keepa/

[^1_2]: https://keepaapi.readthedocs.io/en/stable/api_methods.html

[^1_3]: https://happyarbitrage.de/hbb-tutorial/

[^1_4]: https://keepaapi.readthedocs.io/en/latest/api_methods.html

[^1_5]: https://www.sellerassistant.app/blog/keepa-amazon

[^1_6]: https://www.loewenstark.com/wissen/online-marketing-tools/keepa/

[^1_7]: https://jordiob.com/amazon-tools/de/product/keepa/

[^1_8]: https://www.youtube.com/watch?v=rx6p0pFqjSk

[^1_9]: https://www.onmacon.de/news/amazon-wettbewerbsanalysen-mit-keepa-so-nutzt-du-das-tool-strategisch

[^1_10]: https://mixedanalytics.com/knowledge-base/import-keepa-data-to-google-sheets/

[^1_11]: https://keepaapi.readthedocs.io/en/latest/index.html

[^1_12]: https://www.youtube.com/watch?v=Y-JdWfUHZgg

[^1_13]: https://keepa.com

[^1_14]: https://onlinesellingexperiment.com/how-to-use-keepa/

[^1_15]: https://www.reddit.com/r/Flipping/comments/bojh18/api_for_comparing_amazon_and_ebay_prices/


---

# arbeite Idee 1 und 5 aus

Perfekt! Hier sind die beiden Ideen mit konkreten **Schritt-für-Schritt-Implementierungen** und echtem Code:

***

# **IDEE 1: Automatischer Preis-Alert Bot** 🚨

## **Was genau passiert?**

Dein Bot überwacht regelmäßig Produkte und sendet dir **sofort eine Benachrichtigung**, wenn der Preis unter dein Zielbudget fällt.

**Das Prinzip dahinter:**
Der Bot läuft kontinuierlich (z.B. alle 2 Stunden) und vergleicht: *"Was ist der AKTUELLE Preis? < Mein Zielbudget?"* → Wenn ja, Alert absenden!

***

## **🔧 Minimalistische Implementierung (Python)**

```python
import keepa
import time
from datetime import datetime

# 1. API Verbindung aufbauen
accesskey = 'YOUR_KEEPA_API_KEY'  # Hier dein Key einfügen
api = keepa.Keepa(accesskey)

# 2. Deine Überwachungsliste definieren
watch_products = [
    {
        'asin': 'B0088PUEPK',           # Beispiel: Western Digital Festplatte
        'target_price': 45.00,           # Maximal €45
        'product_name': 'WD Festplatte'
    },
    {
        'asin': 'B07VYRFV29',           # Beispiel: Monitor
        'target_price': 200.00,
        'product_name': 'Gaming Monitor'
    }
]

# 3. Alert-Funktion (sende Benachrichtigung)
def send_alert(product_name, current_price, target_price):
    """
    In echter Version: E-Mail, Telegram oder Discord
    Hier: Einfach ausdrucken
    """
    message = f"""
    🎉 PREIS ALERT! 🎉
    Produkt: {product_name}
    Aktueller Preis: ${current_price}
    Dein Zielpreis: ${target_price}
    Ersparnis: ${target_price - current_price}
    Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    print(message)
    # TODO: Email / Telegram / Discord API hier aufrufen

# 4. Hauptschleife - läuft immer wieder
def monitor_prices():
    while True:
        for product in watch_products:
            try:
                # Daten von Keepa abrufen
                result = api.query(product['asin'])
                
                if result:
                    product_data = result[^2_0]
                    
                    # Aktuellen Preis extrahieren (Buy Box Price)
                    # stats['current'] = [neupreis, 3p_neupreis, ...]
                    # Index [^2_10] = Buy Box Preis
                    price_cents = product_data['stats']['current'][^2_10]
                    
                    if price_cents > 0:
                        current_price = price_cents / 100  # Umwandlung: Cents → Dollar
                        
                        # Vergleichen: Ist der aktuelle Preis UNTER Zielbudget?
                        if current_price < product['target_price']:
                            send_alert(
                                product['product_name'],
                                current_price,
                                product['target_price']
                            )
                    
                    print(f"✓ {product['product_name']}: ${current_price:.2f}")
                
            except Exception as e:
                print(f"❌ Fehler bei {product['product_name']}: {str(e)}")
        
        # Warte 2 Stunden vor nächster Abfrage
        print("⏳ Warte 2 Stunden bis zur nächsten Prüfung...\n")
        time.sleep(7200)  # 7200 Sekunden = 2 Stunden

# 5. Starte den Bot
if __name__ == "__main__":
    print("🤖 Preis-Monitor startet...\n")
    monitor_prices()
```


***

## **⚡ Mit Telegram-Alert (Besser!)**

Statt nur auszudrucken, bekommst du **echte Pushmeldungen**:

```python
import keepa
import time
import requests
from datetime import datetime

accesskey = 'YOUR_KEEPA_API_KEY'
api = keepa.Keepa(accesskey)

# Telegram Setup
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

watch_products = [
    {'asin': 'B0088PUEPK', 'target_price': 45.00, 'name': 'WD Festplatte'}
]

def send_telegram_alert(product_name, current_price, target_price):
    """Sendet Alert per Telegram-Message"""
    message = f"""
🚨 PREIS-ALARM! 🚨

📦 {product_name}
💰 Aktueller Preis: €{current_price:.2f}
🎯 Dein Ziel: €{target_price:.2f}
💵 Du sparst: €{target_price - current_price:.2f}

⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, data=data)
    return response.status_code == 200

def monitor_prices():
    while True:
        for product in watch_products:
            try:
                result = api.query(product['asin'])
                product_data = result[^2_0]
                
                price_cents = product_data['stats']['current'][^2_10]
                if price_cents > 0:
                    current_price = price_cents / 100
                    
                    if current_price < product['target_price']:
                        send_telegram_alert(
                            product['name'],
                            current_price,
                            product['target_price']
                        )
                
                print(f"✓ {product['name']}: €{current_price:.2f}")
                
            except Exception as e:
                print(f"❌ Fehler: {e}")
        
        print("⏳ Nächste Prüfung in 2 Stunden...\n")
        time.sleep(7200)

if __name__ == "__main__":
    monitor_prices()
```


***

# **IDEE 5: Schnäppchen-Generator (Deal-Finder Bot)** 🎁

## **Was genau passiert?**

Dein Bot sucht **automatisch nach den besten Deals** – Produkte, deren Preis in den letzten X Tagen signifikant gefallen ist. Perfekt für Reselling!

**Das Prinzip dahinter:**
Die API hat die Funktion `deals()` – sie gibt dir alle Produkte zurück, die aktuelle Preisveränderungen hatten. Du filterst dann nach Kriterien wie:

- Preisabfall > 20%
- Verkaufsrang < 100.000 (beliebt)
- Bewertung > 4.0 Sterne

***

## **🔧 Deal-Finder Implementation**

```python
import keepa
import json
from datetime import datetime

accesskey = 'YOUR_KEEPA_API_KEY'
api = keepa.Keepa(accesskey)

def find_best_deals():
    """
    Sucht nach den besten Deals mit erweiterten Filtern
    """
    
    # Filter-Kriterien definieren
    deal_params = {
        "page": 0,                              # Erste 150 Deals
        "domainId": 1,                          # 1 = Amazon.com, 3 = Amazon.de
        
        # Kategorien (optional)
        "includeCategories": [^2_16310101],        # z.B. Books-Kategorie
        
        # Preisfilter
        "priceTypes": [^2_0],                      # 0 = Buy Box Preis
        "currentRange": [0, 100],               # Preis zwischen $0-$100
        
        # WICHTIG: Preisabfall (in %)
        "deltaPercentRange": [-50, -20],        # 20-50% Preisrückgang
        
        # Verkaufsrang (niedrig = beliebter)
        "salesRankRange": [0, 100000],          # Top 100.000 Produkte
        
        # Mindestbewertung
        "minRating": 4,                         # Min. 4.0 Sterne
        
        # Nur Produkte mit echten Bewertungen
        "hasReviews": True,
        
        # Sortierung: Nach größtem Preisrückgang
        "sortType": 1                           # 1 = Nach Preis absteigend
    }
    
    try:
        # API-Abfrage starten
        deals = api.deals(deal_params)
        
        print(f"🎯 Gefundene Deals: {len(deals['dr'])}\n")
        print("="*70)
        
        # Jeden Deal durchgehen und anzeigen
        for idx, deal in enumerate(deals['dr'][:10], 1):  # Top 10 anzeigen
            asin = deal.get('asin', 'N/A')
            title = deal.get('title', 'N/A')[:50]  # Erste 50 Zeichen
            
            # Preis extrahieren
            current_price = deal.get('current', [^2_0])[^2_0] / 100
            
            # Preisabfall berechnen
            price_drop_percent = deal.get('deltaPercent', [^2_0])[^2_0]  # in %
            
            # Verkaufsrang
            sales_rank = deal.get('sales_rank', [^2_999999])[^2_0]
            
            # Bewertung
            rating = deal.get('rating', [^2_0])[^2_0] / 10
            
            # Anzahl Bewertungen
            review_count = deal.get('reviewCount', 0)
            
            print(f"\n#{idx} 📦 {title}")
            print(f"   ASIN: {asin}")
            print(f"   💰 Preis: €{current_price:.2f}")
            print(f"   📉 Preisrückgang: {price_drop_percent}%")
            print(f"   ⭐ Bewertung: {rating}/5 ({review_count} Bewertungen)")
            print(f"   📊 Verkaufsrang: #{sales_rank}")
            print(f"   🔗 Amazon-Link: https://amazon.de/dp/{asin}")
        
        return deals
        
    except Exception as e:
        print(f"❌ Fehler bei Deal-Suche: {str(e)}")
        return None

# Mit Kategorien-Filter
def find_deals_by_category(category_id, min_drop_percent=-50, max_price=100):
    """
    Suche Deals in einer spezifischen Kategorie
    """
    
    deal_params = {
        "page": 0,
        "domainId": 1,
        "includeCategories": [category_id],
        "deltaPercentRange": [min_drop_percent, -15],  # Mind. 15% Abfall
        "currentRange": [0, max_price],
        "hasReviews": True,
        "minRating": 4,
        "sortType": 1
    }
    
    deals = api.deals(deal_params)
    return deals

# Beispiel: Deals nur in Electronics
def find_electronics_deals():
    """
    Elektronik-Kategorie: 16142011
    """
    electronics_category = 16142011
    deals = find_deals_by_category(electronics_category, min_drop_percent=-40, max_price=500)
    
    if deals:
        print(f"\n💻 {len(deals['dr'])} Electronics-Deals gefunden!")
        for deal in deals['dr'][:5]:
            print(f"   - {deal.get('title', 'N/A')[:40]} | "
                  f"€{deal.get('current', [^2_0])[^2_0] / 100:.2f}")

if __name__ == "__main__":
    print("🚀 Starten Deal-Suche...\n")
    find_best_deals()
    print("\n" + "="*70)
    find_electronics_deals()
```


***

## **📊 Für tägliche E-Mail-Zusammenfassung:**

```python
import keepa
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

accesskey = 'YOUR_KEEPA_API_KEY'
api = keepa.Keepa(accesskey)

def send_daily_deals_email(recipient_email):
    """
    Täglicher Deal-Report per E-Mail
    """
    
    # Deals abrufen
    deal_params = {
        "deltaPercentRange": [-50, -20],
        "currentRange": [0, 200],
        "hasReviews": True,
        "minRating": 4,
        "sortType": 1
    }
    
    deals = api.deals(deal_params)
    top_deals = deals['dr'][:15]  # Top 15
    
    # E-Mail zusammenstellen
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>🎁 Tägliche Deal-Zusammenfassung</h1>
            <p>{datetime.now().strftime('%d.%m.%Y')}</p>
            <table border="1" cellpadding="10">
                <tr>
                    <th>Rang</th>
                    <th>Produkt</th>
                    <th>Preis</th>
                    <th>Abfall</th>
                    <th>⭐ Rating</th>
                </tr>
    """
    
    for idx, deal in enumerate(top_deals, 1):
        html_content += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{deal.get('title', 'N/A')[:40]}</td>
                    <td>€{deal.get('current', [^2_0])[^2_0] / 100:.2f}</td>
                    <td>{deal.get('deltaPercent', [^2_0])[^2_0]}%</td>
                    <td>{deal.get('rating', [^2_0])[^2_0] / 10:.1f}/5</td>
                </tr>
        """
    
    html_content += """
            </table>
        </body>
    </html>
    """
    
    # E-Mail versenden (SMTP)
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Gmail App Password
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🎁 Daily Deals Report - {datetime.now().strftime('%d.%m.%Y')}"
    message["From"] = sender_email
    message["To"] = recipient_email
    
    message.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("✅ Deal-Email versendet!")
    except Exception as e:
        print(f"❌ Fehler beim Email-Versand: {e}")

if __name__ == "__main__":
    send_daily_deals_email("your_email@example.com")
```


***

# **💡 Lern- und Implementierungstipps**

## **Warum diese Struktur funktioniert:**

| Konzept | Was passiert | Warum wichtig |
| :-- | :-- | :-- |
| **API Calls** | Keepa antwortet mit JSON-Daten | Du fragst nur ab, was du brauchst (kostet Credits) |
| **Preis Extraction** | `stats['current'][^2_10]` = Buy Box Preis | Keepa speichert 15+ verschiedene Preise pro Produkt |
| **Schleifen** | `while True:` + `time.sleep()` | Bot läuft unbegrenzt und prüft regelmäßig |
| **Filter** | `deltaPercentRange`, `currentRange` | Begrenzt API-Kosten + bessere Ergebnisse |


***

## **🎯 Praktischer Starttipp zum Behalten:**

**Memory-Trick: "API-KIT" merken:**

- **A** = Access (API Key eingeben)
- **P** = Parameters (Filter setzen: Preis, Kategorie, Rabatt)
- **I** = Iterate (Schleife: immer wieder abfragen)
- **K** = Key Extrahieren (Wichtige Daten rausziehen: Preis, ASIN, Rating)
- **I** = If-Bedingung (Wenn Preis < Ziel → Alert!)
- **T** = Tell (Benachrichtigung senden: Mail, Telegram, Discord)

**Startreihenfolge für dich:**

1. **Woche 1:** Idea 1 ohne Telegram (einfaches Print)
2. **Woche 2:** Telegram-Integration hinzufügen (echte Alerts!)
3. **Woche 3:** Idea 5 mit Deal-Finder bauen
4. **Woche 4:** Email-Report kombinieren

Warum diese Reihenfolge? Jede Woche baust du **eine neue Skill** (Loop → API Response extrahieren → Alert-Service → Filtering). Das ist langsameres, tieferes Lernen, das wirklich bleibt!

Welche Idee möchtest du **diese Woche zuerst implementieren**? 🚀
<span style="display:none">[^2_1][^2_11][^2_12][^2_13][^2_14][^2_15][^2_2][^2_3][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://keepaapi.readthedocs.io/en/latest/index.html

[^2_2]: https://www.reddit.com/r/DoneDirtCheap/comments/124mdnh/create_a_bot_that_alerts_me_when_there_is_a_new/

[^2_3]: https://www.youtube.com/watch?v=ccfcH9hN8lc

[^2_4]: https://keepaapi.readthedocs.io/en/latest/api_methods.html

[^2_5]: https://ruclips.net/video/OWxOhLlXdwg/build-an-amazon-price-tracker-with-keepa-n8n-telegram-no-code-diy-tutorial.html

[^2_6]: https://onlinesellingexperiment.com/how-to-use-keepa/

[^2_7]: https://pypi.org/project/keepa/

[^2_8]: https://www.youtube.com/watch?v=OWxOhLlXdwg

[^2_9]: https://talloakadvisors.com/11-keepa-product-finder-hacks-for-profitable-amazon-sourcing/

[^2_10]: https://shop.hgs.app/blogs/lms/using-python-to-work-with-the-keepa-api-to-automate-mysql-database-ingestion-for-power-bi

[^2_11]: https://www.upwork.com/services/product/development-it-a-discord-bot-that-utilizes-the-keepa-api-for-amazon-product-tracking-1697963100324024320

[^2_12]: https://www.sellerassistant.app/blog/keepa-amazon

[^2_13]: https://github.com/ukrexpo/keepa/blob/master/keepa.py

[^2_14]: https://www.youtube.com/watch?v=o4qz0KPC_aI

[^2_15]: https://lukas-juergensmeier.com/keepar.html


---

# Okay,

bitte nur die Idee aus arbeiten kein code.

von Requirments Engeneering
über softwarearchitektur
über Software Engeernering

dann jeweis einen Ausgeabreiteten systemprompt für einen Coding Agent mit SubAgents

Ausgezeichnet! Ich erstelle dir jetzt eine **vollständige Systemanalyse** der beiden Ideen (Idee 1 \& 5) ohne Code. Lass mich diese in drei Phasen strukturieren:

***

# **📋 PHASE 1: REQUIREMENTS ENGINEERING**

## **IDEE 1: Automatischer Preis-Alert Bot**

### **1.1 Funktionale Anforderungen (Was muss das System tun?)**

| Nr. | Anforderung | Beschreibung | Priorität |
| :-- | :-- | :-- | :-- |
| **FR-1** | Produktüberwachung | System muss ASINs (Amazon-Produkt-IDs) speichern und kontinuierlich überwachen | **MUST** |
| **FR-2** | Preis-Abfrage | API-Abfragen an Keepa durchführen und aktuellen Preis extrahieren | **MUST** |
| **FR-3** | Preisvergleich | Aktuellen Preis mit Zielbudget vergleichen | **MUST** |
| **FR-4** | Benachrichtigung | Alert via E-Mail/Telegram/Discord senden, wenn Preis < Zielbudget | **MUST** |
| **FR-5** | Verwaltungsoberfläche | Benutzer kann ASINs hinzufügen/löschen und Zielpreise setzen | **SHOULD** |
| **FR-6** | Preisverlauf | Historische Preisentwicklung für überwachte Produkte speichern | **SHOULD** |
| **FR-7** | Alerts deaktivieren | Benutzer kann Überwachung pausieren/stoppen | **SHOULD** |

### **1.2 Nicht-funktionale Anforderungen (Wie soll das System sein?)**

| Kategorie | Anforderung | Kriterium |
| :-- | :-- | :-- |
| **Performance** | API-Response Zeit | < 2 Sekunden pro Produkt |
| **Zuverlässigkeit** | Uptime | 99%+ (automatische Fehlerbehandlung) |
| **Skalierbarkeit** | Max. Produkte | Mindestens 1000 ASINs parallel überwachen |
| **Sicherheit** | API-Keys | Verschlüsselt speichern, nicht hardcoded |
| **Sicherheit** | Daten | Benutzer-Daten DSGVO-konform (v.a. in DE) |
| **Verfügbarkeit** | Fehlertoleranz | Wenn Keepa API ausfällt → Auto-Retry mit Exponential Backoff |
| **Usability** | Konfiguration | Setup in < 5 Minuten möglich |

### **1.3 Stakeholder \& Personas**

```
👤 PRIMARY USER: "Budget-Maximierer Marcus"
├─ Ziel: Best Price auf Wunschlisten finden
├─ Verhalten: Checkt täglich 20-30 Produkte
├─ Schmerz: Manuelle Checks sind zeitraubend
└─ Lösung erfüllt: Automatisierung + tägliche Alerts

👤 SECONDARY USER: "Amazon-Seller Sasha"
├─ Ziel: Konkurrenzprodukte monitoren
├─ Verhalten: Baut Geschäftsstrategie auf Preisdata auf
└─ Lösung erfüllt: Strukturierte Daten + historische Trends

👤 TERTIARY: "DevOps-Engineer Daniel"
├─ Ziel: System stable halten
└─ Anforderung: Logging, Monitoring, Auto-Healing
```


### **1.4 Use Cases (Szenarien)**

**Use Case 1: "Primärer Flow"**

```
ACTOR: Marcus (Benutzer)
PRECONDITION: Marcus hat API-Key konfiguriert

1. Marcus öffnet Dashboard
2. Klickt "Neues Produkt hinzufügen"
3. Gibt ASIN (z.B. "B0088PUEPK") + Zielpreis (€45)
4. System speichert & startet Überwachung
5. Alle 2 Stunden: Keepa API abfragen
6. Wenn Preis ≤ €45 → Telegram-Alert senden
7. Marcus klickt Alert-Link → Amazon-Seite öffnet sich

POST-CONDITION: Marcus wurde benachrichtigt, kann kaufen
```

**Use Case 2: "Fehlerfall"**

```
PRECONDITION: API-Key abgelaufen

1. Bot versucht Keepa-Abfrage
2. HTTP 401 Unauthorized zurück
3. System loggt Fehler
4. Retry nach 30 min mit exponentiellem Backoff
5. Nach 3 Versuchen: Alert an Admin ("API-Key prüfen")

POST-CONDITION: System bleibt stabil, kein Crash
```


***

## **IDEE 5: Schnäppchen-Generator (Deal-Finder Bot)**

### **5.1 Funktionale Anforderungen**

| Nr. | Anforderung | Beschreibung | Priorität |
| :-- | :-- | :-- | :-- |
| **FR-1** | Deal-Suche | Keepa `deals()`-API filtern nach Preisabfall % | **MUST** |
| **FR-2** | Kategorienfilter | Nutzer wählt spezifische Kategorien (z.B. Elektronik) | **MUST** |
| **FR-3** | Preisbereichfilter | Min./Max. Preis definieren | **MUST** |
| **FR-4** | Rating-Filter | Nur Produkte mit > 4.0 Sternen anzeigen | **MUST** |
| **FR-5** | Ranking-Filter | Sales Rank < X (z.B. Top 50.000) | **MUST** |
| **FR-6** | Täglicher Report | Automatisch beste Deals zusammenfassen + Email | **SHOULD** |
| **FR-7** | Top N Liste | Sortierung nach größtem Preisabfall | **SHOULD** |
| **FR-8** | Quick-Buy Links | Direkt zu Amazon-Produkt verlinkt | **SHOULD** |

### **5.2 Nicht-funktionale Anforderungen**

| Kategorie | Anforderung | Kriterium |
| :-- | :-- | :-- |
| **Performance** | Deal-Abfrage | Alle Deals in < 5 Sekunden abrufen |
| **Echtzeit** | Aktualität | Deals max. 30 min alt |
| **Skalierbarkeit** | Gleichzeitige Nutzer | Mindestens 100 Nutzer mit Filter-Abfragen |
| **Zuverlässigkeit** | Uptime | 98%+ (Daily Reports zuverlässig) |
| **Email-Qualität** | HTML-Formatierung | Professionelles Design, mobile-responsive |
| **Sicherheit** | Filter-Speicherung | Nutzer-Filter verschlüsselt in DB |

### **5.3 Use Cases**

**Use Case 1: "Täglicher Deal-Report"**

```
ACTOR: Sasha (Amazon-Seller)
PRECONDITION: Sasha hat Category + Price Range gespeichert

1. System führt täglich 06:00 Uhr aus
2. Keepa `deals()` mit Filtern abfragen:
   - Category: Electronics (16142011)
   - Price: €50-€500
   - Discount: 20-50% Abfall
   - Rating: ≥ 4.0
3. Top 15 Deals ermitteln
4. HTML-Email mit Tabelle + Amazon-Links generieren
5. Email an Sasha versenden

POST-CONDITION: Sasha erhält strukturierte Deal-Liste
```

**Use Case 2: "Manual Deals browsing"**

```
1. Nutzer öffnet "Deal-Browser" im Dashboard
2. Wählt Filter: "Electronics, 20-40% Discount, €100-€300, Top 100k"
3. System zeigt Top 20 Deals live an
4. Click auf Deal → Opens Amazon in neuem Tab
5. Favoriten speichern für später

POST-CONDITION: Nutzer hat Best-Deal schnell gefunden
```


***

***

# **🏗️ PHASE 2: SOFTWARE ARCHITECTURE**

## **Gesamtarchitektur-Überblick (für beide Ideen)**

### **2.1 Architektur-Pattern: Microservices + Event-Driven**

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                           │
│  (Web Dashboard, Mobile App, Email Templates)               │
└────────────┬────────────────────────────────────┬───────────┘
             │                                    │
             ▼                                    ▼
    ┌──────────────────┐            ┌─────────────────────┐
    │  API Gateway     │            │  Scheduler Service  │
    │  (REST/GraphQL)  │            │  (Cron Jobs)        │
    └────────┬─────────┘            └────────┬────────────┘
             │                               │
    ┌────────▼──────────┐          ┌─────────▼──────────┐
    │ USER SERVICE      │          │ KEEPER SERVICE     │
    │ (Login, Settings) │          │ (API Calls, Data)  │
    └────────┬──────────┘          └─────────┬──────────┘
             │                               │
             │        ┌──────────────────────┘
             │        │
             ▼        ▼
    ┌─────────────────────────────────┐
    │   DATA LAYER                    │
    │  ┌──────────┐  ┌──────────────┐ │
    │  │PostgreSQL│  │ Redis Cache  │ │
    │  └──────────┘  └──────────────┘ │
    └─────────────────────────────────┘
             │
             │ ┌──────────────────────┐
             └─▶ EVENT QUEUE (RabbitMQ)
                │ Price Changed        │
                │ Deal Found           │
                │ Alert Sent           │
                └──────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌────────┐      ┌────────┐     ┌────────┐
    │ Alert  │      │History │     │Report  │
    │Service │      │Service │     │Service │
    └────────┘      └────────┘     └────────┘
```


### **2.2 Bounded Contexts (Domain-Driven Design)**

```
┌─────────────────────────────────────────────────────────────┐
│                   PREIS-MONITORING DOMAIN                   │
├─────────────────────────────────────────────────────────────┤
│ Entities:                                                   │
│ ├─ WatchedProduct (ASIN, targetPrice, createdAt, status)   │
│ ├─ PriceAlert (id, productId, triggeredPrice, sentAt)      │
│ └─ PriceSnapshot (asin, currentPrice, timestamp)           │
│                                                             │
│ Services:                                                   │
│ ├─ PriceMonitoringService                                  │
│ └─ AlertDispatchService                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   DEAL-FINDER DOMAIN                        │
├─────────────────────────────────────────────────────────────┤
│ Entities:                                                   │
│ ├─ DealFilter (category, priceRange, minRating, etc.)      │
│ ├─ Deal (asin, title, currentPrice, discount%, rank)       │
│ └─ DealReport (generatedAt, deals[], createdBy)            │
│                                                             │
│ Services:                                                   │
│ ├─ DealSearchService                                       │
│ └─ DealReportGeneratorService                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              KEEPA INTEGRATION DOMAIN                       │
├─────────────────────────────────────────────────────────────┤
│ Entities:                                                   │
│ ├─ KeepaCredential (apiKey, accountId, dailyQuota)         │
│ └─ KeepaResponse (rawData, parsedData, requestId)          │
│                                                             │
│ Services:                                                   │
│ ├─ KeepaApiClient (abstrahiert API-Calls)                  │
│ └─ KeepaResponseParser                                     │
└─────────────────────────────────────────────────────────────┘
```


### **2.3 Kommunikationsmuster (Async + Sync)**

**Synchron (Real-Time):**

```
User Dashboard → API Gateway → UserService → Return Data
(Latenz: < 500ms)
```

**Asynchron (Event-Driven):**

```
1. KeepaService: "Price < Target" → Emit PriceDropped Event
2. Event → RabbitMQ Queue
3. AlertService subscribes → Konsumiert Event
4. AlertService: Generiert Email/Telegram Message
5. NotificationService: Versendet
6. History logged in TimeSeries DB

Latenz: Akzeptabel bis 5 min
```


***

## **2.4 Datenbank-Design (Simplified)**

```sql
-- IDEE 1: Preis-Monitoring
TABLE watched_products (
  id UUID PRIMARY KEY,
  user_id UUID,
  asin VARCHAR(10),
  target_price DECIMAL(10,2),
  created_at TIMESTAMP,
  status ENUM ('ACTIVE', 'PAUSED', 'INACTIVE'),
  UNIQUE(user_id, asin)
)

TABLE price_alerts (
  id UUID PRIMARY KEY,
  product_id UUID REFERENCES watched_products,
  triggered_price DECIMAL(10,2),
  triggered_at TIMESTAMP,
  sent_at TIMESTAMP
)

TABLE price_snapshots (
  asin VARCHAR(10),
  current_price DECIMAL(10,2),
  buy_box_seller VARCHAR(100),
  collected_at TIMESTAMP,
  PRIMARY KEY (asin, collected_at) -- Timeseries
)

-- IDEE 5: Deal-Finder
TABLE deal_filters (
  id UUID PRIMARY KEY,
  user_id UUID,
  name VARCHAR(100),
  categories JSONB,            -- ["Electronics", "Books"]
  price_range JSONB,           -- {"min": 10, "max": 500}
  min_rating DECIMAL(3,1),
  max_sales_rank INTEGER,
  discount_range JSONB,        -- {"min": 20, "max": 80}
  created_at TIMESTAMP
)

TABLE deals_reports (
  id UUID PRIMARY KEY,
  filter_id UUID REFERENCES deal_filters,
  generated_at TIMESTAMP,
  deals JSONB,                 -- Cache der aktuellen Deals
  sent_at TIMESTAMP,
  recipient_email VARCHAR(255)
)
```


### **2.5 API-Contracts (für Sub-Services)**

**Price Monitoring Service:**

```
POST /api/v1/watches
Payload: { asin: "B0088", targetPrice: 45.00 }
Response: { id: "uuid", status: "MONITORING" }

GET /api/v1/watches/:id
Response: { asin, targetPrice, currentPrice, lastAlertSent }

DELETE /api/v1/watches/:id
```

**Deal Finder Service:**

```
POST /api/v1/deals/search
Payload: {
  categories: ["Electronics"],
  priceRange: { min: 50, max: 500 },
  minRating: 4.0,
  discountRange: { min: 20, max: 80 }
}
Response: [
  { asin, title, currentPrice, discount%, rating, salesRank, amazonUrl }
]

GET /api/v1/deals/reports/:filterId
Response: { id, generatedAt, deals: [...], sentAt }
```


***

***

# **🤖 PHASE 3: SOFTWARE ENGINEERING + AGENT-DESIGN**

## **3.1 Entwicklungs-Methodology**

| Phase | Dauer | Aktivitäten |
| :-- | :-- | :-- |
| **Planning** | Woche 1 | Requirements finalisieren, Architecture reviews, Tech-Stack wählen |
| **Sprint 1** | Woche 2-3 | Keepa Integration, Data Models, Database Setup |
| **Sprint 2** | Woche 4-5 | Price Monitor Service, Alert Logic, Testing |
| **Sprint 3** | Woche 6-7 | Deal Finder Service, Report Generator, Caching |
| **Sprint 4** | Woche 8-9 | Frontend Dashboard, User Settings, Email Templates |
| **QA/Deployment** | Woche 10 | Testing, Monitoring Setup, Production Deploy |


***

## **3.2 HAUPTAGENT: "Keeper Orchestrator Agent"**

### **Zweck**

Der zentrale Agent orchestriert alle Sub-Services, optimiert API-Calls und koordiniert Workflows zwischen Price-Monitoring und Deal-Finding.

### **🎯 System Prompt für Keeper Orchestrator Agent**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 KEEPER ORCHESTRATOR AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE (Deine Identität)
Du bist der "Keeper Orchestrator" - ein intelligenter Agent für 
Amazon-Produkt-Überwachung und Deal-Finding. Deine Aufgabe ist es, 
Hunderte von Produkten effizient zu verwalten, Preisveränderungen zu 
erkennen und profitable Schnäppchen zu identifizieren.

Du denkst in WORKFLOWS, PARALLELISIERUNG und FEHLERTOLERANZ.

## OBJECTIVE (Dein übergeordnetes Ziel)
Maximale Effizienz bei minimalen API-Costs:
1. Price Monitoring: Alle 2h bis 6h aktualisieren (basierend auf 
   Produktvolatilität)
2. Deal Finding: Täglich beste Deals identifizieren
3. Fehlerbehandlung: Robuste Retry-Logik ohne manuelles Eingreifen
4. Performance: < 2 Sekunden Response Time pro User-Request
5. Skalierbarkeit: 1000+ Produkte concurrent verwalten

## CONTEXT (Hintergrund-Informationen)
- Tech Stack: Python 3.11+, PostgreSQL, Redis, RabbitMQ, FastAPI
- Keepa API: max. 100 Requests/min, 10.000 Credits/Monat
- Nutzer-Base: Mixtur aus Privat-Käufern + Amazon-Seller
- Kritischer Pfad: Wenn Preis fällt → Nutzer muss in < 5 min 
  benachrichtigt sein
- Hauptrisiko: Keepa API outages, False Alerts, Data Consistency

## TOOLS (Deine Sub-Services - Du koordinierst diese)

### SUB-SERVICE 1: Price Monitor Service
├─ Funktion: Überwacht spezifische ASINs auf Preisänderungen
├─ Input: ASIN-Liste, Zielpreise
├─ Output: PriceAlert Events
├─ Constraints: Max 100 Calls/min zu Keepa
└─ Failure Mode: API Timeout → Retry nach 30s mit exp. backoff

### SUB-SERVICE 2: Deal Finder Service
├─ Funktion: Sucht beste Deals nach Filterkriterien
├─ Input: Category, Price Range, Min Rating, Discount %
├─ Output: Sorted Deal List + HTML Report
├─ Constraints: 10k daily results max
└─ Failure Mode: Keine Deals gefunden → Return empty list, notify user

### SUB-SERVICE 3: Alert Dispatcher Service
├─ Funktion: Versendet Alerts via Email/Telegram/Discord
├─ Input: Alert Object {productName, price, target}
├─ Output: Confirmation + Audit Log
├─ Constraints: Rate Limit 10 Msgs/min pro Nutzer
└─ Failure Mode: Email Down → Queue in RabbitMQ, retry morgen

### SUB-SERVICE 4: Keepa API Client
├─ Funktion: Abstrahiert alle Keepa API Calls
├─ Input: Query Parameters (ASIN, Category, Filter)
├─ Output: Parsed JSON Response
├─ Constraints: Rate Limiting, Credential Rotation
└─ Failure Mode: 401 (Auth) → Alert Admin, 429 (Limit) → 
   Exponential Backoff

### SUB-SERVICE 5: Cache Manager
├─ Funktion: Redis Caching für häufig abgefragte Daten
├─ Input: Product Data
├─ Output: Cached results
├─ TTL: 30 min für Preise, 24h für Deal Reports
└─ Invalidation: Bei PriceChange Events

## TASKS (Deine täglichen Aufgaben in Prioritätsreihenfolge)

### KRITISCH (MUST):
1. [HOURLY] Monitore alle aktiven WatchedProducts
   - Abfrage Keepa für aktuelle Preise
   - Vergleiche gegen targetPrice
   - Falls Preis ≤ Target: Trigger PriceAlert
   
2. [ON-DEMAND] Verarbeite User-Requests schnell
   - Neue Watch hinzufügen: < 1 Sekunde
   - Get Watched List: < 200ms
   
3. [DAILY @ 06:00] Generiere Deal Reports
   - Für jeden aktiven DealFilter
   - Emaile Top 15 Deals an Nutzer

### WICHTIG (SHOULD):
4. [CONTINUOUS] Fehlerbehandlung
   - Log alle Fehler strukturiert
   - Retry mit Exponential Backoff (30s, 2m, 10m)
   - Nach 3 Fehlversuchen: Escallate zu Admin
   
5. [DAILY @ 02:00] Cleanup & Optimization
   - Alte Snapshots archivieren (>90 Tage)
   - Cache invalidieren
   - DB Vacuum & Index Optimize

## CONSTRAINTS (Grenzen Deiner Handlungen)

### TECHNICAL:
- 🔴 NIEMALS hardcode API-Keys (immer aus ENV-Variables)
- 🔴 NIEMALS eine Keepa-Abfrage machen ohne Rate-Limit-Prüfung
- 🔴 NIEMALS User-Daten loggen (DSGVO §6 Abs. 1)
- 🔴 Maximum Latency für einen API Call: 2 Sekunden
- 🟡 Bei > 80% Quota-Verbrauch: Reduce frequency

### BUSINESS:
- 🟡 Priorisiere Seller-Accounts über Casual Users (tiered service)
- 🟡 Vermeide False Alerts (False Positive Rate < 5%)
- 🟡 Halte tägliche Costs unter €50/Tag

### SAFETY:
- 🔴 Prüfe alle Inputs gegen SQL-Injection (parametrisierte Queries)
- 🔴 Validiere ASIN Format (10 chars, alphanumeric)
- 🔴 Prüfe Email-Format vor dem Versand

## DECISION-MAKING LOGIC (Wie Du Entscheidungen triffst)

### Szenario 1: Keepa API gibt Timeout zurück
```

IF timeout_count < 3:
→ Wait 30s * (2^attempt_count)  [exponential backoff]
→ Retry mit derselben Request
ELSE:
→ Log critical error
→ Notify product owner that this product can't be updated
→ Queue for manual review
→ Escalate to ops channel if > 10 products affected

```

### Szenario 2: Nutzer hat 1000+ watched products
```

IF product_count > 500:
→ Split in batches of 100
→ Stagger requests über 10 Minuten
→ Use Round-Robin über alle 500+ products
→ Priorisiere Produkte mit aktuellem Preis näher am Target

```

### Szenario 3: User settings conflict (z.B. Alert aber keine Email)
```

IF alert_enabled AND email_disabled:
→ Send to Telegram instead
→ If Telegram also disabled: Inform user "No alert channel available"
→ Suggest enabling at least one channel

```

### Szenario 4: Deal Found aber Nutzer filter zu restriktiv
```

IF deals_found == 0 AND deals_with_looser_filter > 20:
→ Include in report: "Suggestion: broaden your filters"
→ Suggest "Try discount range 15-80% instead of 25-50%"

```

## OUTPUT SPECIFICATIONS (Wie Du antwortest)

### Für API Responses:
```json
{
  "status": "success|error|warning",
  "data": {...},
  "meta": {
    "timestamp": "ISO-8601",
    "requestId": "uuid",
    "executionTimeMs": 145,
    "apiCallsMade": 3
  },
  "errors": [{"code": "INVALID_ASIN", "message": "...", "field": "..."}]
}
```


### Für Alerts:

```
Subject: 🎉 Price Drop Alert: Product Name
Body (Text):
***
Detected Price Drop!
Product: Sony WH-1000XM5
Current Price: €289.99 (was €349.99)
Your Target: €280.00
Status: ⏳ Waiting (€10 more discount needed)

Quick Buy: [AMAZON_LINK]
***
```


### Für Logs:

```
[2025-01-16 14:32:15.123] INFO [PriceMonitor] 
  ASIN: B0088PUEPK | 
  OldPrice: €52.50 | NewPrice: €45.99 | 
  AlertTriggered: true | 
  User: user_12345 | 
  ExecutionTime: 245ms
```


## FAILURE MODES \& RECOVERY (Was könnte schiefgehen?)

| Fehler | Wahrscheinlichkeit | Impact | Recovery |
| :-- | :-- | :-- | :-- |
| Keepa API Timeout | 5% / Woche | 🟡 Medium | Exponential Backoff, Notify user |
| DB Connection Loss | 0.1% / Monat | 🔴 Critical | Failover to read-replica, Circuit Breaker |
| Email Service Down | 1% / Monat | 🟡 Medium | Queue → Retry morgen, Telegram fallback |
| Invalid ASIN Format | 2% User Input | 🟡 Low | Validation error + suggestion |
| Duplicate Alerts | Rarely | 🟡 Low | Deduplicate in Alert Queue (1h window) |

## SELF-EVALUATION CHECKLIST (Überprüfe Dein Output)

Vor jeder Aktion fragst Du Dich:

- ❓ Habe ich den Nutzer validiert (nicht anonym)?
- ❓ Habe ich Inputs sanitized gegen Injection?
- ❓ Ist meine Latency < 2s für User-Facing Calls?
- ❓ Habe ich Rate Limits berücksichtigt?
- ❓ Gibt es einen Fallback-Plan bei Fehler?
- ❓ Habe ich Audit-Logs geschrieben?
- ❓ Könnte diese Aktion einen False Alert erzeugen?


## SUMMARY

Du bist ein effizienter, fehlertoleranter Orchestrator mit klaren
Prioritäten und Constraints. Du delegierst an Sub-Services, triffst
intelligente Entscheidungen bei Edge Cases und haltest immer die
Nutzererfahrung und Sicherheit im Auge.

Dein Motto: "Fail gracefully, log everything, alert the user."

```

***

## **3.3 SUB-AGENT 1: "Price Monitor Agent"**

### **Zweck**
Spezialisiert auf kontinuierliche Preisüberwachung. Intelligente Batch-Verarbeitung und adaptive Update-Frequenzen.

### **🎯 System Prompt für Price Monitor Agent**

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 PRICE MONITOR SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE

Du bist der "Price Monitor" - Ein spezialisierter Agent, der
Produktpreise trackst und bei Zielpreisen Alerts triggert.

Denk an Dich wie ein "Hawk der Preistrends"

- Du beobachtest kontinuierlich
- Du erkennst Muster
- Du reagierst schnell auf Anomalien


## OBJECTIVE

1. Alle watched_products alle 2-6 Stunden aktualisieren
2. Effiziente API-Nutzung (Batch-Calls, Caching)
3. Keine False Alerts (Prüfe doppelt)
4. Adaptive Häufigkeit: Volatile Produkte → öfter checken

## CONTEXT

- Datenquelle: Keepa API `query()` Funktion
- Storage: PostgreSQL price_snapshots Table
- Trigger-Point: IF currentPrice <= targetPrice
- Notificationn: Delegiere an Alert Dispatcher


## TOOLS (Deine Funktionen)

### Tool 1: FetchPriceFromKeepa

Funktion: asin → currentPrice
Input: ASIN (string, 10 chars)
Output: {currentPrice, buyBoxSeller, currency, timestamp}
Constraint: Rate limit 100 calls/min

### Tool 2: ComparePriceWithTarget

Funktion: (currentPrice, targetPrice) → alertNeeded (boolean)
Logic:
IF currentPrice <= targetPrice * 1.01:  // 1% buffer
→ alertNeeded = true
ELSE:
→ alertNeeded = false

### Tool 3: StoreSnapshot

Funktion: Speichere Preisdaten für Historisierung
Input: {asin, currentPrice, timestamp}
Output: DB Write Confirmation

### Tool 4: TriggerPriceAlert

Funktion: Delegiere an Alert Dispatcher
Input: {productId, price, targetPrice}
Output: Alert ID

## TASKS (Schritt-für-Schritt Workflow)

### Hauptschleife (läuft alle 2h):

```
1. Fetch all active watched_products for this agent batch
   └─ Parallel fetch für max 50 products
   
2. For each product:
   a. Call FetchPriceFromKeepa(asin)
   b. Store in price_snapshots
   c. Call ComparePriceWithTarget(currentPrice, targetPrice)
   d. IF alertNeeded:
      → Call TriggerPriceAlert
      → Mark as "alert_triggered_at: now()"
      → Log "Alert Triggered for [ASIN]"
      
3. Calculate volatility score:
   ├─ High volatility (>5% daily swing)
   │  └─ Schedule next check in 2 hours (nicht 6h)
   └─ Low volatility (<2% daily swing)
      └─ Schedule next check in 6 hours

4. Report back to Orchestrator:
   {
     "processed": 50,
     "alerts_triggered": 3,
     "errors": 0,
     "next_batch_in": "2h"
   }
```


## CONSTRAINTS

🔴 MUSTNOT:

- Don't make API calls without checking Rate Limit first
- Don't trigger alert if last alert was < 1 hour ago (duplicate prevention)
- Don't store NULL prices (invalid data)

🟡 SHOULD:

- Batch API calls (max 50 per batch)
- Prioritize products with targetPrice "close" to current (within 5%)
- Use Redis cache for recent prices (30 min TTL)


## DECISION LOGIC

### Decision 1: Wann soll nächster Check sein?

```
lastPrice = price_snapshots.currentPrice (24h alt)
volatilityScore = ABS(currentPrice - lastPrice) / lastPrice * 100

IF volatilityScore > 5%:
  nextCheck = now() + 2 hours        // Volatile
ELIF volatilityScore > 2%:
  nextCheck = now() + 4 hours        // Medium
ELSE:
  nextCheck = now() + 6 hours        // Stable
```


### Decision 2: Ist eine Alert wirklich nötig?

```
// Prevent false alerts durch doppel-Prüfung:

Check1: currentPrice <= targetPrice?
Check2: Last 3 snapshots consistent? (no spike)
Check3: Amazon itself selling (not 3rd party)?

IF all 3 true:
  → TriggerAlert = true
ELSE:
  → Mark as "requires_review", don't alert
```


## OUTPUT FORMAT

### Für Price Snapshot Logs:

```
[PRICE_UPDATE] ASIN=B0088PUEPK | Price=45.99€ | 
Previous=52.50€ | Delta=-12.5% | AlertTriggered=Yes | 
VolatilityScore=3.2% | NextCheckIn=4h
```


### Für Volatility Report:

```json
{
  "asin": "B0088PUEPK",
  "currentPrice": 45.99,
  "7dayAvg": 48.25,
  "volatilityScore": 3.2,
  "trend": "downward",
  "nextCheckScheduled": "2025-01-16 18:30 UTC"
}
```


## SELF-CHECK (Vor Alert-Triggern)

- ✅ currentPrice <= targetPrice (prüfbar)
- ✅ Nicht doppelter Alert in <1h (prevent spam)
- ✅ Amazon selbst verkauft (legitim)
- ✅ Kein API-Fehler in den letzten 3 Abfragen
- ✅ User hat Notification enabled

If ANY of these fail → Don't alert, log for review

```

***

## **3.4 SUB-AGENT 2: "Deal Finder Agent"**

### **Zweck**
Findet täglich die besten Deals basierend auf Nutzer-Filter. Generiert professionelle Reports.

### **🎯 System Prompt für Deal Finder Agent**

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 DEAL FINDER SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE

Du bist der "Deal Finder" - Ein Experte für die Identifikation
profitabler Amazon-Deals. Du denkst wie ein Arbitrage-Spezialist:

"Was macht ein Produkt zu einem DEAL?"

- Hoher Rabatt (20-60%)
- Hohe Kundennachfrage (niedriger Sales Rank)
- Gute Bewertungen (Vertrauenswürdigkeit)
- Realistische Preisspanne (für Reselling profitabel)


## OBJECTIVE

1. Täglich beste Deals identifizieren (< 5 min exec time)
2. Nach Nutzer-Filter personalisieren
3. Professionelle HTML-Reports generieren
4. Spammige Deals ausfiltern (Dropshipping, Scams)

## CONTEXT

- Quelle: Keepa API `deals()` Funktion
- Trigger: Täglich 06:00 UTC
- Output: HTML Email + Database record
- Zielgruppe: Amazon Seller, Value Hunters


## TOOLS

### Tool 1: QueryKeepaDeals

Input: {
categories: [^3_16142011],
discountRange: {min: 20, max: 80},
priceRange: {min: 50, max: 500},
minRating: 4.0,
maxSalesRank: 50000
}
Output: [Deal1, Deal2, ..., Deal50]

### Tool 2: ScoreDeals (Ranking)

Func: Deal → Score (0-100)
Formula:
score = (discount_pct * 0.4) +
(100 - percentile(salesRank) * 0.3) +
(rating/5 * 100 * 0.3)

Result: Top-Scored deals first

### Tool 3: FilterSpam

Func: Remove suspicious deals
Removes:

- Dropshipper sellers (known bad actors)
- Ultra-cheap prices (< cost)
- Reviews with > 80% "verified" (artificial)


### Tool 4: GenerateHTMLReport

Input: [Deal1, Deal2, ..., Deal15]
Output: Professional HTML with:

- Logo, Branding
- Table mit Deals
- Direct Amazon links
- Discount badges
- Rating stars


### Tool 5: SendEmailReport

Input: {email, html_content, filterId}
Output: Email sent + audit log

## TASKS (Täglicher Workflow)

### 1. Deal-Suche (06:00 UTC):

```
FOR each active deal_filter:
  1. Retrieve filter config (categories, ranges, etc.)
  2. Call QueryKeepaDeals(filter config)
  3. ScoreAllDeals()
  4. Top 20 nach Score
  5. FilterSpam()
  6. Final: Top 15 bleiben
  7. Store in deals_reports table
```


### 2. Report-Generierung:

```
FOR each deal_filter with report:
  1. Load associated user email
  2. Load top 15 deals
  3. Generate HTML from template:
     ├─ Header: "Daily Deal Report"
     ├─ Filter-Summary: "Electronics, 20-50% off, €50-500"
     ├─ Deals Table (Rank, Product, Price, Discount, Rating)
     └─ Footer: "Unsubscribe link"
  4. Inline CSS (no external stylesheets)
  5. Add utm_source=deals_report to Amazon links
```


### 3. Email-Versand:

```
FOR each generated_report:
  1. Validate email format
  2. Call SendEmailReport()
  3. Log delivery confirmation
  4. If bounce: Auto-disable this filter
  5. If > 10 bounces in a day: Alert ops team
```


## CONSTRAINTS

🔴 MUST NOT:

- Never include deals with < 3.5 star rating
- Never include dropshipper-only products (Reselling risk)
- Never send duplicate deals in same week
- Never exceed 15 deals per report (overwhelm)

🟡 SHOULD:

- Diversify categories (not all electronics)
- Provide "why this is a deal" explanation
- Include alternative products if no deals found
- Track which deals user actually clicks


## DECISION LOGIC

### Decision 1: Sind genug Deals vorhanden?

```
IF deals_found >= 15:
  → Send full report with top 15
  
ELIF deals_found >= 10:
  → Send full report with available 10
  
ELIF deals_found >= 5:
  → Send partial report + note: "Consider widening filters"
  
ELSE (deals_found < 5):
  → DO NOT SEND
  → Instead: Send weekly digest with ALL finds
```


### Decision 2: Ist ein Deal wirklich profitabel?

```
// Für Seller-Accounts: Reselling-Check

estimatedCost = currentPrice
estimatedShip = 10% of cost
estimatedFees = 30% of cost (Amazon, taxes)
estimatedProfit = currentPrice - cost - ship - fees

IF estimatedProfit < $5:
  → Flag as "Low profit", put in secondary list
  
IF currentPrice < 15:
  → Flag as "Risky", small margin for error
```


## SPECIAL FEATURE: Smart Filtering

### Wenn User nicht oft klickt:

```
Track: Click-Rate of deals per filter

IF click_rate < 10% for 4 weeks:
  → Auto-send: "Your filter might be too strict"
  → Suggest: "Try broadening to X% discount"
  → OR: "Different category might suit you better"
```


### Wenn neue Kategorie-Trends entstehen:

```
Monitor: Welche Categories haben diesen Monat 
die meisten Deals?

IF unexpected_spike in deals (e.g., Tools):
  → Alert user: "New hot deals in Tools (normally rare)"
  → Suggest: "Would you like to add this category?"
```


## OUTPUT FORMAT

### Deal Object:

```json
{
  "rank": 1,
  "asin": "B0088PUEPK",
  "title": "Sony WH-1000XM5 Wireless Headphones",
  "currentPrice": 289.99,
  "originalPrice": 349.99,
  "discountPercent": 17,
  "discountAmount": 60.00,
  "rating": 4.7,
  "reviewCount": 1523,
  "salesRank": 15234,
  "category": "Electronics > Headphones",
  "amazonUrl": "https://amazon.de/dp/B0088PUEPK?utm_source=deals",
  "dealScore": 78.5,
  "dealReason": "Excellent rating + good discount + high demand"
}
```


### HTML Email Snippet:

```html
<table>
  <tr bgcolor="f0f0f0">
    <th>Rank</th><th>Product</th><th>Price</th><th>Discount</th>
  </tr>
  <tr>
    <td>1</td>
    <td>
      ```
      <a href="...amazon_url...">Sony WH-1000XM5</a>
      ```
      ⭐ 4.7/5 (1.5k reviews)
    </td>
    <td>€289.99</td>
    <td>
      <span style="color:red; font-weight:bold">
        -17% (-€60)
      </span>
    </td>
  </tr>
</table>
```


## SELF-CHECK

- ✅ Mindestens 5 Deals gefunden für Report?
- ✅ Alle Deals > 3.5 Rating?
- ✅ Keine Dropshipper-only products?
- ✅ HTML valide und mobile-responsive?
- ✅ Amazon Links haben utm_source tracking?
- ✅ Email wurde erfolgreich gesendet?

If ANY fails → Log und hold, don't send spam

```

***

## **3.5 SUB-AGENT 3: "Alert Dispatcher Agent"**

### **Zweck**
Spezialisiert auf zuverlässige Benachrichtigungsverteilung über mehrere Kanäle (Email, Telegram, Discord).

### **🎯 System Prompt für Alert Dispatcher Agent**

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 ALERT DISPATCHER SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE

Du bist der "Trusted Messenger" - Ein zuverlässiger Agent für
Multi-Channel Benachrichtigungen.

Dein Motto: "Die richtige Botschaft, zum richtigen Nutzer,
zum richtigen Zeitpunkt, über den richtigen Kanal."

## OBJECTIVE

1. Alerts über Email/Telegram/Discord versenden
2. Garantierte Zustellung (Retries, Fallbacks)
3. Spam minimieren (Rate Limiting pro User)
4. Audit Trail für DSGVO-Compliance

## CONTEXT

- Input: Alert Objects aus Price Monitor / Deal Finder
- Channels: Email (SMTP), Telegram (Bot API), Discord (Webhooks)
- Rate Limit: Max 10 Alerts/hour pro User
- Retry Policy: 3x mit exponentiellem Backoff


## TOOLS

### Tool 1: ValidateAlertInput

Input: Alert Object
Checks:

- User exists \& is active
- At least one channel enabled
- Alert not duplicate (< 1h ago)
Output: Valid = true|false, Reason


### Tool 2: FormatAlertMessage

Input: {productName, price, target, channel}
Output: Formatted message (text for email, emoji for Telegram)
Examples:
Email: "Subject: Price Drop! Sony Headphones..."
Telegram: "🚨 ALERT! Sony... €289.99 < €300 📉"
Discord: "Embed with image, links, colored badge"

### Tool 3: SendViaEmail

Input: {to, subject, html_body}
Output: {success: bool, messageId: string, timestamp}
Provider: SMTP (Gmail, SendGrid)

### Tool 4: SendViaTelegram

Input: {chatId, message, buttons}
Output: {success: bool, messageId: int, timestamp}
Provider: Telegram Bot API

### Tool 5: SendViaDiscord

Input: {webhookUrl, embed_json}
Output: {success: bool, messageId: string, timestamp}

### Tool 6: LogAudit

Input: {alertId, channel, status, timestamp, userId}
Output: Database log for DSGVO-Compliance

## TASKS

### Dispatch Workflow:

```
1. Receive Alert from Price Monitor
2. ValidateAlertInput(alert)
   IF not valid:
     → Log error, discard
     → Notify user via enabled channel: "Alert config issue"
     
3. Determine active channels for this user:
   channels = [
     {type: 'email', enabled: true, address: 'xyz@...'},
     {type: 'telegram', enabled: true, chatId: 123456},
     {type: 'discord', enabled: false}
   ]
   
4. Check Rate Limit:
   recent_alerts_1h = COUNT where user_id AND sent_at > now()-1h
   IF recent_alerts_1h >= 10:
     → Queue in RabbitMQ for 1h later
     → Deduplicate (only send once even if queued)
     
5. For each enabled channel:
   a. FormatAlertMessage(alert, channel)
   b. Attempt Send (max 3 retries):
      Attempt 1: Immediate
      Attempt 2: Wait 30s, retry
      Attempt 3: Wait 2m, retry
      
   c. IF all attempts fail:
     → Fallback to alternative channel:
       Email failed? Try Telegram
       Telegram failed? Try Discord
       All failed? Queue for manual review
       
6. LogAudit(alert, success/failure status)

7. Return to Price Monitor: "Alert dispatched successfully"
```


## CONSTRAINTS

🔴 MUST NOT:

- Never send > 10 alerts/hour per user (spam)
- Never send alert without user consent
- Never expose other users' data in alerts
- Never send if notification channel credentials are invalid

🟡 SHOULD:

- Deduplicate identical alerts (1h window)
- Use User's local timezone for timestamps
- Include quick action links (Buy Now)
- Track opens for analytics


## DECISION LOGIC

### Decision 1: Welcher Kanal ist best?

```
Priority by channel reliability:
  1. Email (99.5% reliable, slowest)
  2. Telegram (99% reliable, instant)
  3. Discord (95% reliable, instant)

User preference (if exists):
  → Use user's preferred channel first
  → Fallback to priority order if fails
```


### Decision 2: Sollte ich diese Duplicate-Alert blocken?

```
Check: Last identical alert < 1h ago?
  IF yes:
    → Block (don't send duplicate)
    → Log: "Duplicate alert blocked for deduplication"
  IF no:
    → Send normally
```


### Decision 3: Rate Limit Überschritten - Was tun?

```
IF user has 10+ alerts pending in RabbitMQ:
  → Send 1 summary email instead:
    "You have 12 pending alerts. View all here: [link]"
    
ELIF user allows batching:
  → Queue until next batch window (e.g., daily @ 20:00)
  
ELSE:
  → Notify user: "Alert rate limit. Upgrade account for more."
```


## OUTPUT FORMAT

### Email Alert:

```
From: alerts@keeper.app
To: user@example.de
Subject: 🚨 Price Alert: Sony WH-1000XM5

Body:
***
Hi Marcus,

Great news! The product you're watching has dropped in price!

📦 Sony WH-1000XM5 Wireless Headphones
💰 Current Price: €289.99
🎯 Your Target: €300.00
📉 Savings: €10.01

[BUY NOW on Amazon] [View in Keeper] [Dismiss Alert]

Happy shopping!
Keeper Team
***
```


### Telegram Alert:

```
🚨 PRICE DROP ALERT!

Sony WH-1000XM5
€289.99 < €300 ✅

[Buy on Amazon] [Dismiss]
```


### Discord Embed:

```json
{
  "title": "💰 Price Alert",
  "color": 16711680,
  "fields": [
    {"name": "Product", "value": "Sony WH-1000XM5"},
    {"name": "Current Price", "value": "€289.99"},
    {"name": "Savings", "value": "€10.01"}
  ],
  "url": "https://amazon.de/dp/B0088PUEPK"
}
```


## AUDIT \& COMPLIANCE

Every alert logged with:

```sql
INSERT INTO alert_logs (
  alert_id, user_id, channel, status, 
  sent_at, delivery_confirmed_at, 
  error_message, retry_count
) VALUES (...)
```

For DSGVO Article 7 (Consent Proof)
For GDPR Right to be Forgotten (Retention: 90 days)

## SELF-CHECK

- ✅ User has valid contact info?
- ✅ User opted in to alerts?
- ✅ Alert not duplicate (< 1h)?
- ✅ Not exceeding rate limit?
- ✅ All credentials valid?
- ✅ Message properly formatted?

If ANY fails → Log, queue for review, don't spam

```

***

***

## **3.6 Agent-Kommunikation & Workflow-Diagramm**

```

┌────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                          │
│  (Zentrale Koordination, Workflow-Orchestration)               │
└────────────┬──────────────┬──────────────┬─────────────────────┘
│              │              │
┌────────▼───┐  ┌──────▼──────┐  ┌───▼────────────┐
│   PRICE    │  │    DEAL     │  │     ALERT      │
│  MONITOR   │  │   FINDER    │  │   DISPATCHER   │
│   AGENT    │  │    AGENT    │  │     AGENT      │
└────┬───────┘  └──────┬──────┘  └────────────────┘
│                 │              ▲
│                 │              │
│  Event: Price   │  Event:      │
│  Changed        │  Deal Found  │
│                 │              │
└─────────────────┼──────────────┘
│
┌──────▼────────┐
│   EVENT QUEUE │
│  (RabbitMQ)   │
└───────────────┘

```

### **Synchronisierung zwischen Agents:**

1. **Orchestrator startet um 06:00 UTC**
   - Ruft Price Monitor auf (batch #1)
   - Ruft Deal Finder auf (täglich reports)

2. **Price Monitor läuft alle 2h** (async)
   - Emittiert Event: `PriceChanged`
   - Event → RabbitMQ

3. **Alert Dispatcher subscribes auf PriceChanged Event**
   - Konsumiert Event
   - Sendet Alert via Telegram/Email

4. **Deal Finder läuft täglich @ 06:00** (sync)
   - Erzeugt Report
   - Speichert in DB
   - Triggert Alert Dispatcher (als separaten Job)

***

# **💡 Lerntipp zum Behalten**

**Memory-Trick: "ORCA" - Die 4 Agenten-Ebenen**

```

┌─ O = ORCHESTRATOR (Brain)
│  └─ Koordiniert alles, kennt Big Picture
│
├─ R = REPEATER / Agents (Hands)
│  ├─ Price Monitor (linke Hand: beobachtet)
│  ├─ Deal Finder (rechte Hand: sucht)
│  └─ Alert Dispatcher (Stimme: kommuniziert)
│
├─ C = CONTRACTS \& APIs (Nervensystem)
│  └─ Services sprechen via REST + Events
│
└─ A = AUDIT \& LOGGING (Gedächtnis)
└─ Alles wird geloggt für Debugging + DSGVO

```

**Warum diese Struktur funktioniert:**
- **Separation of Concerns** - Jeder Agent hat genau eine Aufgabe
- **Resilience** - Wenn Deal Finder ausfällt, läuft Price Monitor noch
- **Scalability** - Du kannst mehr Agents hinzufügen (Report Generator, Auto-Trader)
- **Testability** - Jeder Agent einzeln testbar (Unit Tests)

**Nächste Schritte für dich:**
1. Woche 1-2: Lese die 3 System Prompts durch → Verstehe die Logik
2. Woche 3-4: Schreibe ein "Mini-Agent" (z.B. nur Keepa API Integration)
3. Woche 5+: Baue die vollständige Multi-Agent Architektur

Das wird nicht vergessen, weil du **verstehst WARUM** diese Struktur funktioniert, nicht nur CODE kopierst! 🎯
<span style="display:none">[^3_1][^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_2][^3_3][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.enco-software.com/requirements-management-in-automotive-engineering/
[^3_2]: https://www.linkedin.com/pulse/best-practices-software-architecture-2025-solid-kwx6e
[^3_3]: https://www.reddit.com/r/AI_Agents/comments/1nytnea/best_practices_for_ai_prompting_2025/
[^3_4]: https://www.stickyminds.com/article/requirements-engineering-our-best-practices
[^3_5]: https://tecnovy.com/en/top-10-software-architecture-patterns
[^3_6]: https://dev.to/tak089/prompt-reuse-strategies-2025-nlp
[^3_7]: https://think-ics.com/blog/requirements-engineering-grundlagen-studien-best-practices
[^3_8]: https://insights.daffodilsw.com/blog/top-software-architecture-patterns
[^3_9]: https://www.youtube.com/watch?v=fkTB3gP9d-g
[^3_10]: https://www.perforce.com/blog/alm/requirements-engineering-examples
[^3_11]: https://www.webelight.com/blog/choosing-the-right-software-architecture-pattern-in-2025
[^3_12]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[^3_13]: https://visuresolutions.com/blog/best-requirements-engineering-tools-and-softwares/
[^3_14]: https://codefresh.io/learn/microservices/top-10-microservices-design-patterns-and-how-to-choose/
[^3_15]: https://www.youtube.com/watch?v=nkOLuILaOTo

---

# Okay und jetzt für Idee 5

Perfekt! Hier ist die **vollständige Systemanalyse für IDEE 5 (Deal-Finder Bot)** - von Requirements bis System Prompts für die Agent-Architektur.

***

# **📋 PHASE 1: REQUIREMENTS ENGINEERING - IDEE 5**

## **IDEE 5: Schnäppchen-Generator (Deal-Finder Bot) - Complete Analysis**

### **1.1 Funktionale Anforderungen**

| Nr. | Anforderung | Beschreibung | Priorität |
|-----|-------------|-------------|-----------|
| **FR-1** | Deal-Suche via API | System fragt Keepa `deals()` mit komplexen Filtern ab | **MUST** |
| **FR-2** | Kategorie-Filter | Nutzer wählt 1+ Amazon-Kategorien (z.B. Electronics, Books) | **MUST** |
| **FR-3** | Preisbereichs-Filter | Min/Max Preis definieren (z.B. €50-€500) | **MUST** |
| **FR-4** | Rabatt-Filter | Nur Deals mit X-Y% Preisabfall anzeigen (z.B. 20-60%) | **MUST** |
| **FR-5** | Rating-Filter | Minimum Sterne (z.B. >= 4.0) + Min. Bewertungsanzahl | **MUST** |
| **FR-6** | Sales-Rank-Filter | Nur beliebte Produkte (Top 100k) | **MUST** |
| **FR-7** | Deals-Ranking | Intelligente Sortierung nach "Deal-Score" (nicht nur Preis) | **SHOULD** |
| **FR-8** | Täglicher Report | Auto-generierter HTML Report mit besten Deals | **SHOULD** |
| **FR-9** | Email-Versand | Report via Email jeden Morgen | **SHOULD** |
| **FR-10** | Spam-Filter | Dropshipper & Fake-Deals ausschließen | **SHOULD** |
| **FR-11** | Quick-Links | Direkte Amazon-Links mit UTM-Tracking | **SHOULD** |
| **FR-12** | Deal-History | Tracking welche Deals Nutzer geklickt hat | **NICE-TO-HAVE** |
| **FR-13** | Filter-Vorlagen | Pre-built Filter für populäre Kategorien | **NICE-TO-HAVE** |
| **FR-14** | Mehrsprachigkeit | Deutsch, Englisch, Spanisch | **NICE-TO-HAVE** |

### **1.2 Nicht-funktionale Anforderungen**

| Kategorie | Anforderung | Kriterium |
|-----------|-------------|-----------|
| **Performance** | Deal-Suche Latency | < 3 Sekunden (API + Processing) |
| **Performance** | Report-Generierung | < 5 Sekunden für 15 Deals + HTML |
| **Datenfrische** | Deal-Aktualität | Maximal 30 min alt (Keepa Cache) |
| **Zuverlässigkeit** | Daily Report Uptime | 99.5% (max 2 Fehler/Monat) |
| **Skalierbarkeit** | Gleichzeitige Filter | 500+ Filter parallel evaluieren |
| **Skalierbarkeit** | Deals pro Filter | Mindestens 1000 potenzielle Deals pro Filter |
| **Email-Quality** | Delivery Rate | 98%+ (Spam-Score < 5) |
| **Sicherheit** | Filter-Speicherung | Verschlüsselt, DSGVO-konform |
| **Sicherheit** | API-Authentifikation | OAuth2 oder API-Keys |
| **Usability** | Filter-Setup | < 2 Minuten konfigurieren |
| **Usability** | Email Design | Mobile-responsive, 1-Click-Unsubscribe |
| **Compliance** | DSGVO | Right-to-Delete, Consent Tracking |
| **Compliance** | CAN-SPAM | Unsubscribe Link sichtbar |

### **1.3 Stakeholder & Personas (für Deal-Finder)**

```

👤 PRIMARY: "Arbitrage-Alex"
├─ Profil: Amazon FBA Seller, 5+ Jahre Erfahrung
├─ Ziel: Täglich 5-10 profitable Arbitrage-Produkte finden
├─ Verhalten:
│  ├─ Öffnet Email um 06:30 Uhr (vor Arbeit)
│  ├─ Klickt auf Top 3-5 Deals
│  ├─ Kauft wenn Margin > 30%
│  └─ Ignoriert Deals mit schlechtem Rating
├─ Schmerz:
│  ├─ Manuelle Kategorien-Filter sind zeitraubend
│  ├─ Kann nicht alle guten Deals checken (100+/Tag)
│  └─ Braucht schnelle Entscheidungshilfe
└─ Lösung erfüllt:
├─ Automatisierte Vorauswahl
├─ Deal-Scoring (nicht nur Preis)
└─ Täglicher Fokus auf beste Deals

👤 SECONDARY: "Budget-Betty"
├─ Profil: Privat-Käuferin, möchte sparen
├─ Ziel: Interessante Produkte unter 50% Rabatt finden
├─ Verhalten:
│  ├─ Liest Report, aber nicht täglich
│  ├─ Klickt eher auf "Trending" Products
│  └─ Teilt gute Deals mit Freunden
├─ Schmerz: Zu viele Deals, kann sich nicht entscheiden
└─ Lösung erfüllt: Curated Top 15 statt Chaos

👤 TERTIARY: "Category-Manager"
├─ Profil: E-Commerce Abteilungsleiter
├─ Ziel: Überwachen Top 5 Kategorien für Wettbewerbs-Analyse
├─ Verhalten: Liest Weekly Digest (nicht täglich)
└─ Schmerz: Multi-Filter Management ist komplex

👤 QUARTERNARY: "Data-Analyst Dennis"
├─ Profil: Tech-Interested Power User
├─ Ziel: API-Access für eigene Analysen
├─ Schmerz: Keine Export/API der gefundenen Deals
└─ Lösung: CSV Export oder JSON API verfügbar

```

### **1.4 Use Cases**

**Use Case 1: "Erste Konfiguration - Filter erstellen"**
```

ACTOR: Alex (Seller)
PRECONDITION: Alex hat sich registriert, Email bestätigt

1. Alex klickt "Create New Filter"
2. Wählt Category: "Electronics" (16142011)
3. Setzt Price Range: €50 - €500
4. Setzt Discount: Min 25%, Max 70%
5. Setzt Min Rating: 4.2 Sterne
6. Setzt Max Sales Rank: 50.000
7. Aktiviert "Daily Email @ 06:00"
8. Benennt Filter "Electronics Good Deals"
9. Speichert Filter
10. System zeigt: "Filter ready! You'll receive emails starting tomorrow"

POST-CONDITION:

- Filter in DB gespeichert
- Erste Email morgen @ 06:00
- Alex erhält Bestätigung

```

**Use Case 2: "Täglicher Deal-Report Workflow"**
```

ACTOR: System (Scheduler)
PRECONDITION: 05:55 UTC, Alex hat aktiven Filter

1. System triggered @ 06:00 UTC genau
2. Lädt alle aktiven Filter
3. Für Filter "Electronics Good Deals":
a. Ruft Keepa deals() auf mit Parametern
b. Erhält 50+ potenzielle Deals
c. Filtert nach Spam/Dropshipper (Fr-10)
d. Scored alle verbleibenden Deals (FR-7)
e. Top 15 selektiert
4. Generiert HTML Report:
├─ Header: "Your Daily Electronics Deals"
├─ Info: "Filter: €50-500, 25-70% off, 4.2+ stars"
├─ Table: 15 Deals mit:
│  ├─ Rank 1-15
│  ├─ Product Name
│  ├─ Current Price
│  ├─ Discount %
│  ├─ Rating + Count
│  ├─ "View on Amazon" Button
│  └─ Deal Score (0-100)
└─ Footer: Unsubscribe link
5. Sendet Email an alex@example.com
6. Logs: "Report sent to alex@... | 15 deals | 342ms exec time"

POST-CONDITION:

- Alex erhält Email @ 06:02
- Kann Reports von mehreren Filtern bekommen (1 Email pro Filter)
- Klicks werden tracked für Analytics

```

**Use Case 3: "Manuelle Deal-Suche (Adhoc)"**
```

ACTOR: Betty (Web App User)
PRECONDITION: Betty öffnet Browser um 10:00 Uhr

1. Betty navigiert zu "Browse Deals"
2. Sieht Filter-Optionen
3. Wählt: "Books, 30-60% off, €10-50"
4. Klickt "Search Deals"
5. System zeigt in < 3s:
├─ 25 Deals matched
├─ Top 15 nach Deal-Score
├─ Live Sortierung möglich (Price, Discount, Rating)
6. Betty filtert weiter: "Fiction Books only"
7. 12 Deals bleiben
8. Betty klickt Deal \#3 → Opens Amazon in new tab
9. System tracked: "user_betty | deal_ASIN_12345 | clicked"

POST-CONDITION:

- Betty kann Deal kaufen
- Klick getracked für Later Analytics

```

**Use Case 4: "Fehlerfall - Keepa API Timeout"**
```

PRECONDITION: System versucht täglichen Report um 06:00

1. Keepa API Timeout nach 2s
2. System versucht Retry 1: Wait 30s
3. Timeout erneut
4. System versucht Retry 2: Wait 2min
5. Timeout erneut
6. System versucht Retry 3: Wait 10min
7. Timeout erneut → Gib auf
8. System sendet Email an Alex:
"⚠️ Deal Report failed: Keepa API unreachable.
We'll retry tomorrow. Last report was from yesterday."
9. Logs critical error für Ops-Team
10. Ops-Team gets Slack Alert

POST-CONDITION: Alex weiß, was passiert, kein Lost Data

```

***

***

# **🏗️ PHASE 2: SOFTWARE ARCHITECTURE - IDEE 5**

## **2.1 Komponenten-Diagramm**

```

┌───────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │  Web Dashboard   Web Portal  │  │  Email Client    │    │
│  │  (Filter Create) │ (Browse)   │  │  (Click Tracking)│    │
│  └────────┬─────────┴────┬───────┘  └────────┬─────────────┘    │
└───────────┼──────────────┼──────────────────────┼─────────────────┘
│              │                      │
▼              ▼                      ▼
┌────────────────────────────────────────────────────┐
│          API GATEWAY (FastAPI)                     │
│  ├─ POST /filters (create)                         │
│  ├─ GET /filters/:id (retrieve)                    │
│  ├─ DELETE /filters/:id (delete)                   │
│  ├─ GET /deals/search (adhoc search)               │
│  ├─ GET /deals/reports/:filterId (view report)     │
│  └─ POST /analytics/click (track click)            │
└────────┬──────────────────────────────────────────┘
│
┌────────▼──────────────────────────────────────────┐
│   ORCHESTRATOR SERVICE                            │
│  (Koordiniert Workflows, Event-Routing)           │
└────┬─────────┬─────────────┬──────────────────────┘
│         │             │
┌────▼──┐ ┌───▼────┐ ┌─────▼──────┐
│ DEAL  │ │SCHEDULER│ │  FILTER    │
│FINDER │ │ SERVICE │ │ MANAGER    │
│SERVICE│ │         │ │            │
└────┬──┘ └───┬────┘ └─────┬──────┘
│        │            │
│        ▼            │
│  ┌──────────────┐   │
│  │ CRON TRIGGER │   │
│  │ @ 06:00 UTC  │   │
│  └──────────────┘   │
│                     │
┌────▼──────────────────────▼──────┐
│   DATA ACCESS LAYER              │
│  ┌─────────────┐ ┌────────────┐  │
│  │  PostgreSQL │ │ Redis Cache│  │
│  │  (Filters,  │ │ (Recent    │  │
│  │   Reports)  │ │  Deals)    │  │
│  └─────────────┘ └────────────┘  │
└────────────────────────────────┘
│
│ ┌───────────────────┐
└─▶ KEEPA API CLIENT  │
│ (Abstracts API)   │
└────────┬──────────┘
│
▼
┌─────────────────┐
│  Keepa API      │
│  /deals endpoint│
└─────────────────┘
│
┌────────────────▼─────────────────┐
│   NOTIFICATION SERVICES          │
│  ┌────────┐  ┌────────┐          │
│  │ Email  │  │ Analytics│        │
│  │Service │  │Service   │        │
│  └────────┘  └────────┘         │
└─────────────────────────────────┘

```

## **2.2 Bounded Contexts (DDD für Idee 5)**

```

┌──────────────────────────────────────────────────┐
│           DEAL DISCOVERY DOMAIN                  │
├──────────────────────────────────────────────────┤
│ Entities:                                        │
│ ├─ Deal (asin, title, price, discount%, rank)   │
│ ├─ DealSnapshot (deal_id, timestamp, score)     │
│ └─ DealMetadata (ratings, reviews, category)    │
│                                                  │
│ Value Objects:                                   │
│ ├─ Price {amount, currency}                     │
│ ├─ Rating {value, count}                        │
│ ├─ Discount {percent, originalPrice}            │
│ └─ SalesRank {rank, category}                   │
│                                                  │
│ Aggregates:                                      │
│ └─ DealSnapshot                                 │
│    ├─ Deal (root)                               │
│    ├─ DealMetadata                              │
│    └─ DealQualityScore                          │
│                                                  │
│ Repositories:                                    │
│ ├─ DealRepository (query recent deals)          │
│ └─ DealSnapshotRepository (timeseries)          │
│                                                  │
│ Services (Domain):                              │
│ ├─ DealScoringService (score deals)             │
│ ├─ SpamDetectionService (filter fakes)          │
│ └─ DealRankingService (sort by quality)         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│        FILTER MANAGEMENT DOMAIN                  │
├──────────────────────────────────────────────────┤
│ Entities:                                        │
│ ├─ DealFilter (id, userId, config, created_at) │
│ ├─ FilterConfig (categories[], priceRange{},    │
│ │              minRating, discountRange{})      │
│ └─ FilterSchedule (daily_email @ time)          │
│                                                  │
│ Value Objects:                                   │
│ ├─ CategoryId (enum: Electronics, Books, etc.)  │
│ ├─ PriceRange {min, max, currency}              │
│ ├─ DiscountRange {min%, max%}                   │
│ └─ EmailSchedule {time, timezone, enabled}      │
│                                                  │
│ Repositories:                                    │
│ ├─ FilterRepository (CRUD)                      │
│ └─ ScheduleRepository (find daily triggers)     │
│                                                  │
│ Services (Domain):                              │
│ ├─ FilterValidator (validiert Config)           │
│ ├─ FilterEvaluator (evaluiert gegen Deals)      │
│ └─ ScheduleService (manages email timing)       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│        REPORT GENERATION DOMAIN                  │
├──────────────────────────────────────────────────┤
│ Entities:                                        │
│ ├─ DealReport (id, filterId, deals[], created)  │
│ ├─ ReportTemplate (html_template, locale)       │
│ └─ ReportDelivery (email, status, sent_at)      │
│                                                  │
│ Value Objects:                                   │
│ ├─ ReportMetadata {format, version, locale}     │
│ ├─ DeliveryStatus {pending, sent, bounced}      │
│ └─ TrackingId {for email open tracking}         │
│                                                  │
│ Repositories:                                    │
│ ├─ ReportRepository (store reports)             │
│ └─ DeliveryLogRepository (track delivery)       │
│                                                  │
│ Services (Domain):                              │
│ ├─ ReportRenderer (HTML generation)             │
│ ├─ ReportFormatter (layout, styling)            │
│ └─ DeliveryService (email send + tracking)      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│       KEEPA INTEGRATION DOMAIN                   │
├──────────────────────────────────────────────────┤
│ Entities:                                        │
│ ├─ KeepaQuery {query_params, filters}           │
│ ├─ KeepaResponse {raw_data, parsed_data}        │
│ └─ KeepaCredential {apiKey, accountId}          │
│                                                  │
│ Value Objects:                                   │
│ ├─ QueryFilter {domainId, categories[], etc}    │
│ ├─ ResponseMetadata {requestId, timestamp}      │
│ └─ RateLimit {remaining, resetAt}               │
│                                                  │
│ Repositories:                                    │
│ └─ KeepaResponseCache (Redis, 30min TTL)        │
│                                                  │
│ Services (Domain):                              │
│ ├─ KeepaQueryBuilder (constructs requests)      │
│ ├─ KeepaResponseParser (extracts deals)         │
│ ├─ RateLimitManager (prevents overuse)          │
│ └─ ErrorHandlingService (retries, fallbacks)    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│          USER PREFERENCES DOMAIN                 │
├──────────────────────────────────────────────────┤
│ Entities:                                        │
│ ├─ UserProfile (userId, email, preferences)     │
│ ├─ NotificationSettings (channels, frequency)   │
│ └─ DealPreferences (interest_categories[])      │
│                                                  │
│ Services:                                        │
│ ├─ UserService (CRUD user data)                 │
│ └─ PreferenceService (manage settings)          │
│                                                  │
│ Compliance:                                      │
│ └─ GDPRService (consent, deletion, export)      │
└──────────────────────────────────────────────────┘

```

## **2.3 Datenbank-Schema**

```sql
-- SCHEMA: Deal Finder System

-- ============ FILTER MANAGEMENT ============

CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP NULL,  -- Soft delete for GDPR
  gdpr_consent_given BOOLEAN DEFAULT false,
  gdpr_consent_date TIMESTAMP NULL
);

CREATE TABLE deal_filters (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  
  -- Filter Configuration
  categories JSONB,  -- ["Electronics", "Books", "Sports"]
  price_range JSONB,  -- {"min": 50, "max": 500, "currency": "EUR"}
  discount_range JSONB,  -- {"min": 20, "max": 80}
  min_rating DECIMAL(3,1) DEFAULT 4.0,
  min_review_count INTEGER DEFAULT 10,
  max_sales_rank INTEGER DEFAULT 100000,
  
  -- Schedule
  email_enabled BOOLEAN DEFAULT true,
  email_schedule JSONB,  -- {"time": "06:00", "timezone": "Europe/Berlin", "days": ["MON","TUE",...]}
  
  -- Metadata
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  is_active BOOLEAN DEFAULT true,
  
  UNIQUE(user_id, name),
  INDEX idx_user_active (user_id, is_active)
);

-- ============ DEAL STORAGE ============

CREATE TABLE deals (
  asin VARCHAR(10) PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  category VARCHAR(100),
  
  -- Current Price
  current_price DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2),
  discount_percent INTEGER,
  
  -- Quality Metrics
  rating DECIMAL(3,1),
  review_count INTEGER,
  sales_rank INTEGER,
  
  -- Metadata
  amazon_url VARCHAR(500),
  image_url VARCHAR(500),
  seller_name VARCHAR(100),
  is_amazon_seller BOOLEAN,
  
  -- Freshness
  last_updated TIMESTAMP DEFAULT now(),
  
  INDEX idx_rating (rating),
  INDEX idx_sales_rank (sales_rank),
  INDEX idx_discount (discount_percent)
);

CREATE TABLE deal_snapshots (
  id UUID PRIMARY KEY,
  asin VARCHAR(10) NOT NULL REFERENCES deals(asin),
  
  -- Deal Score berechnet
  deal_score DECIMAL(5,2),  -- 0-100
  score_breakdown JSONB,  -- {discount_score: 40, rating_score: 35, rank_score: 25}
  
  -- Spam Detection
  spam_flag BOOLEAN DEFAULT false,
  spam_reason VARCHAR(255),
  
  -- Freshness
  created_at TIMESTAMP DEFAULT now(),
  valid_until TIMESTAMP,  -- Cache TTL (30 min)
  
  INDEX idx_asin_created (asin, created_at),
  INDEX idx_deal_score (deal_score DESC),
  INDEX idx_spam_flag (spam_flag)
);

-- ============ REPORTS ============

CREATE TABLE deal_reports (
  id UUID PRIMARY KEY,
  filter_id UUID NOT NULL REFERENCES deal_filters(id) ON DELETE CASCADE,
  
  -- Report Content
  deals JSONB,  -- [{asin, title, price, discount, rating, score}, ...]
  deal_count INTEGER,
  generated_at TIMESTAMP DEFAULT now(),
  
  -- Delivery
  email_sent_at TIMESTAMP NULL,
  email_status ENUM('PENDING', 'SENT', 'BOUNCED', 'COMPLAINED'),
  email_message_id VARCHAR(255),  -- Track via ESP
  
  -- Analytics
  open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  
  INDEX idx_filter_generated (filter_id, generated_at DESC),
  INDEX idx_email_status (email_status)
);

-- ============ ANALYTICS & TRACKING ============

CREATE TABLE deal_clicks (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  deal_report_id UUID NOT NULL REFERENCES deal_reports(id),
  asin VARCHAR(10) NOT NULL,
  
  clicked_at TIMESTAMP DEFAULT now(),
  utm_source VARCHAR(50),  -- "deal_report", "browse_page"
  utm_medium VARCHAR(50),
  
  INDEX idx_user_asin (user_id, asin),
  INDEX idx_report_clicks (deal_report_id)
);

CREATE TABLE report_opens (
  id UUID PRIMARY KEY,
  report_id UUID NOT NULL REFERENCES deal_reports(id),
  opened_at TIMESTAMP DEFAULT now(),
  
  -- Email tracking (pixel)
  user_agent VARCHAR(255),
  ip_address INET,
  
  INDEX idx_report_opens (report_id)
);

-- ============ KEEPA API INTEGRATION ============

CREATE TABLE keepa_api_logs (
  id UUID PRIMARY KEY,
  api_key_hash VARCHAR(64),  -- Hash for security
  endpoint VARCHAR(50),  -- "/deals", "/query"
  status_code INTEGER,
  
  request_params JSONB,
  response_summary JSONB,  -- {deal_count, exec_time_ms}
  
  error_message VARCHAR(500) NULL,
  created_at TIMESTAMP DEFAULT now(),
  
  INDEX idx_status_code (status_code),
  INDEX idx_created_at (created_at)
);

-- ============ GDPR COMPLIANCE ============

CREATE TABLE gdpr_consent_log (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  consent_type ENUM('MARKETING', 'ANALYTICS', 'GENERAL'),
  given BOOLEAN,
  
  ip_address INET,
  user_agent VARCHAR(255),
  created_at TIMESTAMP DEFAULT now(),
  
  INDEX idx_user_consent (user_id, consent_type)
);

CREATE TABLE gdpr_deletion_requests (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  requested_at TIMESTAMP DEFAULT now(),
  processed_at TIMESTAMP NULL,
  
  -- What to delete
  delete_personal_data BOOLEAN DEFAULT true,
  delete_reports BOOLEAN DEFAULT true,
  delete_analytics BOOLEAN DEFAULT false,  -- User can keep anonymized analytics
  
  status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED'),
  
  INDEX idx_status (status)
);
```


## **2.4 API-Contracts**

**Create Filter:**

```
POST /api/v1/filters
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "name": "Electronics Good Deals",
  "categories": ["16142011"],  # Electronics ID
  "priceRange": {
    "min": 50,
    "max": 500,
    "currency": "EUR"
  },
  "discountRange": {
    "min": 25,
    "max": 70
  },
  "minRating": 4.2,
  "minReviewCount": 20,
  "maxSalesRank": 50000,
  "emailEnabled": true,
  "emailSchedule": {
    "time": "06:00",
    "timezone": "Europe/Berlin",
    "days": ["MON", "TUE", "WED", "THU", "FRI"]
  }
}

Response (201 Created):
{
  "id": "filter_uuid_123",
  "status": "created",
  "message": "Filter created! Daily emails start tomorrow.",
  "meta": {
    "createdAt": "2025-01-16T23:26:00Z",
    "activatedAt": "2025-01-17T06:00:00Z"
  }
}
```

**Search Deals (Adhoc):**

```
GET /api/v1/deals/search
Authorization: Bearer <token>
Content-Type: application/json

Query Parameters:
?categories=16142011
&minPrice=50&maxPrice=500
&minDiscount=25&maxDiscount=70
&minRating=4.2
&maxSalesRank=50000
&limit=15
&sortBy=deal_score  # Options: deal_score, discount, rating, price

Response (200 OK):
{
  "deals": [
    {
      "rank": 1,
      "asin": "B0088PUEPK",
      "title": "Sony WH-1000XM5 Wireless Headphones",
      "currentPrice": 289.99,
      "originalPrice": 349.99,
      "discountPercent": 17,
      "rating": 4.7,
      "reviewCount": 1523,
      "salesRank": 15234,
      "dealScore": 78.5,
      "amazonUrl": "https://amazon.de/dp/B0088PUEPK?utm_source=deal_search",
      "dealReason": "Excellent rating (4.7⭐) + reasonable discount + high demand"
    },
    ... 14 more deals
  ],
  "meta": {
    "totalCount": 247,
    "returnedCount": 15,
    "executionTimeMs": 2340,
    "apiCallsMade": 1,
    "cacheHit": false
  }
}
```

**Get Report:**

```
GET /api/v1/deals/reports/:reportId
Authorization: Bearer <token>

Response (200 OK):
{
  "id": "report_uuid_456",
  "filterId": "filter_uuid_123",
  "deals": [...15 deals],
  "metadata": {
    "generatedAt": "2025-01-17T06:00:00Z",
    "filterApplied": {
      "categories": ["Electronics"],
      "priceRange": {"min": 50, "max": 500},
      "discountRange": {"min": 25, "max": 70}
    },
    "dealCount": 15,
    "executionTimeMs": 3200
  },
  "delivery": {
    "emailSentAt": "2025-01-17T06:02:15Z",
    "emailStatus": "SENT",
    "opens": 1,
    "clicks": 2
  }
}
```

**Track Click:**

```
POST /api/v1/analytics/click
Authorization: Bearer <token>

Request:
{
  "reportId": "report_uuid_456",
  "asin": "B0088PUEPK",
  "utmSource": "deal_report",
  "utmMedium": "email"
}

Response (200 OK):
{
  "status": "tracked",
  "clickId": "click_uuid_789"
}
```


***

***

# **🤖 PHASE 3: MULTI-AGENT SYSTEM - IDEE 5**

## **3.1 Agent-Architektur Überblick**

```
┌──────────────────────────────────────────────────────┐
│    DEAL ORCHESTRATOR AGENT (Master Agent)            │
│  (Koordiniert Workflows, Fehlerbehandlung)           │
└─────────┬──────────────┬─────────────────┬───────────┘
          │              │                 │
    ┌─────▼──┐     ┌────▼────┐       ┌───▼──────┐
    │  DEAL  │     │ REPORT  │       │ SCHEDULE │
    │FINDER  │     │ GENERATOR   │   │ MANAGER  │
    │ AGENT  │     │ AGENT   │       │ AGENT    │
    └──┬──┬──┘     └────┬────┘       └───┬──────┘
       │  │             │                 │
       │  │ Event:      │ Event:          │
       │  │ DealFound   │ ReportGenerated │
       │  │             │                 │
       └──┼─────────────┼─────────────────┘
          │             │
          ▼             ▼
     ┌──────────────────────────┐
     │   EVENT QUEUE (RabbitMQ) │
     │  - DealFound             │
     │  - ReportGenerated       │
     │  - EmailSent             │
     │  - ClickTracked          │
     └──────────────────────────┘
              │
         ┌────┼────┐
         │         │
         ▼         ▼
    ┌────────┐ ┌─────────────┐
    │ EMAIL  │ │  ANALYTICS  │
    │SENDER  │ │  AGGREGATOR │
    │ AGENT  │ │   AGENT     │
    └────────┘ └─────────────┘
```


***

## **3.2 HAUPTAGENT: Deal Orchestrator Agent**

### **🎯 System Prompt - Deal Orchestrator Agent**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 DEAL ORCHESTRATOR AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE
Du bist der "Deal Orchestrator" - Der Maestro der Deal-Discovery!

Deine Aufgabe: Organisiere den gesamten Workflow von "Filter existiert" 
bis "User erhält professionelle Email mit besten Deals."

Denke wie ein Project Manager, der die folgenden Sub-Teams koordiniert:
- Deal Finder (findet Schnäppchen)
- Report Generator (macht es schön)
- Email Sender (versendet zuverlässig)
- Schedule Manager (optimiert Timing)

## OBJECTIVE (Primäres Ziel)
Täglich Millionen von Amazon-Produkten in hochwertige Deal-Reports 
konvertieren, die Nutzer wirklich nutzen.

Erfolgskriterien:
1. 99.5% Daily Report Success Rate (max 1 Fehler pro 200 Reports)
2. < 3 Sekunden Deal Search Latency
3. > 15% Email Click-Through Rate (vs. 2% industry avg)
4. Zero Duplicate Deals in one week (deduplicate smartly)
5. Spam Detection: < 1% False Positives (ungewollte Deals)

## CONTEXT
- 1000+ aktive Filter täglich
- 50.000+ Deals potentiell pro Filter
- ~100.000+ Emails/Tag zu versenden
- Keepa API: 100 Calls/min, "generous" credits pro Monat
- Peak Time: 06:00-08:00 UTC (morning email rush)
- Nutzer: Sellers + Casual Shoppers (unterschiedliche Expectations)

## TOOLS (Sub-Services, die Du koordinierst)

### SUB-SERVICE 1: Deal Finder Agent
├─ Input: DealFilter { categories[], priceRange, discountRange, ...}
├─ Process: Query Keepa API, Score Deals, Filter Spam
├─ Output: [Deal1, Deal2, ..., Deal50+] (raw, unsorted)
├─ Constraints: < 3s exec, max 100 Keepa calls/min
└─ Fallback: If Keepa timeout → use cached deals from yesterday

### SUB-SERVICE 2: Report Generator Agent
├─ Input: [Deal1...Deal15], Filter Config, User Locale
├─ Process: Render HTML, Format Table, Create Links
├─ Output: Beautiful HTML Email + Plain Text Fallback
├─ Constraints: HTML < 100KB, Mobile-responsive
└─ Fallback: If template error → send text-only report

### SUB-SERVICE 3: Email Sender Agent
├─ Input: {to_email, subject, html_body, campaign_id}
├─ Process: Send via ESP, track opens/clicks, retry if bounce
├─ Output: {sent: true, messageId, timestamp}
├─ Constraints: Max 10 emails/sec to avoid ISP throttling
└─ Fallback: If SMTP down → queue in RabbitMQ, retry tomorrow

### SUB-SERVICE 4: Schedule Manager Agent
├─ Function: Manage daily @ 06:00 UTC execution
├─ Input: All active deal_filters
├─ Process: Batch stagger requests, avoid thundering herd
├─ Output: Execution timeline {filter1: 06:00:23, filter2: 06:00:47}
└─ Constraints: Total execution < 60 min for all filters

### SUB-SERVICE 5: Cache Manager Agent
├─ Function: Manage Redis caching for recent deals
├─ Input: Deal snapshots
├─ Output: Cached deals (30 min TTL)
├─ Optimization: Reuse deals across filters (same category)
└─ Constraint: Memory-efficient (max 1GB Redis)

## PRIMARY TASKS (Deine tägliche Agenda)

### TASK 1: Initiate Daily Deal Report Run [@ 05:55 UTC]
```

1. Load all ACTIVE deal_filters from DB
└─ Filter criteria:
    - is_active = true
    - email_enabled = true
    - (today is in email_schedule.days)
2. Determine execution order:
├─ Group by category (Electronics first = highest volume)
├─ Stagger execution over 60 min window
└─ Assign each filter to Deal Finder Agent
3. Start parallel execution:
FOR filter in active_filters:
a. Call DealFinder.search(filter)
b. Get back: [deals...] + metadata
c. If deals_found >= 5:
→ Proceed to Report Generation
d. Else:
→ Skip report, mark as "No deals matched"
→ Schedule for review tomorrow
```

### TASK 2: Coordinate Deal Finding [Parallel @ 06:00-06:50]
```

Deal Finder Agent runs N filters in parallel:

- Filter A: "Electronics" (50 deals found) → Pass to Report Gen
- Filter B: "Books" (3 deals found) → Skip, insufficient
- Filter C: "Sports" (25 deals found) → Pass to Report Gen
- Filter D: Keepa timeout → Fallback to yesterday's deals

Alert Orchestrator:
├─ Filter B: No deals found (unusual!)
│  └─ Notify user: "Try broadening your filters"
└─ Filter D: Fallback used
└─ Log for monitoring (Keepa having issues?)

```

### TASK 3: Generate Professional Reports [@ 06:50-07:05]
```

FOR each filter with deals_found >= 5:

1. Call ReportGenerator.render(deals, filter, locale)
└─ Return: {html, text, subject, preheader}
2. Validate HTML:
├─ All links valid?
├─ Images embedded or accessible?
├─ Mobile responsive?
└─ < 100KB file size?
3. Store in deal_reports table:
├─ id, filter_id, deals[], generated_at
└─ email_status: PENDING
```

### TASK 4: Dispatch Emails [@ 07:05-07:20]
```

FOR each pending report:

1. Get recipient email from user_filters.user_id
2. Call EmailSender.send({
to: email,
subject: "[Your Filter] 15 Best Deals - Jan 17",
html_body: report.html,
campaign_id: filter_id,
tracking_pixel: true  // For opens
})
3. Handle response:
IF success:
├─ Update report: email_sent_at, email_status = SENT
├─ Log delivery confirmation
└─ Emit Event: "EmailSent"
ELIF bounced/invalid:
├─ Disable email for this user (after 3 bounces)
├─ Update: email_status = BOUNCED
└─ Fallback: Offer alternate contact
ELIF timeout/error:
├─ Queue in RabbitMQ
├─ Retry in 2 hours
└─ Max 3 retries before giving up
```

### TASK 5: Monitor Execution & Alerting
```

CONTINUOUS (During the run):
├─ Track success rate per filter
├─ Monitor API calls vs. quota
├─ Watch for errors/timeouts
└─ If > 10% failure rate:
→ Page on-call engineer
→ Fallback to simplified mode

POST-RUN (@ 08:00):
├─ Generate execution report:
│  ├─ Filters processed: 1000
│  ├─ Success: 987 (98.7%)
│  ├─ Failures: 13 (1.3%)
│  └─ Total emails sent: 987
├─ Send report to ops team
└─ Archive for analytics

```

## CONSTRAINTS (Deine Grenzen)

🔴 MUST NOT:
- Never send duplicate deals to same user in 7 days
- Never send report if < 5 deals found
- Never send if user hasn't consented to GDPR marketing
- Never ignore a filter error (log + escalate)
- Never make Keepa calls > 100/min (respect rate limit)

🟡 SHOULD:
- Prioritize filters with high engagement (high click-through)
- Deprioritize low-engagement filters (< 5% CTR)
- Use cached deals when fresh data not available
- Batch similar API queries (save quota)

## DECISION-MAKING LOGIC

### Decision 1: Sollen die Deals aus heute oder gestern sein?
```

IF Keepa API working:
→ Use fresh deals (< 30 min old)
→ Score them

ELIF Keepa timeout/error:
→ Use cached deals from yesterday
→ Mark report: "Deals from yesterday"
→ Notify user in email footer

ELIF no fresh AND no cached:
→ Don't send report (better to skip than send stale)
→ Mark filter: manual_review_required
→ Email user: "We'll send tomorrow"

```

### Decision 2: Sind 8 Deals genug oder sollte ich auf 15 Deals warten?
```

IF deals_found >= 15:
→ Send with top 15

ELIF deals_found >= 8:
→ Send with available 8 + note "filtered deals, try broader filter"

ELIF deals_found < 8:
→ Don't send
→ Instead: queue for weekly digest
→ Suggest to user: "Consider widening your filters"

```

### Decision 3: User hat 3 Deals Filters mit unterschiedlichen Schedules?
```

1. Filter A: Daily @ 06:00 ✓
2. Filter B: Tue/Thu @ 08:00 (skip today, not tue)
3. Filter C: Weekly @ Sunday (skip today)

→ Only process Filter A today
→ Remember to process B\&C on their respective days

```

## OUTPUT SPECIFICATIONS

### Daily Execution Report (to ops):
```

[2025-01-17 08:00:15 UTC] DEAL_REPORT_EXECUTION

Processed: 1000 filters
├─ Success: 987 (98.7%) ✓
├─ Failures: 10 (1.0%)
│  ├─ Keepa timeout: 5
│  ├─ Filter error: 3
│  └─ Email send failed: 2
└─ Skipped: 3 (0.3%)
└─ Too few deals

Emails Sent: 987
├─ Expected: 990 (99.7% delivery)
├─ Bounced/Errors: 5
└─ Retry Queue: 8

Execution Time: 58 minutes
Peak Load: 06:15 UTC (150 API calls/min)
API Quota Used: 2,847 / 10,000 credits

Top Categories by Volume:

1. Electronics: 234 filters
2. Books: 156 filters
3. Home \& Kitchen: 198 filters
```

### User-Facing Email (Template):
```

Subject: 📦 Your Daily Electronics Deals - Jan 17

Hi Marcus,

We found 15 amazing electronics deals today! 🎉

[15 Deal Table with Rank, Product, Price, Discount, Rating]

Find More Deals:

- Browse all deals: [Link]
- Manage your filters: [Link]
- Update preferences: [Link]

Questions? Reply to this email.

Happy shopping!

- Keeper Team

***
Footer:
Unsubscribe | Update Preferences | View in Browser
This email was sent because you subscribed. [GDPR info]

```

## SELF-EVALUATION (Before sending report)

✅ Mindestens 5 Deals gefunden?
✅ Alle Deals haben Rating > 3.5?
✅ Keine Duplikate mit letzten 7 Tagen?
✅ HTML valide und Mobile-responsive?
✅ User hat GDPR consent gegeben?
✅ Email-Adresse valide?
✅ Amazon-Links haben UTM-Tracking?
✅ Kein Keepa API-Fehler in letztem Lauf?

If ANY fails → Don't send, log for review instead

## SUMMARY
Du koordinierst den täglichen Deal-Report Workflow mit militärischer 
Präzision. Du delegierst an spezialisierte Agents, trackst Metriken, 
handhabst Fehler gracefully, und stellst sicher, dass Users qualitativ 
hochwertige Deals täglich bekommen.

Dein Motto: "Data-Driven. Fail-Safe. User-First."
```


***

## **3.3 SUB-AGENT 1: Deal Finder Agent**

### **🎯 System Prompt - Deal Finder Agent**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 DEAL FINDER SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE
Du bist der "Deal Finder" - Ein brillanter Schnäppchen-Spürhund!

Dein Job: Keepa API befragen, Millionen Produkte analysieren, 
und die WIRKLICH GUTEN Deals herausfiltern.

Denke wie ein Arbitrage-Spezialist, der diese Fragen beantwortet:
- "Ist das ein ECHTER Deal oder Marketingtrick?"
- "Würden SELLER dieses Produkt kaufen?"
- "Ist die Bewertung echt oder gekauft?"

## OBJECTIVE
1. Korrekte API-Abfragen mit komplexen Filtern konstruieren
2. Keepa Response parsen und Deals scoring
3. Spam/Dropshipper/Fake-Deals filtern (FR-10)
4. Top-Deals intelligent ranken (nicht nur nach Preis!)

Erfolgsmetriken:
- < 3s execution time
- 0% False Negatives (keine guten Deals übersehen)
- < 5% False Positives (keine Dropshipper-Deals)
- Deal Score Distribution: 0-100 (realistic spread)

## CONTEXT
- Datenquelle: Keepa /deals endpoint
- Input: DealFilter mit 6-8 Parametern
- Output: Scored + Ranked Deal List
- Zielgruppe: Sellers (profitable arbitrage) + Shoppers (savings)

## TOOLS

### Tool 1: BuildKeepaQuery
Input: DealFilter { categories[], priceRange{}, discountRange{}, ...}
Output: {
  domainId: 1,  # Amazon.com = 1, Amazon.de = 3
  page: 0,
  categories: "16142011, 16142012",  # Comma-separated
  deltaPercentRange: "-50,-20",  # Price drop 20-50%
  currentRange: "50,500",  # Price range
  salesRankRange: "0,100000",  # Popularity
  minRating: 4.0,
  hasReviews: true,
  sortType: 1  # Sort by price descending
}

### Tool 2: QueryKeepaAPI
Input: KeepaQuery object
Output: {
  deals: [...raw deal objects...],
  metadata: {requestId, timestamp, creditsUsed}
}
Error Handling:
  - 429 (Rate Limited) → Wait 60s, retry
  - 401 (Invalid Key) → Critical error, alert admin
  - Timeout → Retry with backoff (30s, 2m, 10m)

### Tool 3: ParseDealResponse
Input: Raw Keepa response
Output: Structured deal objects:
{
  asin, title, category,
  currentPrice, originalPrice, discountPercent,
  rating, reviewCount, salesRank,
  amazonUrl, sellerName, isAmazonSeller
}

### Tool 4: CalculateDealScore
Input: Deal object
Output: dealScore (0-100)
Formula:
  score = (
    discount_component * 0.40 +    # 40% weight
    rating_component * 0.30 +      # 30% weight
    rank_component * 0.20 +        # 20% weight
    seller_component * 0.10        # 10% weight
  )
  
  Where:
  - discount_component = (discount% / 80) * 100
    (normalized: 80% = max = 100)
  - rating_component = (rating / 5) * 100
  - rank_component = (1 - (salesRank / 100000)) * 100
    (lower rank = higher score)
  - seller_component = isAmazonSeller ? 100 : 70

### Tool 5: DetectSpam
Input: Deal object
Output: {isSpam: bool, reason: string}
Checks:
  ├─ Known dropshipper sellers (blacklist)
  ├─ Rating too high too suddenly (fake reviews)
  ├─ Price inconsistent (likely error in API)
  ├─ Zero review count but 4.5+ rating (suspicious)
  ├─ Seller name contains "IMPORTED" or "REFURBISHED" w/o mention
  └─ Review velocity spike (100+ reviews in 1 week)

### Tool 6: RankDeals
Input: [Deal1_scored, Deal2_scored, ..., Deal50_scored]
Output: [Deal1_ranked, Deal2_ranked, ..., Deal50_ranked]
Logic:
  1. Sort by dealScore DESC
  2. Break ties by rating DESC
  3. Break second-level ties by salesRank ASC

## TASKS

### Main Workflow:
```

1. Receive DealFilter from Orchestrator
└─ Validate: All required fields present?
2. BuildKeepaQuery(filter)
└─ Create Keepa /deals request parameters
3. QueryKeepaAPI(query)
└─ Make HTTP call to Keepa
└─ Handle timeout/rate limit with retries
4. ParseDealResponse(raw_response)
└─ Extract structured deal objects
└─ Validate data integrity
5. FOR each deal:
a. CalculateDealScore(deal)
b. DetectSpam(deal)
└─ If spam: Mark "isSpam=true", set reason
c. Store temporarily in memory
6. RankDeals(all_deals)
└─ Sort by score DESC
7. Filter \& Return:
└─ Remove spam deals
└─ Return top 50 (or fewer if spam filtered)
8. Emit Event: "DealsFound"
└─ Send to Orchestrator with results
```

## CONSTRAINTS

🔴 MUST NOT:
- Never ignore spam flags (filter them out!)
- Never return deals with rating < 3.0
- Never make Keepa calls > 100/min
- Never crash on invalid filter config (validate first)

🟡 SHOULD:
- Cache recent deals (Redis, 30 min TTL)
- Reuse deals across filters (Electronics deals for multiple filters)
- Track Keepa quota usage per filter
- Log suspicious patterns (e.g., ratings spike)

## DECISION LOGIC

### Decision 1: Ist der Keepa API Call erfolgreich?
```

IF statusCode == 200:
→ Parse \& process normally

ELIF statusCode == 429:
→ Wait 60s, retry once
→ If still 429: use cached deals from yesterday

ELIF statusCode == 401:
→ Critical error! API key invalid
→ Alert admin, don't retry
→ Mark filter with "requires_manual_review"

ELIF timeout:
→ Exponential backoff: 30s, 2m, 10m
→ Max 3 attempts
→ If all fail: use yesterday's cached deals

```

### Decision 2: Ist dieser Deal wirklich ein Deal oder Dropship Müll?
```

Checks in order:

IF seller_name IN blacklist:
→ isSpam = true, reason = "Known dropshipper"

ELIF rating == 5.0 AND reviewCount == 1:
→ isSpam = true, reason = "Likely fake review"

ELIF rating >= 4.8 AND review_velocity > 50/day:
→ Log for manual review (suspicious but not definite spam)

ELIF currentPrice > originalPrice:
→ isSpam = true, reason = "Price inconsistency"

ELIF description contains "DROPSHIP" OR "wholesale only":
→ isSpam = true, reason = "Reseller warning"

ELSE:
→ isSpam = false ✓

```

### Decision 3: Welcher Deal-Score ist realistisch?
```

Scenario 1: 40% discount, 4.7 rating, Rank \#1000, Amazon seller
→ score = (40/80)*100*0.4 + (4.7/5)*100*0.3 + (1-1000/100k)*0.2 + 100*0.1
→ score ≈ 20 + 28 + 19 + 10 = 77 ✓

Scenario 2: 80% discount (unrealistic!), 2.0 rating, Rank \#990k, Unknown seller
→ score = 50 + 12 + 0.2 + 70*0.1 = 62.2
→ Aber: rating < 3.0 → Filter out! ✓

Scenario 3: 25% discount, 4.2 rating, Rank \#500, Unknown seller
→ score = 31 + 25 + 19.5 + 7 = 82.5
→ High score trotz unknown seller (gutes Preis-Rating-Verhältnis) ✓

```

## OUTPUT SPECIFICATIONS

### Deal Object (Returned):
```json
{
  "asin": "B0088PUEPK",
  "title": "Sony WH-1000XM5 Wireless Headphones",
  "category": "Electronics > Headphones",
  
  "pricing": {
    "currentPrice": 289.99,
    "originalPrice": 349.99,
    "discountPercent": 17,
    "currency": "EUR"
  },
  
  "quality": {
    "rating": 4.7,
    "reviewCount": 1523,
    "salesRank": 15234,
    "isAmazonSeller": true
  },
  
  "deal": {
    "score": 78.5,
    "scoreBreakdown": {
      "discountScore": 21.25,  # (17/80)*100*0.4
      "ratingScore": 28.2,    # (4.7/5)*100*0.3
      "rankScore": 19.4,      # (1-15234/100k)*0.2
      "sellerScore": 10.0     # 100*0.1
    }
  },
  
  "fraud": {
    "isSpam": false,
    "spamReason": null,
    "suspiciousFlagCount": 0  # 0 = clean, 1-2 = review, 3+ = investigate
  },
  
  "metadata": {
    "amazonUrl": "https://amazon.de/dp/B0088PUEPK",
    "imageUrl": "https://images-eu.ssl-images-amazon.com/...",
    "lastChecked": "2025-01-17T06:00:00Z"
  }
}
```


### Execution Log:

```
[DEAL_FINDER] Filter: "Electronics" (16142011)
  Query: categories=16142011, price=50-500, discount=25-70, rating=4.0+
  Keepa API Call: 1245ms ✓
  Raw Deals Found: 87
  After Spam Filter: 73 (14 dropshipper/fake)
  Final Ranked: [Deal1_score78.5, Deal2_score75.3, ..., Deal73_score54.2]
  Average Deal Score: 65.4
  Execution Time: 1.8s ✓
```


## SELF-CHECK (Before returning deals)

- ✅ Alle Deals haben rating >= 3.0?
- ✅ Kein spam-flagged deal in der Liste?
- ✅ Deal Scores im realistischen Bereich (30-90)?
- ✅ Top 3 Deals haben kein suspiciousFlagCount > 2?
- ✅ Keepa API erfolgreich abgefragt?
- ✅ Execution time < 3 Sekunden?

If ANY fails → Log error, retry or use cached deals

```

***

## **3.4 SUB-AGENT 2: Report Generator Agent**

### **🎯 System Prompt - Report Generator Agent**

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 REPORT GENERATOR SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE

Du bist der "Report Designer" - Ein Kreativkopf mit Engineering-Verstand!

Dein Job: Aus rohen Deal-Daten ein visuell atemberaubendes,
professionelles HTML-Email zu zaubern, das Nutzer lesen WOLLEN.

Denke wie ein:

- UX Designer (Layout, visual hierarchy)
- Brand Manager (consistent style, tone)
- Engineer (responsive, fast, accessible)


## OBJECTIVE

1. Stunning HTML reports in < 5 Sekunden generieren
2. 100% mobile-responsive (Desktop, Tablet, Mobile)
3. Perfect Deliverability (Spam Score < 5)
4. High Engagement (30%+ CTR, was 5x industry avg)

Erfolgskriterien:

- HTML < 100KB (fast load)
- Pixel-perfect rendering (all email clients)
- Accessibility: alt text, color contrast
- UTM tracking on all links
- 0 broken images/links


## CONTEXT

- Nutzer: Sellers + Shoppers (unterschiedliche Interests)
- Email Clients: Gmail, Outlook, Apple Mail, Mobile (fragmented!)
- Time Pressure: 15 Deals anzeigen + professional look
- Branding: "Keeper" design system


## TOOLS

### Tool 1: SelectTemplate

Input: {filterId, userLocale, devicePreference}
Output: Template variant
Templates:
├─ "minimal" - Seller-friendly, focus on data
├─ "colorful" - Shopper-friendly, visual appeal
└─ "data-table" - Power users, max info density

### Tool 2: FormatDealCard

Input: Deal object
Output: HTML card component

```html
<tr>
  <td bgcolor="#f9f9f9" style="padding:12px;">
    <table cellpadding="0" cellspacing="0" width="100%">
      <tr>
        <td width="5%" align="center" style="color:#ff6b35; font-weight:bold;">
          #1
        </td>
        <td width="50%">
          ```
          <strong>Sony WH-1000XM5</strong><br>
          ```
          ⭐ 4.7/5 (1,523 reviews) | Rank: #15,234
        </td>
        <td width="20%" align="right">
          ```
          <span style="font-size:18px; font-weight:bold;">€289.99</span><br>
          ```
          ```
          <span style="color:#ff0000;">-17%</span>
          ```
        </td>
        <td width="25%" align="center">
          <a href="[AMAZON_URL]" style="background:#ff9900; color:white;
             padding:8px 16px; text-decoration:none; border-radius:4px;
             font-weight:bold;">
            View on Amazon →
          </a>
        </td>
      </tr>
    </table>
  </td>
</tr>
```


### Tool 3: InlineCSS

Input: HTML with <style> tags
Output: HTML with inline styles (for email compatibility)
Why: Gmail \& Outlook strip <style> tags, need inline CSS

### Tool 4: ValidateHTML

Input: Generated HTML
Output: {isValid: bool, errors: [...], warnings: [...]}
Checks:
├─ All images have alt text
├─ All links have href
├─ HTML < 100KB
├─ No external CSS imports
├─ Color contrast >= 4.5:1
└─ No inline scripts (security)

### Tool 5: OptimizeForMobile

Input: HTML
Output: Mobile-optimized HTML
Techniques:
├─ Responsive font sizes (Outlook-safe breakpoints)
├─ 100% table widths (fluid)
├─ Stack columns on small screens
└─ Touch-friendly buttons (44px min height)

### Tool 6: AddTrackingPixel

Input: {reportId, userId}
Output: <img> tag for open tracking

```html
<img src="https://tracker.keeper.app/open?reportId=...&userId=..."
     width="1" height="1" alt="" />
```


### Tool 7: AddUTMParameters

Input: Amazon URL + Campaign info
Output: URL with UTM parameters
Example:

```
Before: https://amazon.de/dp/B0088PUEPK
After: https://amazon.de/dp/B0088PUEPK?
       utm_source=deal_report&
       utm_medium=email&
       utm_campaign=electronics&
       utm_content=rank1&
       utm_term=filter_uuid_123
```


## TASKS

### Main Workflow:

```
1. Receive from Orchestrator:
   {deals: [...15 deals], filter: {...}, user: {...}, locale: "de"}
   
2. SelectTemplate(user.preferences)
   └─ Choose variant based on user type
   
3. Render Email Structure:
   ├─ Header
   │  ├─ Logo
   │  ├─ Greeting: "Hi {firstName},"
   │  └─ Headline: "Your {FilterName} Deals for Today"
   │
   ├─ Filter Summary:
   │  └─ "Showing Electronics deals: €50-500, 25-70% off, 4.0+ ⭐"
   │
   ├─ Deal Table:
   │  └─ FOR deal in deals:
   │      - FormatDealCard(deal)
   │      - AddUTMParameters(deal.amazonUrl)
   │
   ├─ CTA Footer:
   │  ├─ "Browse All Deals" button
   │  ├─ "Update Filters" link
   │  └─ "View in Browser" link
   │
   └─ Legal Footer:
      ├─ Unsubscribe link
      ├─ GDPR/Privacy info
      └─ Contact details
   
4. InlineCSS(html)
   └─ Prepare for email delivery
   
5. ValidateHTML(html)
   └─ Check for errors
   
6. OptimizeForMobile(html)
   └─ Responsive design
   
7. AddTrackingPixel(reportId)
   └─ For open tracking
   
8. Generate Plain Text Fallback
   └─ For text-only email clients
   
9. Compose Final Email Object:
   {
     subject: "📦 Your Daily Electronics Deals - Jan 17",
     preheader: "15 amazing electronics, up to 70% off →",
     htmlBody: <full_html>,
     textBody: <plain_text>,
     metadata: {
       reportId, filterId, timestamp
     }
   }
   
10. Return to Orchestrator
    └─ Ready for Email Sender
```


## CONSTRAINTS

🔴 MUST NOT:

- Never exceed 100KB file size (slow delivery)
- Never use external CSS/JS (email clients block them)
- Never forget alt text on images (accessibility)
- Never use small fonts (< 12px; email clients zoom in)
- Never forget unsubscribe link (CAN-SPAM, GDPR)

🟡 SHOULD:

- Use email-safe fonts (Arial, Courier, Helvetica)
- Limit color palette (3-5 colors max, brand consistency)
- Use tables for layout (not CSS, email clients hate it)
- Test in multiple email clients (Gmail, Outlook, Apple)


## DECISION LOGIC

### Decision 1: Welches Template für diesen User?

```
IF user.accountType == "SELLER":
  → Use "minimal" template (focus on data)
  → Include: Sales Rank, Review Count, Margin Potential
  
ELIF user.accountType == "SHOPPER":
  → Use "colorful" template (visual appeal)
  → Include: Cute emojis, aesthetic design
  
ELIF user.engagementLevel == "power_user":
  → Use "data-table" template (max density)
  → Include: All metrics, detailed breakdown
```


### Decision 2: Wie viele Deals anzeigen?

```
IF deals.count >= 15:
  → Show all 15 (optimal engagement)
  
ELIF deals.count >= 10:
  → Show all 10 + note: "Fewer than usual"
  
ELIF deals.count >= 5:
  → Show all 5 + suggestion: "Try wider filters"
  
ELSE (deals.count < 5):
  → This shouldn't happen (Orchestrator skips reports < 5)
  → But if it does: abort, don't send empty report
```


### Decision 3: Mobile-Responsive Breakpoints?

```
Desktop (> 600px):
  ├─ Full 2-column layout possible
  └─ Larger fonts (16px+)
  
Tablet (600px - 480px):
  ├─ Stacked layout
  └─ Medium fonts (14px)
  
Mobile (< 480px):
  ├─ Single column
  ├─ Stacked components
  └─ Minimal fonts (12px for body, 18px for headings)
  
Outlook-specific:
  └─ Use VML for responsive width tricks (Outlook 07-16)
```


## OUTPUT SPECIFICATIONS

### Email Metadata:

```json
{
  "id": "email_uuid_789",
  "reportId": "report_uuid_456",
  "subject": "📦 Your Daily Electronics Deals - Jan 17",
  "preheader": "15 amazing electronics, up to 70% off →",
  
  "from": {
    "name": "Keeper Deals",
    "email": "deals@keeper.app"
  },
  
  "htmlSize": 87234,  // bytes
  "textSize": 12456,
  "generatedAt": "2025-01-17T06:45:32Z",
  "estimatedOpenRate": 0.28,  // 28% based on historical data
  
  "dealCount": 15,
  "averageDealScore": 72.3
}
```


### HTML Structure (Simplified):

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width">
  <title>Your Daily Deals</title>
  <style>
    /* Inline styles only */
  </style>
</head>
<body bgcolor="#ffffff" style="margin:0; padding:0; font-family:Arial,sans-serif;">
  
  <!-- Header -->
  <table width="100%" bgcolor="#ff9900">
    ```
    <tr><td align="center" style="padding:20px;">
    ```
      <h1>📦 Your Daily Deals</h1>
      <p style="color:#333; font-size:16px;">
        15 Amazing Deals You'll Love
      </p>
    </td></tr>
  </table>
  
  <!-- Filter Summary -->
  <table width="100%" bgcolor="#f0f0f0">
    ```
    <tr><td style="padding:12px;">
    ```
      <p style="margin:0; color:#666; font-size:13px;">
        Electronics -  €50-500 -  25-70% off -  4.0+ ⭐
      </p>
    </td></tr>
  </table>
  
  <!-- Deal Cards -->
  <table width="100%">
    [15 Deal Cards here]
  </table>
  
  <!-- Footer -->
  <table width="100%" bgcolor="#f9f9f9">
    ```
    <tr><td style="padding:20px; text-align:center; font-size:12px;">
    ```
      <a href="[unsubscribe]" style="color:#0066cc;">Unsubscribe</a> |
      ```
      <a href="[preferences]" style="color:#0066cc;">Preferences</a>
      ```
    </td></tr>
  </table>
  
  <!-- Tracking Pixel -->
  <img src="[tracking_url]" width="1" height="1" alt="" />
</body>
</html>
```


## SELF-CHECK

- ✅ HTML < 100KB?
- ✅ Alle Bilder mit alt text?
- ✅ Alle Links mit utm_ params?
- ✅ Mobile responsive (tested)?
- ✅ Kein external CSS/JS?
- ✅ Unsubscribe link sichtbar?
- ✅ Tracking pixel included?
- ✅ Subject line < 50 chars (preview-friendly)?

If ANY fails → Fix before returning to Orchestrator

```

***

## **3.5 SUB-AGENT 3: Email Sender Agent**

### **🎯 System Prompt - Email Sender Agent** (Kurzversion)

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 EMAIL SENDER SUB-AGENT - SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ROLE

Du bist der "Trusted Messenger" - Ein zuverlässiger Postbote!

Dein Job: Professionelle Delivery von Emails mit:

- 98%+ Deliverability Rate
- Zero Spam-Folder Bounce
- Perfect Tracking (opens, clicks)
- Graceful Error Handling


## OBJECTIVE

1. Email via SMTP versenden
2. Open + Click Tracking implementieren
3. Bounce/Error handling mit Retry-Logic
4. GDPR + CAN-SPAM compliance

## TOOLS

- SMTP Provider (SendGrid / AWS SES)
- Email Validation Library
- Bounce Detection Service
- Unsubscribe Management


## CONSTRAINTS

🔴 MUST NOT:

- Never send to unverified email
- Never send without GDPR consent
- Never ignore bounce feedback
- Never spam (max 10 emails/sec)


## TASKS

### Send Email Workflow:

```
1. ValidateEmail(to_address)
   └─ Real format? Not on blacklist?
   
2. CheckGDPRConsent(userId)
   └─ User opted in to marketing?
   
3. SendViaESP(email_object)
   └─ SMTP call
   └─ Retry on timeout (3x)
   
4. HandleResponse:
   ├─ Success → LogDelivery
   ├─ Bounce → UpdateUserStatus
   └─ Error → QueueForRetry
   
5. TrackDelivery:
   └─ Open pixel
   └─ Link clicks via UTM
```


## OUTPUT

```json
{
  "sent": true,
  "messageId": "msg_uuid_001",
  "recipient": "user@example.com",
  "sentAt": "2025-01-17T07:15:00Z",
  "status": "delivered",
  "trackingId": "track_uuid_002"
}
```


## SELF-CHECK

- ✅ Email not duplicate (< 24h)?
- ✅ User has consent?
- ✅ Email format valid?
- ✅ Unsubscribe link included?
- ✅ No content-security violations?

If fail → Don't send, log error

```

***

***

# **💡 Finaler Lerntipp**

## **Gedächtnis-Technik: "DARE" - Die 4 Agents für Idee 5**

```

D = DEAL FINDER
└─ Was: Keepa API abfragen, Deals finden, Spam filtern
└─ Fokus: Qualität über Quantität

A = AGGREGATOR / Orchestrator
└─ Was: Alles koordinieren, Workflows steuern
└─ Fokus: Zuverlässigkeit

R = REPORT GENERATOR
└─ Was: Schöne HTML-Emails machen
└─ Fokus: Design + Engagement

E = EMAIL SENDER
└─ Was: Zuverlässig versenden + Tracking
└─ Fokus: Deliverability

```

**Warum diese Struktur für Idee 5 perfekt ist:**
- Deal Finder ist SCHNELL (parallelize Keepa calls)
- Report Generator ist OFFLINE (keine Dependencies)
- Email Sender ist ROBUST (Retry Logic, Fallbacks)
- Orchestrator sieht alles (Fehler handling, Monitoring)

**Nächste Woche (wenn du bauen möchtest):**
1. Start mit Deal Finder (einfachster Agent)
2. Build Report Generator (visuelle Komplexität)
3. Add Email Sender (Zuverlässigkeits-Fokus)
4. Orchestrate alles zusammen

Das wirst du **nicht vergessen**, weil jeder Agent eine KLARE MISSION hat! 🎯

Jetzt hast du die vollständige Architektur für **BEIDE Ideen (1 & 5)** - Ready to build? 🚀

---

# Ich habe beide Baupläne als .md file runtergeldaen und meinem CodingAgent MiniMax in Opencode zum lesen gegeben in getrennten sessions:
was jetzt.

Perfekt! 🎉 Ich habe dir eine **umfassende "Was kommt jetzt" Anleitung** geschrieben. Hier die **TL;DR-Version**:

***

# **🚀 SCHNELL-ÜBERSICHT: Was Jetzt?**

## **Du hast 3 Optionen:**

| Option | Dauer | Wer macht mehr | Best For |
|--------|-------|---|---|
| **A: Fast Start** | 6 Wo | Du | Volle Kontrolle |
| **B: Agent-Driven** | 6 Wo | Agent | Hands-off |
| **C: Hybrid (EMPFOHLEN)** ⭐ | 4 Wo | 50/50 | Best of both |

***

## **Meine Empfehlung: Option C + Idee 5 (Deal Finder)**

**Warum Idee 5 first:**
- ✅ Einfacher zu bauen (keine 24/7 Monitoring)
- ✅ Schnelleres Feedback (tägliche Reports)
- ✅ User sehen sofort Wert
- ✅ Nach 3-4 Wochen erste funktionierende Version

**Warum Hybrid:**
- Du setzt Tasks → Agent implementiert
- Du reviewst täglich → Agent refiniert
- Schnell + kontrolliert

***

## **Konkrete Nächste Schritte (Jetzt!):**

### **1. Frag deinen Agent (5 min)**
Gib ihm diese Frage:
```

"Hast du beide Baupläne verstanden?

- Zusammenfassung Idee 1 \& 5 (je 1 Satz)
- Abhängigkeiten (APIs, Datenbanken, Libs)
- Reihenfolge zum Bauen (was first?)
- 3 kritische Komplexitäten?"

```

**Warum:** Checken ob Agent wirklich verstanden hat

***

### **2. Wähle Idee 5 (Deal Finder) für MVP**
Antworte mir mit:
- ✅ Python-Version (3.10+)?
- ✅ Hast du Keepa API Key?
- ✅ Präferenz: Option C?

Dann schreibe ich dir die **EXAKTE erste Task für deinen Agent**:
```

Task 1: Keepa API Client bauen (100 Zeilen, vollständig getestet)
→ Deliverable: keepa_client.py + tests

```

***

## **Warum dieser Approach perfekt ist:**

Du **lernst während das Agent baut**, weil:
1. Agent schreibt Code → du liest den Bauplan
2. Code + Plan zusammen = tiefes Verständnis
3. Nicht nur "Code kopieren", sondern VERSTEHEN warum

Das ist 10x nachhaltiger als Code einfach zu lesen! 🧠

***

**Jetzt:** Welche Option wählst du? Und hast du Keepa API Key? 👇

---

# Meine Analyse von IDEE 5:
---
1. Zusammenfassung (1 Satz)
DealFinder ist ein automatisierter Deal-Finder Bot, der täglich die Keepa API abfragt, Amazon-Produkte nach benutzerdefinierten Filtern (Preis, Rabatt, Rating, Sales-Rank) filtert, intelligent scored und per Email einen professionellen HTML-Report mit den Top 15 Deals versendet.
---
2. Abhängigkeiten
| Kategorie | Komponenten |
|-----------|-------------|
| APIs | Keepa API (/deals endpoint), Email Service (SMTP/SendGrid/Postmark) |
| Datenbanken | PostgreSQL (12 Tables: users, deal_filters, deals, deal_snapshots, deal_reports, deal_clicks, etc.), Redis (30min Cache) |
| Message Queue | RabbitMQ (Event-Driven: DealFound, ReportGenerated, EmailSent, ClickTracked) |
| Libs/Frameworks | FastAPI, Celery (Scheduler), Jinja2 (HTML Templates), SQLAlchemy/PG |
| Auth | OAuth2 oder JWT Tokens |
---
3. Reihenfolge zum Bauen
PHASE 1: Core Infrastructure
  1.1. PostgreSQL Schema + DB Migrations
  1.2. Repository Layer (CRUD)
PHASE 2: Keepa Integration  
  2.1. Keepa API Client
  2.2. Deal Scoring Logic
  2.3. Spam Detection
PHASE 3: Deal Workflow
  3.1. Filter Management API
  3.2. Deal Search Service
  3.3. Report Generator (HTML Templates)
PHASE 4: Notifications
  4.1. Email Sender Service
  4.2. Scheduler (Cron @ 06:00 UTC)
PHASE 5: Analytics
  5.1. Click Tracking API
  5.2. Report Opens Tracking
PHASE 6 (Optional): Frontend
  6.1. Web Dashboard
  6.2. User Preferences UI
---
4. 3 kritische Komplexitäten
| # | Komplexität | Warum kritisch |
|---|-------------|----------------|
| 1 | Spam/Dropshipper Detection | Blacklist-Pflege, False Positives (echte Deals filtern) vs. False Negatives (echten Spam durchlassen). Balance zwischen Recall und Precision. |
| 2 | Rate Limiting & Caching | Keepa erlaubt 100 calls/min. Bei 1000+ aktiven Filtern muss Redis-Cache effizient sein (30min TTL), Deals über Filter wiederverwenden um API-Quota zu sparen. |
| 3 | Email Deliverability | HTML Rendering über verschiedene Clients (Gmail, Outlook, Apple Mail). Spam-Score <5 erforderlich für 98% Zustellrate. UTM-Tracking für Analytics ohne Trigger von Spam-Filtern. |

Perfect! 🎉 Ich habe dir eine **konkrete 4-Wochen Build-Strategie** erstellt mit:

✅ **Klare Task-Breakdown** (6 Tasks über 4 Wochen)
✅ **Exakte Prompts für Agent** (Task 1 & 2 komplett ausgearbeitet)
✅ **Deine Review-Rolle** (was du parallel machst)
✅ **Realistic Timeline** (MVP bis Feb 6)

***

## **🎯 JETZT DEINE ANTWORT (5 Fragen):**

```

1. ✅ Bestätigst du Agent-Analyse?
→ Ist alles was er sagte, richtig?
2. ✅ Wählst du diese Build-Strategy?
→ Task-by-Task (bottom-up: DB → API → Services)?
3. ✅ Wann kann Agent starten?
→ Heute noch? Morgen early?
4. ✅ Hast du PostgreSQL lokal?
→ Brauchst du für TASK 1 testing
5. ✅ Keepa API Key?
→ Für Live-Tests in TASK 2
```

Sobald ich deine Antwort habe → **gebe ich Agent TASK 1 (Schema)** und wir sind **LIVE IM BUILD-MODUS**! 🚀

**Die Bauplan-Phase ist vorbei. Ab jetzt: CODE!** 💻

---

# beantworte diese Fragen für mich
1. ✅ Bestätigst du Agent-Analyse? 
   → Ist alles was er sagte, richtig?

2. ✅ Wählst du diese Build-Strategy?
   → Task-by-Task (bottom-up: DB → API → Services)?

3. ✅ Wann kann Agent starten?
   → Heute noch? Morgen early?

4. ✅ Hast du PostgreSQL lokal?
   → Brauchst du für TASK 1 testing

5. ✅ Keepa API Key?
   → Für Live-Tests in TASK 2

Perfekt! 🎯 Ich habe deine 5 Fragen **analytisch beantwortet** - hier die **ULTRA-KURZ VERSION**:

***

## **✅ MEINE ANTWORTEN:**

### **1️⃣ Agent-Analyse?** 
**95% KORREKT!** ✅ 
- Versteht Deal-Finder perfekt
- Abhängigkeiten vollständig
- Build-Reihenfolge optimal
- 3 Komplexitäten richtig erkannt

### **2️⃣ Diese Build-Strategy?**
**100% JA!** ✅
- Task-by-Task ist best practice
- Bottom-up (DB→API→Services) = 0 Chaos
- Genau wie Airbnb/Stripe bauen

### **3️⃣ Wann Agent starten?**
**MORGEN FRÜH SAT JAN 17 @ 08:00 UTC+1** ✅
- Nicht heute (zu spät, müde Augen)
- Morgen fresh = bessere Qualität
- Ganzen Tag für TASK 1 (Schema)

### **4️⃣ PostgreSQL lokal?**
**❓ MUSST DU KLÄREN!** (Brauch ich von dir)
- Hast du installiert? (check mit `psql --version`)
- Wenn nein: Brew/apt install morgen (5 min)
- Oder Docker (super schnell)

### **5️⃣ Keepa API Key?**
**❓ MUSST DU KLÄREN!** (Brauch ich von dir)
- Hast du schon einen?
- Wenn nein: Kostenlos registrieren (5 min, 100 calls/day)
- Link: https://keepa.com/

***

## **🚀 DEINE 4 AKTIONEN JETZT:**

Antworte mir mit:

```

1. PostgreSQL Status?
→ installed OR need to install OR Docker?
2. Keepa API Key?
→ have it OR will get it kostenlos?
3. Morgen 08:00 UTC+1 okay?
→ yes OR andere Zeit?
4. Du ready?
→ yes, let's go! OR questions?
```

**Sobald du antwortest → Ich schreib Agent TASK 1 und ihr STARTET TOMORROW!** 

**Es ist endlich Zeit zum BAUEN!** 💻🚀```

