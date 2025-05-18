from data_loader import fetch_weather_data, save_to_csv
from data_processing import clean_and_merge_data
from visualization import plot_temperature, plot_humidity

def main():
    df_raw = fetch_weather_data()
    save_to_csv(df_raw)
    df_clean = clean_and_merge_data(df_raw)
    plot_temperature(df_clean)
    plot_humidity(df_clean)

if __name__ == "__main__":
    main()
