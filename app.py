import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from data_loader import fetch_weather_data
from data_processing import clean_and_merge_data, merge_with_locations, calculate_heat_index
from visualization import plot_temperature, plot_humidity

# Funkcja do interpretacji pogody
def interpretuj_pogode(wiersz):
    opad = float(wiersz.get('suma_opadu', 0))
    temp = float(wiersz['temperatura'])
    wilg = float(wiersz['wilgotnosc_wzgledna'])

    if opad > 0 and temp < 0:
        return "❄️ Śnieg"
    elif opad > 2.5:
        return "🌧️ Deszcz"
    elif wilg > 85:
        return "☁️ Pochmurno"
    elif wilg < 60:
        return "☀️ Słonecznie"
    else:
        return "🌤️ Częściowe zachmurzenie"

# Funkcja do tłumaczenia kierunku wiatru
def kierunek_wiatru(stopnie):
    kierunki = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    indeks = round(stopnie / 45) % 8
    return kierunki[indeks]

# Konfiguracja strony
st.set_page_config(page_title="Pogoda w Polsce", layout="wide")
st.title("Prognoza pogody w polskich miastach")

# Pobieranie i przetwarzanie danych
df_surowe = fetch_weather_data()
df_czyste = clean_and_merge_data(df_surowe)
df_czyste = merge_with_locations(df_czyste)
df_czyste = calculate_heat_index(df_czyste)

# Średnia temperatura
srednia_temp = df_czyste['temperatura'].mean()

# Wybór stacji
stacja_wybrana = st.sidebar.selectbox("Wybierz stację do analizy", df_czyste['stacja'].unique())
df_stacja = df_czyste[df_czyste['stacja'] == stacja_wybrana]
aktualny_wiersz = df_stacja.iloc[0]

# Historia pogodowa z pliku
try:
    df_historia = pd.read_csv("weather_log.csv")
    df_historia["data_pobrania"] = pd.to_datetime(df_historia["data_pobrania"])
    dzisiaj = datetime.now()
    siedem_dni_temu = dzisiaj - timedelta(days=7)
    df_historia_stacja = df_historia[
        (df_historia["stacja"] == stacja_wybrana) & 
        (df_historia["data_pobrania"] >= siedem_dni_temu)
    ]
except:
    df_historia_stacja = pd.DataFrame()

# Wyświetlanie danych
st.subheader(f"Analiza stacji: {stacja_wybrana}")

opis_pogody = interpretuj_pogode(aktualny_wiersz)
st.markdown(f"### Aktualna prognoza: **{opis_pogody}**")

# Rząd 1: podstawowe parametry
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📈 Temperatura", f"{aktualny_wiersz['temperatura']} °C")
with col2:
    st.metric("🌡️ Odczuwalna temperatura", f"{aktualny_wiersz['heat_index']} °C")
with col3:
    st.metric("💧 Wilgotność", f"{aktualny_wiersz['wilgotnosc_wzgledna']}%")
with col4:
    st.metric("🌧️ Opady", f"{aktualny_wiersz['suma_opadu']} mm")

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# Rząd 2: dodatkowe informacje
kierunek = kierunek_wiatru(float(aktualny_wiersz.get("kierunek_wiatru", 0)))
predkosc_wiatru = aktualny_wiersz.get("predkosc_wiatru", "brak danych")
cisnienie = aktualny_wiersz.get("cisnienie", "brak danych")
odchylenie_temp = round(aktualny_wiersz['temperatura'] - srednia_temp, 2)

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("🔀 Odchylenie od średniej", f"{odchylenie_temp} °C")
with col6:
    st.metric("💨 Wiatr", f"{predkosc_wiatru} m/s, {kierunek}")
with col7:
    st.metric("📉 Ciśnienie", f"{cisnienie} hPa")
with col8:
    st.write("")  # pusta kolumna

# Historia pogodowa
if not df_historia_stacja.empty:
    st.markdown(f"### Ostatnie 7 dni – {stacja_wybrana}:")
    col_temp, col_wilg, col_cisn = st.columns(3)

    fig_temp = px.line(df_historia_stacja, x="data_pobrania", y="temperatura", markers=True, title="Temperatura (°C)")
    fig_temp.update_layout(xaxis_title="Data", yaxis_title="Temperatura")
    col_temp.plotly_chart(fig_temp, use_container_width=True)

    fig_wilg = px.line(df_historia_stacja, x="data_pobrania", y="wilgotnosc_wzgledna", markers=True, title="Wilgotność (%)")
    fig_wilg.update_layout(xaxis_title="Data", yaxis_title="Wilgotność")
    col_wilg.plotly_chart(fig_wilg, use_container_width=True)

    fig_cisn = px.line(df_historia_stacja, x="data_pobrania", y="cisnienie", markers=True, title="Ciśnienie (hPa)")
    fig_cisn.update_layout(xaxis_title="Data", yaxis_title="Ciśnienie")
    col_cisn.plotly_chart(fig_cisn, use_container_width=True)
