import requests
import pandas as pd

def fetch_weather_data():
    url = "https://danepubliczne.imgw.pl/api/data/synop"
    response = requests.get(url)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def save_to_csv(df, filename="weather_data.csv"):
    df.to_csv(filename, index=False)
