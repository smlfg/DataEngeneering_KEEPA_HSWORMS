# Streamlit - Dashboard Framework

## Was ist Streamlit?

**Streamlit** ist ein Python-Framework zum Erstellen **interaktiver Web-Dashboards** ohne HTML/CSS/JavaScript.

### Der Unterschied zu klassischer Web-Entwicklung

| **Klassisch (HTML/JS)** | **Streamlit** |
|------------------------|---------------|
| HTML + CSS + JavaScript | Nur Python |
| React/Vue/Angular | Keine Frontend-Kenntnisse nötig |
| API-Calls manuell | Automatisches Caching |
| Komplex | Sehr einfach |

**Beispiel:**

```python
# streamlit_app.py
import streamlit as st

st.title("Arbitrage Dashboard")
st.write("Hello World!")

number = st.slider("Wähle eine Zahl", 0, 100)
st.write(f"Du hast {number} gewählt")
```

**Starten:**
```bash
streamlit run streamlit_app.py
```

**Ergebnis:** Sofort ein Web-Dashboard auf http://localhost:8501

## Kernkonzepte

### 1. **Widgets** (Eingabe-Elemente)

Widgets ermöglichen **User-Interaktion**.

```python
import streamlit as st

# Text-Eingabe
name = st.text_input("Dein Name")

# Zahl
age = st.number_input("Dein Alter", min_value=0, max_value=120)

# Slider
margin = st.slider("Mindest-Marge (%)", 0, 50, 10)

# Dropdown
market = st.selectbox("Markt", ["DE", "UK", "IT", "ES", "FR"])

# Multi-Select
markets = st.multiselect("Märkte", ["DE", "UK", "IT", "ES", "FR"])

# Checkbox
show_details = st.checkbox("Details anzeigen")

# Button
if st.button("Daten laden"):
    st.write("Button geklickt!")

# Radio Buttons
choice = st.radio("Wähle eine Option", ["Option A", "Option B"])

# Date Picker
import datetime
date = st.date_input("Datum", datetime.date.today())
```

### 2. **Display-Elemente** (Ausgabe)

```python
# Text
st.write("Einfacher Text")
st.markdown("**Fettgedruckter** Text")
st.title("Großer Titel")
st.header("Header")
st.subheader("Subheader")

# Daten
st.json({"key": "value"})
st.code("print('Hello')", language="python")

# Dataframe
import pandas as pd
df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
st.dataframe(df)
st.table(df)

# Metriken
st.metric(label="Produkte", value=1234, delta="+100")

# Charts
st.line_chart(df)
st.bar_chart(df)
st.area_chart(df)

# Bilder
st.image("https://example.com/image.jpg")
```

### 3. **Layout** (Seitenstruktur)

```python
# Spalten
col1, col2 = st.columns(2)

with col1:
    st.write("Linke Spalte")

with col2:
    st.write("Rechte Spalte")

# Sidebar
with st.sidebar:
    st.write("Sidebar-Inhalt")
    filter_value = st.slider("Filter", 0, 100)

# Expander (Aufklappbar)
with st.expander("Mehr Details"):
    st.write("Versteckter Inhalt")

# Tabs
tab1, tab2 = st.tabs(["Übersicht", "Details"])

with tab1:
    st.write("Übersicht-Tab")

with tab2:
    st.write("Details-Tab")

# Container
container = st.container()
container.write("Container-Inhalt")
```

### 4. **Caching** (Performance)

Streamlit führt das **komplette Skript** bei jeder Interaktion **neu aus**.

**Problem:** API-Calls bei jedem Slider-Move

**Lösung:** Caching

```python
import streamlit as st
import requests

@st.cache_data(ttl=60)  # Cache 60 Sekunden
def fetch_opportunities(min_margin):
    response = requests.get(
        "http://api:8000/opportunities",
        params={"min_margin": min_margin}
    )
    return response.json()

# UI
min_margin = st.slider("Mindest-Marge", 0, 50, 10)

# Wird nur bei neuem min_margin aufgerufen, sonst gecacht
opportunities = fetch_opportunities(min_margin)

st.write(f"Gefunden: {len(opportunities)} Opportunities")
```

**Cache-Typen:**

```python
@st.cache_data         # Für Daten (JSON, DataFrames)
@st.cache_resource     # Für Ressourcen (DB-Connections)
```

## Unser Dashboard

### Datei-Struktur

```
src/dashboard/
├── Dockerfile
├── dashboard.py         # Hauptdatei
├── requirements.txt
└── utils/
    └── api_client.py    # API-Wrapper
```

### dashboard.py - Hauptdatei

