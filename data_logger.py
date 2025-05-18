import pandas as pd
import requests
from datetime import datetime
import os

# Adres API
ADRES_API = "https://danepubliczne.imgw.pl/api/data/synop"

# Ścieżka do pliku logu
PLIK_LOGU = os.path.join(os.path.dirname(__file__), "weather_log.csv")

# Funkcja do pobierania danych pogodowych
def pobierz_dane_pogodowe():
    odpowiedz = requests.get(ADRES_API)
    dane = odpowiedz.json()
    df = pd.DataFrame(dane)
    df['data_pobrania'] = datetime.now().strftime('%Y-%m-%d')
    return df[['stacja', 'temperatura', 'wilgotnosc_wzgledna', 'cisnienie', 'data_pobrania']]

# Funkcja do zapisywania dziennych danych pogodowych
def zapisz_dzienne_dane():
    nowe_dane = pobierz_dane_pogodowe()

    if os.path.exists(PLIK_LOGU):
        df_stare = pd.read_csv(PLIK_LOGU)
        df_polaczone = pd.concat([df_stare, nowe_dane], ignore_index=True)
    else:
        df_polaczone = nowe_dane

    df_polaczone.to_csv(PLIK_LOGU, index=False, encoding='utf-8-sig')
    print("Dane zapisane:", datetime.now())

# Uruchamianie zapisu przy bezpośrednim wykonaniu pliku
if __name__ == "__main__":
    zapisz_dzienne_dane()
