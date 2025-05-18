import pandas as pd

def clean_and_merge_data(df):
    # Wybór istotnych kolumn
    df = df[['stacja', 'temperatura', 'wilgotnosc_wzgledna', 'cisnienie',
             'predkosc_wiatru', 'kierunek_wiatru', 'suma_opadu']]
    
    # Konwersja typów danych
    df['temperatura'] = pd.to_numeric(df['temperatura'], errors='coerce')
    df['wilgotnosc_wzgledna'] = pd.to_numeric(df['wilgotnosc_wzgledna'], errors='coerce')
    df['cisnienie'] = pd.to_numeric(df['cisnienie'], errors='coerce')
    df['predkosc_wiatru'] = pd.to_numeric(df['predkosc_wiatru'], errors='coerce')
    df['kierunek_wiatru'] = pd.to_numeric(df['kierunek_wiatru'], errors='coerce')
    df['suma_opadu'] = pd.to_numeric(df['suma_opadu'], errors='coerce')

    # Usunięcie braków danych
    df.dropna(inplace=True)
    
    # Grupowanie – średnia dla każdej stacji
    df_grouped = df.groupby('stacja').mean(numeric_only=True).reset_index()
    
    return df_grouped



def merge_with_locations(df_weather, location_file="stations_coordinates.csv"):
    df_locations = pd.read_csv(location_file)
    return df_weather.merge(df_locations, on="stacja", how="left")

def calculate_heat_index(df):
    T = df['temperatura']
    RH = df['wilgotnosc_wzgledna']
    V = pd.to_numeric(df.get('predkosc_wiatru', 0), errors='coerce') * 3.6  # m/s → km/h

    # Heat Index dla T > 20°C
    T_F = (T * 9/5) + 32
    HI_F = (
        -42.379 + 2.04901523 * T_F + 10.14333127 * RH
        - 0.22475541 * T_F * RH - 6.83783e-3 * T_F**2
        - 5.481717e-2 * RH**2 + 1.22874e-3 * T_F**2 * RH
        + 8.5282e-4 * T_F * RH**2 - 1.99e-6 * T_F**2 * RH**2
    )
    HI_C = (HI_F - 32) * 5/9

    # Wind Chill dla T <= 10°C i V >= 4.8 km/h (czyli ~1.3 m/s)
    wind_chill = 13.12 + 0.6215 * T - 11.37 * V**0.16 + 0.3965 * T * V**0.16

    df['heat_index'] = T  # domyślnie

    df.loc[T > 20, 'heat_index'] = HI_C
    df.loc[(T <= 10) & (V >= 4.8), 'heat_index'] = wind_chill

    df['heat_index'] = df['heat_index'].round(1)
    return df