else:
    st.info("Brak danych historycznych do wyświetlenia.")

# Anomalie pogodowe
st.subheader("Wyjątkowo ciepłe i zimne obszary")

srednia = df_czyste['temperatura'].mean()
odchylenie = df_czyste['temperatura'].std()

df_gorace = df_czyste[df_czyste['temperatura'] > srednia + 5]
df_zimne = df_czyste[df_czyste['temperatura'] < srednia - 5]

st.markdown(f"Średnia krajowa temperatura: **{round(srednia, 2)} °C**")
st.markdown(f"Odchylenie standardowe: **{round(odchylenie, 2)}**")

st.markdown("#### 🌞 Stacje z temperaturą > średnia + 5°C")
st.dataframe(df_gorace[['stacja', 'temperatura']])

st.markdown("#### ❄️ Stacje z temperaturą < średnia - 5°C")
st.dataframe(df_zimne[['stacja', 'temperatura']])

# Mapa pogodowa
st.sidebar.header("Ustawienia mapy")
pokaz_mape = st.sidebar.checkbox("Pokaż mapę pogodową", value=True)
zmienna_mapy = st.sidebar.selectbox("Wybierz zmienną do mapy", ["temperatura", "wilgotnosc_wzgledna", "cisnienie", "heat_index"])

if pokaz_mape:
    st.subheader(f"Mapa – {zmienna_mapy.capitalize()}")
    df_mapa = df_czyste.dropna(subset=["latitude", "longitude", zmienna_mapy])

    fig_mapa = px.scatter_mapbox(
        df_mapa,
        lat="latitude",
        lon="longitude",
        color=zmienna_mapy,
        size=zmienna_mapy,
        hover_name="stacja",
        color_continuous_scale="RdYlBu_r",
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 52, "lon": 19},
        title=f"{zmienna_mapy.capitalize()} w Polsce",
        height=700
    )
    st.plotly_chart(fig_mapa)

# Ekstrema pogodowe
st.markdown("### Ekstremalne wartości pogodowe")

col1, col2, col3, col4, col5, col6 = st.columns(6)

max_temp = df_czyste.loc[df_czyste['temperatura'].idxmax()]
col1.metric("Najcieplejsze miasto", max_temp['stacja'], f"{max_temp['temperatura']}°C")

min_temp = df_czyste.loc[df_czyste['temperatura'].idxmin()]
col2.metric("Najzimniejsze miasto", min_temp['stacja'], f"{min_temp['temperatura']}°C")

max_wilg = df_czyste.loc[df_czyste['wilgotnosc_wzgledna'].idxmax()]
col3.metric("Największa wilgotność", max_wilg['stacja'], f"{max_wilg['wilgotnosc_wzgledna']}%")

min_wilg = df_czyste.loc[df_czyste['wilgotnosc_wzgledna'].idxmin()]
col4.metric("Najmniejsza wilgotność", min_wilg['stacja'], f"{min_wilg['wilgotnosc_wzgledna']}%")

if 'predkosc_wiatru' in df_czyste.columns:
    max_wiatr = df_czyste.loc[df_czyste['predkosc_wiatru'].idxmax()]
    col5.metric("Najsilniejszy wiatr", max_wiatr['stacja'], f"{max_wiatr['predkosc_wiatru']} m/s")

    min_wiatr = df_czyste.loc[df_czyste['predkosc_wiatru'].idxmin()]
    col6.metric("Najsłabszy wiatr", min_wiatr['stacja'], f"{min_wiatr['predkosc_wiatru']} m/s")
else:
    col5.warning("Brak danych o wietrze")
    col6.empty()

# Porównanie dwóch miast
st.sidebar.header("Porównanie dwóch miast")
miasta = df_czyste['stacja'].unique()
miasto1 = st.sidebar.selectbox("Wybierz pierwsze miasto", miasta)
miasto2 = st.sidebar.selectbox("Wybierz drugie miasto", miasta, index=1)

df_porownanie = df_czyste[df_czyste['stacja'].isin([miasto1, miasto2])]

# Porównanie parametrów
st.subheader("Porównanie parametrów")

