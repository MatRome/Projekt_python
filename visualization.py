import matplotlib.pyplot as plt
import seaborn as sns

def plot_temperature(df):
    df_sorted = df.sort_values(by='temperatura', ascending=False)

    plt.figure(figsize=(10, 12))
    sns.barplot(x='temperatura', y='stacja', data=df_sorted)
    plt.title('Średnia temperatura w miastach')
    plt.tight_layout()
    plt.savefig('temperature_plot.png')
    plt.close()


def plot_humidity(df):
    df_sorted = df.sort_values(by='wilgotnosc_wzgledna', ascending=False)

    plt.figure(figsize=(10, 12))
    sns.barplot(x='wilgotnosc_wzgledna', y='stacja', data=df_sorted)
    plt.title('Średnia wilgotność względna w miastach')
    plt.tight_layout()
    plt.savefig('humidity_plot.png')
    plt.close()