```python
import streamlit as st
import requests
import pandas as pd
from typing import List, Dict

# Seitenkonfiguration
st.set_page_config(
    page_title="Arbitrage Tracker",
    page_icon="💰",
    layout="wide"
)

# API-Basis-URL
API_BASE_URL = "http://api:8000"

# Caching für API-Calls
@st.cache_data(ttl=60)
def fetch_opportunities(min_margin: float, limit: int) -> List[Dict]:
    """Arbitrage-Opportunities von API laden"""
    response = requests.get(
        f"{API_BASE_URL}/opportunities",
        params={
            "min_margin": min_margin,
            "limit": limit
        }
    )
    return response.json()

@st.cache_data(ttl=300)
def fetch_stats() -> Dict:
    """System-Statistiken laden"""
    response = requests.get(f"{API_BASE_URL}/stats")
    return response.json()

# Header
st.title("💰 Amazon Arbitrage Tracker")
st.markdown("**Finde profitable Arbitrage-Möglichkeiten zwischen Amazon-Marktplätzen**")

# Sidebar - Filter
with st.sidebar:
    st.header("⚙️ Filter")

    min_margin = st.slider(
        "Mindest-Marge (%)",
        min_value=0,
        max_value=50,
        value=10,
        step=1
    )

    source_market = st.selectbox(
        "Quellmarkt (Einkauf)",
        options=["Alle", "DE", "UK", "IT", "ES", "FR"]
    )

    target_market = st.selectbox(
        "Zielmarkt (Verkauf)",
        options=["Alle", "DE", "UK", "IT", "ES", "FR"]
    )

    limit = st.number_input(
        "Maximale Ergebnisse",
        min_value=10,
        max_value=500,
        value=100,
        step=10
    )

    refresh_button = st.button("🔄 Daten aktualisieren")

# Statistiken
stats = fetch_stats()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📦 Gesamt-Produkte",
        value=stats.get("total_products", 0)
    )

with col2:
    st.metric(
        label="💰 Opportunities",
        value=stats.get("total_opportunities", 0)
    )

with col3:
    st.metric(
        label="🌍 Märkte",
        value=len(stats.get("markets", []))
    )

st.divider()

# Opportunities laden
with st.spinner("Lade Arbitrage-Möglichkeiten..."):
    opportunities = fetch_opportunities(min_margin, limit)

# Anzeige
st.subheader(f"🎯 {len(opportunities)} Arbitrage-Möglichkeiten gefunden")

if not opportunities:
    st.warning("Keine Opportunities gefunden. Versuche die Filter anzupassen.")
else:
    # Als DataFrame
    df = pd.DataFrame(opportunities)

    # Spalten umbenennen
    df = df.rename(columns={
        "asin": "ASIN",
        "title": "Produkt",
        "source_market": "Kaufmarkt",
        "target_market": "Verkaufsmarkt",
        "source_price": "Kaufpreis (Cent)",
        "target_price": "Verkaufspreis (Cent)",
        "margin": "Gewinn (Cent)",
        "margin_percentage": "Marge %"
    })

    # Preise in Euro umrechnen
    if "Kaufpreis (Cent)" in df.columns:
        df["Kaufpreis (€)"] = df["Kaufpreis (Cent)"] / 100
        df["Verkaufspreis (€)"] = df["Verkaufspreis (Cent)"] / 100
        df["Gewinn (€)"] = df["Gewinn (Cent)"] / 100

    # Sortieren nach Marge
    df = df.sort_values("Marge %", ascending=False)

    # Interaktive Tabelle
    st.dataframe(
        df[[
            "ASIN",
            "Produkt",
            "Kaufmarkt",
            "Verkaufsmarkt",
            "Kaufpreis (€)",
            "Verkaufspreis (€)",
            "Gewinn (€)",
            "Marge %"
        ]],
        use_container_width=True,
        height=600
    )

    # Details zu ausgewähltem Produkt
    st.subheader("📊 Produkt-Details")

    selected_asin = st.selectbox(
        "Produkt auswählen",
        options=df["ASIN"].tolist(),
        format_func=lambda x: df[df["ASIN"] == x]["Produkt"].iloc[0]
    )

    if selected_asin:
        product = df[df["ASIN"] == selected_asin].iloc[0]

        col1, col2 = st.columns([1, 2])

        with col1:
            if "image_url" in product and product["image_url"]:
                st.image(product["image_url"], width=200)

        with col2:
            st.markdown(f"**Titel:** {product['Produkt']}")
            st.markdown(f"**ASIN:** {product['ASIN']}")
            st.markdown(f"**Kaufmarkt:** {product['Kaufmarkt']}")
            st.markdown(f"**Verkaufsmarkt:** {product['Verkaufsmarkt']}")
            st.markdown(f"**Gewinn:** {product['Gewinn (€)']}€ ({product['Marge %']:.1f}%)")

            # Amazon-Links
            buy_url = f"https://www.amazon.{product['Kaufmarkt'].lower()}/dp/{product['ASIN']}"
            sell_url = f"https://www.amazon.{product['Verkaufsmarkt'].lower()}/dp/{product['ASIN']}"

            st.markdown(f"[🛒 Kaufen auf Amazon {product['Kaufmarkt']}]({buy_url})")
            st.markdown(f"[💰 Verkaufen auf Amazon {product['Verkaufsmarkt']}]({sell_url})")

# Footer
st.divider()
st.caption("Daten-Update: Alle 60 Sekunden | Quelle: Keepa API")
```

## Interaktivität

### Rerun bei Änderung

Streamlit führt das **komplette Skript neu aus** wenn:
- Ein Widget geändert wird
- Ein Button geklickt wird
- `st.rerun()` aufgerufen wird