wymagane_kolumny = ['stacja', 'temperatura', 'wilgotnosc_wzgledna', 'predkosc_wiatru', 'heat_index', 'suma_opadu']
brakujace = [k for k in wymagane_kolumny if k not in df_porownanie.columns]
if brakujace:
    st.warning(f"Brakuje kolumn: {', '.join(brakujace)}.")
else:
    df_slupki = df_porownanie[wymagane_kolumny].melt(id_vars='stacja', var_name='Parametr', value_name='Wartość')

    etykiety_parametrow = {
        "temperatura": "Temperatura (°C)",
        "wilgotnosc_wzgledna": "Wilgotność (%)",
        "predkosc_wiatru": "Wiatr (m/s)",
        "heat_index": "Temp. odczuwalna (°C)",
        "suma_opadu": "Opady (mm)"
    }
    df_slupki["Parametr"] = df_slupki["Parametr"].map(etykiety_parametrow)

    fig_porownanie = px.bar(
        df_slupki,
        y='Parametr',
        x='Wartość',
        color='stacja',
        barmode='group',
        orientation='h',
        title='Grupowane porównanie parametrów'
    )
    fig_porownanie.update_layout(xaxis_title="Wartość", yaxis_title="Parametr", legend_title="Stacja")

    st.plotly_chart(fig_porownanie, use_container_width=True)

# Ciśnienie w wybranych miastach
st.markdown("#### Ciśnienie atmosferyczne")

col1, col2 = st.columns(2)
cisnienie1 = df_porownanie[df_porownanie['stacja'] == miasto1]['cisnienie'].values[0]
col1.metric(label=f"{miasto1}", value=f"{cisnienie1} hPa")

cisnienie2 = df_porownanie[df_porownanie['stacja'] == miasto2]['cisnienie'].values[0]
col2.metric(label=f"{miasto2}", value=f"{cisnienie2} hPa")

# Ranking stacji
st.subheader("Ranking stacji")
if st.button("Pokaż ranking wszystkich stacji"):
    st.markdown("### Temperatury (°C)")
    df_sort_temp = df_czyste.sort_values(by="temperatura", ascending=False)
    fig_temp = px.bar(df_sort_temp, x="temperatura", y="stacja", orientation="h")
    st.plotly_chart(fig_temp)

    st.markdown("### Wilgotność (%)")
    df_sort_wilg = df_czyste.sort_values(by="wilgotnosc_wzgledna", ascending=False)
    fig_wilg = px.bar(df_sort_wilg, x="wilgotnosc_wzgledna", y="stacja", orientation="h")
    st.plotly_chart(fig_wilg)

    st.markdown("### Temperatura odczuwalna (°C)")
    df_sort_heat = df_czyste.sort_values(by="heat_index", ascending=False)
    fig_heat = px.bar(df_sort_heat, x="heat_index", y="stacja", orientation="h")
    st.plotly_chart(fig_heat)

    st.markdown("### Ciśnienie (hPa)")
    df_sort_cisnienie = df_czyste.sort_values(by="cisnienie", ascending=False)
    fig_cisnienie = px.bar(df_sort_cisnienie, x="cisnienie", y="stacja", orientation="h")
    st.plotly_chart(fig_cisnienie)

st.subheader("Dodatkowe wizualizacje pogodowe")

# LM
# 1
st.markdown("Średnia temperatura odczuwalna w stacjach")
df_mean_heat = df_czyste.groupby("stacja")["heat_index"].mean().reset_index()
fig_bar_heat = px.bar(df_mean_heat, x="stacja", y="heat_index",
                      title="Średnia temperatura odczuwalna (°C)")
fig_bar_heat.update_layout(xaxis_title="Stacja", yaxis_title="Temperatura odczuwalna (°C)", xaxis_tickangle=45)
st.plotly_chart(fig_bar_heat, use_container_width=True)

# 2
st.markdown("Korelacja między parametrami pogodowymi")
parametry = ["temperatura", "wilgotnosc_wzgledna", "cisnienie", "heat_index"]
if 'predkosc_wiatru' in df_czyste.columns:
    parametry.append("predkosc_wiatru")
if 'suma_opadu' in df_czyste.columns:
    parametry.append("suma_opadu")
corr_matrix = df_czyste[parametry].corr()
fig_heatmap = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r",
                        title="Mapa korelacji parametrów pogodowych")
st.plotly_chart(fig_heatmap, use_container_width=True)

# 3
st.markdown("Odchylenie temperatury od średniej krajowej")
df_czyste["odchylenie_temp"] = df_czyste["temperatura"] - df_czyste["temperatura"].mean()
fig_line_odchylenie = px.line(df_czyste, x="stacja", y="odchylenie_temp", markers=True,
                              title="Odchylenie temperatury od średniej (°C)")
