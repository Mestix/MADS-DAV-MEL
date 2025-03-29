# src/les3.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from loguru import logger

# Visualisatie 1: Aantal berichten per week (globaal overzicht)
def generate_weekly_overview_chart(df: pd.DataFrame, output_path: Path):
    # Zorg dat timestamp een datetime is
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Zet de week-startdatum in een aparte kolom
    df['week'] = df['timestamp'].dt.to_period('W').apply(lambda r: r.start_time.date())

    # Filter vanaf 1 september 2023
    start_date = pd.to_datetime('2023-09-01').date()
    df_filtered = df[df['week'] >= start_date]

    # Tel het aantal berichten per week
    weekly_counts = df_filtered.groupby('week').size().reset_index(name='message_count')

    # Carnavalperiodes definiëren
    carnavals = [
        (pd.to_datetime('2024-02-08').date(), pd.to_datetime('2024-02-15').date(), 'Carnaval 2024'),
        (pd.to_datetime('2025-02-27').date(), pd.to_datetime('2025-03-04').date(), 'Carnaval 2025')
    ]

    # Plot aanmaken
    plt.figure(figsize=(14, 6))
    plt.plot(weekly_counts['week'], weekly_counts['message_count'], label='Aantal berichten per week', color='tab:blue')

    # Carnaval visueel markeren
    for start, end, label in carnavals:
        plt.axvspan(start, end, color='orange', alpha=0.3, label=label)

    # Dubbele labels uit de legenda filteren
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.xlabel('Week')
    plt.ylabel('Aantal berichten')
    plt.title('Activiteit in de familiechat per week rondom carnaval 2024 & 2025')
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    logger.info(f"Afbeelding opgeslagen als: {output_path}")

# Visualisatie 2: Zoom in op de 2 weken vóór carnaval
def generate_carnaval_detail_chart(df: pd.DataFrame, output_path: Path):
    # Carnaval startdata per jaar
    carnaval_data = pd.DataFrame({
        "year": [2024, 2025],
        "start_date": [pd.Timestamp("2024-02-08"), pd.Timestamp("2025-02-27")]
    })

    # Bepaal bij welke carnavalsperiode een bericht hoort
    def get_carnaval_year(ts):
        for _, row in carnaval_data.iterrows():
            start = row["start_date"]
            if start - pd.Timedelta(days=14) <= ts <= start + pd.Timedelta(days=5):
                return row["year"]
        return None

    # Berekeningen starten
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['carnaval_year'] = df['timestamp'].apply(get_carnaval_year)
    df_carnaval = df[df["carnaval_year"].notna()].copy()

    # Voeg startdatum carnaval toe
    df_carnaval = df_carnaval.merge(carnaval_data, left_on="carnaval_year", right_on="year", how="left")

    # Bereken hoeveel dagen tot carnaval
    df_carnaval["days_until_carnaval"] = (
        df_carnaval["timestamp"].dt.floor("D") - df_carnaval["start_date"]
    ).dt.days

    # Tel aantal berichten per dag tot carnaval
    agg = df_carnaval.groupby(["carnaval_year", "days_until_carnaval"]).size().reset_index(name="message_count")

    # Plot maken
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=agg, x="days_until_carnaval", y="message_count", hue="carnaval_year", marker="o")
    plt.axvline(0, color="gray", linestyle="--", label="Start carnaval")
    plt.title("Activiteit in de 2 weken vóór carnaval")
    plt.xlabel("Dagen tot carnaval")
    plt.ylabel("Aantal berichten")
    plt.legend(title="Jaar")
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    logger.info(f"Afbeelding opgeslagen als: {output_path}")

# Wrapper-functie die beide grafieken aanmaakt vanuit main.py
def generate_time_charts(df: pd.DataFrame, output_dir: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    # Eén functie die beide visualisaties uitvoert
    generate_weekly_overview_chart(df, output_dir / "les3_weekactiviteit.png")
    generate_carnaval_detail_chart(df, output_dir / "les3_2weken_detail.png")