```python
import streamlit as st

counter = 0

if st.button("Zähler erhöhen"):
    counter += 1  # FALSCH! Wird bei jedem Rerun zurückgesetzt

st.write(f"Counter: {counter}")  # Immer 0
```

**Lösung: Session State**

```python
import streamlit as st

# Initialisierung
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Zähler erhöhen"):
    st.session_state.counter += 1  # Bleibt erhalten

st.write(f"Counter: {st.session_state.counter}")
```

## Charts & Visualisierung

### Pandas DataFrames

```python
import pandas as pd
import streamlit as st

df = pd.DataFrame({
    "Markt": ["DE", "UK", "IT", "ES", "FR"],
    "Opportunities": [45, 23, 67, 34, 12]
})

# Bar Chart
st.bar_chart(df.set_index("Markt"))
```

### Plotly (Interaktiv)

```python
import plotly.express as px

fig = px.bar(
    df,
    x="Markt",
    y="Opportunities",
    title="Opportunities pro Markt",
    color="Opportunities"
)

st.plotly_chart(fig, use_container_width=True)
```

### Altair

```python
import altair as alt

chart = alt.Chart(df).mark_bar().encode(
    x="Markt",
    y="Opportunities",
    color="Markt"
)

st.altair_chart(chart, use_container_width=True)
```

## Formular-Handling

```python
import streamlit as st

with st.form("product_form"):
    st.write("Produkt hinzufügen")

    asin = st.text_input("ASIN")
    title = st.text_input("Titel")
    price = st.number_input("Preis (€)", min_value=0.0)

    submitted = st.form_submit_button("Speichern")

    if submitted:
        st.success(f"Produkt {asin} gespeichert!")
```

**Vorteil:** Form wird nur bei Submit neu gerendert

## File Upload

```python
import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("CSV hochladen", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
```

## Multi-Page Apps

### Datei-Struktur

```
dashboard/
├── Home.py              # Hauptseite
└── pages/
    ├── 1_Opportunities.py
    ├── 2_Statistics.py
    └── 3_Settings.py
```

Streamlit erkennt automatisch `pages/`-Ordner und erstellt Navigation.

### Beispiel

**Home.py:**
```python
import streamlit as st

st.title("Willkommen")
st.write("Wähle eine Seite in der Sidebar")
```

**pages/1_Opportunities.py:**
```python
import streamlit as st

st.title("Opportunities")
# Opportunities-Code hier
```

## Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
dashboard:
  build:
    context: .
    dockerfile: src/dashboard/Dockerfile
  environment:
    - API_BASE_URL=http://api:8000
    - STREAMLIT_SERVER_PORT=8501
    - STREAMLIT_SERVER_HEADLESS=true
  ports:
    - "8501:8501"
  depends_on:
    - api
```

### Streamlit Cloud (kostenlos)

1. Code auf GitHub pushen
2. https://streamlit.io/cloud
3. Repository verbinden
4. Automatisches Deployment

## Best Practices

### 1. **State Management**

```python
# Initialisierung
if "data" not in st.session_state:
    st.session_state.data = None

# Speichern
st.session_state.data = fetch_data()

# Lesen
data = st.session_state.data
```

### 2. **Caching**

```python
# Daten-Caching (mit TTL)
@st.cache_data(ttl=60)
def load_data():
    return api.fetch()

# Ressourcen-Caching (ohne TTL)
@st.cache_resource
def get_database_connection():
    return connect_to_db()
```

### 3. **Error Handling**

```python
try:
    data = fetch_api_data()
    st.dataframe(data)
except requests.exceptions.RequestException as e:
    st.error(f"API-Fehler: {e}")
except Exception as e:
    st.error(f"Unerwarteter Fehler: {e}")
```

### 4. **Loading States**

```python
with st.spinner("Lade Daten..."):
    data = slow_function()

st.success("Daten geladen!")
```

### 5. **Progress Bars**

```python
import time

progress_bar = st.progress(0)

for i in range(100):
    time.sleep(0.1)
    progress_bar.progress(i + 1)

st.success("Fertig!")
```

## Styling

### Custom CSS

```python
st.markdown("""
<style>
.big-font {
    font-size: 30px !important;
    color: blue;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Großer blauer Text</p>', unsafe_allow_html=True)
```

### Theme (config.toml)

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

## Zusammenfassung

| **Feature** | **Beschreibung** | **Unser Einsatz** |
|-------------|------------------|-------------------|
| **Framework** | Streamlit | Web-Dashboard |
| **Port** | 8501 | HTTP Server |
| **Widgets** | Slider, Selectbox, Button | Filter-UI |
| **Display** | DataFrame, Charts, Metrics | Daten-Visualisierung |
| **Caching** | @st.cache_data | API-Performance |
| **Layout** | Columns, Sidebar, Tabs | Seitenstruktur |

**Streamlit macht unser System:**
- 🎨 Benutzerfreundlich (Interaktives UI)
- ⚡ Schnell entwickelt (Nur Python)
- 📊 Visuell (Charts & Tabellen)
- 🔄 Reaktiv (Auto-Rerun)