fig_line_odchylenie.update_layout(xaxis_title="Stacja", yaxis_title="Odchylenie (°C)", xaxis_tickangle=45)
st.plotly_chart(fig_line_odchylenie, use_container_width=True)

# 4
if 'predkosc_wiatru' in df_czyste.columns:
    st.markdown("Maksymalna prędkość wiatru w stacjach")
    df_max_wiatr = df_czyste.groupby("stacja")["predkosc_wiatru"].max().reset_index()
    fig_bar_wiatr = px.bar(df_max_wiatr, x="stacja", y="predkosc_wiatru",
                           title="Maksymalna prędkość wiatru (m/s)")
    fig_bar_wiatr.update_layout(xaxis_title="Stacja", yaxis_title="Prędkość wiatru (m/s)", xaxis_tickangle=45)
    st.plotly_chart(fig_bar_wiatr, use_container_width=True)

# 5
st.markdown("#### 1. Temperatura odczuwalna vs Ciśnienie")
fig_scatter_heat_press = px.scatter(df_czyste, x="heat_index", y="cisnienie", color="stacja",
                                    title="Zależność temperatury odczuwalnej i ciśnienia", hover_data=["stacja"])
fig_scatter_heat_press.update_layout(xaxis_title="Temperatura odczuwalna (°C)", yaxis_title="Ciśnienie (hPa)")
st.plotly_chart(fig_scatter_heat_press, use_container_width=True)


# 6
st.markdown("Rozkład wilgotności w stacjach")
fig_box_wilg = px.box(df_czyste, x="stacja", y="wilgotnosc_wzgledna", title="Rozkład wilgotności (%) w stacjach")
fig_box_wilg.update_layout(xaxis_title="Stacja", yaxis_title="Wilgotność (%)", xaxis_tickangle=45)
st.plotly_chart(fig_box_wilg, use_container_width=True)

# 7
if 'suma_opadu' in df_czyste.columns:
    st.markdown("Suma opadów w stacjach")
    df_sum_opady = df_czyste.groupby("stacja")["suma_opadu"].sum().reset_index()
    fig_bar_opady = px.bar(df_sum_opady, x="stacja", y="suma_opadu", title="Suma opadów (mm) w stacjach")
    fig_bar_opady.update_layout(xaxis_title="Stacja", yaxis_title="Suma opadów (mm)", xaxis_tickangle=45)
    st.plotly_chart(fig_bar_opady, use_container_width=True)

# 8
if not df_historia_stacja.empty:
    st.markdown("Ciśnienie w ostatnich 7 dniach")
    fig_line_cisnienie_hist = px.line(df_historia_stacja, x="data_pobrania", y="cisnienie", markers=True,
                                      title=f"Ciśnienie atmosferyczne – {stacja_wybrana}")
    fig_line_cisnienie_hist.update_layout(xaxis_title="Data", yaxis_title="Ciśnienie (hPa)")
    st.plotly_chart(fig_line_cisnienie_hist, use_container_width=True)

# 9
if not df_historia_stacja.empty and 'suma_opadu' in df_historia_stacja.columns:
    st.markdown("#### 2. Liczba dni z opadami w ostatnich 7 dniach")
    df_historia_stacja["opady_obecne"] = df_historia_stacja["suma_opadu"].apply(lambda x: "Opady" if x > 0 else "Bez opadów")
    opady_counts = df_historia_stacja["opady_obecne"].value_counts().reset_index()
    opady_counts.columns = ["Kategoria", "Liczba dni"]
    fig_bar_opady_hist = px.bar(opady_counts, x="Kategoria", y="Liczba dni",
                                title=f"Liczba dni z opadami – {stacja_wybrana}")
    fig_bar_opady_hist.update_layout(xaxis_title="Kategoria", yaxis_title="Liczba dni")
    st.plotly_chart(fig_bar_opady_hist, use_container_width=True)
    
# 10
st.markdown("#### 1. Różnica między temperaturą a temperaturą odczuwalną")
df_czyste["roznica_heat_temp"] = df_czyste["heat_index"] - df_czyste["temperatura"]
df_roznica = df_czyste.groupby("stacja")["roznica_heat_temp"].mean().reset_index()
fig_bar_roznica = px.bar(df_roznica, x="stacja", y="roznica_heat_temp",
                         title="Średnia różnica między temperaturą odczuwalną a rzeczywistą (°C)")
fig_bar_roznica.update_layout(xaxis_title="Stacja", yaxis_title="Różnica (°C)", xaxis_tickangle=45)
st.plotly_chart(fig_bar_roznica, use_container_width=True)