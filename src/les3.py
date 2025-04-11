from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger


def generate_weekly_overview_chart(df: pd.DataFrame, output_path: Path):
    """
    Genereert een lijnplot van het aantal berichten per week.
    Carnavalperiodes worden automatisch gemarkeerd op basis van 'is_carnaval'.
    """
    df["week"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())

    # Tel berichten per week
    weekly_counts = (
        df.groupby("week")
        .size()
        .reset_index(name="message_count")
    )

    # Carnavalweken uit 'is_carnaval'-kolom
    carnaval_weken = (
        df[df["is_carnaval"]]
        .drop_duplicates("week")
        .sort_values("week")["week"]
        .tolist()
    )

    carnaval_perioden = group_consecutive(carnaval_weken)

    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(
        weekly_counts["week"],
        weekly_counts["message_count"],
        color="tab:blue",
        label="Aantal berichten per week"
    )

    # Carnaval visueel markeren
    for i, (start, end) in enumerate(carnaval_perioden):
        plt.axvspan(start, end, color="orange", alpha=0.3, label=f"Carnaval {i + 1}")

    # Legenda opschonen
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.xlabel("Week")
    plt.ylabel("Aantal berichten")
    plt.title("Activiteit in de familiechat per week rondom carnaval 2024 & 2025")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Afbeelding opgeslagen als: {output_path}")


def generate_carnaval_detail_chart(df: pd.DataFrame, output_path: Path):
    """
    Zoomt in op de 2 weken vóór en 5 dagen tijdens carnaval,
    toont activiteit per dag (aantal berichten) per jaar.
    """
    df["date"] = df["timestamp"].dt.floor("D")
    df["year"] = df["timestamp"].dt.year

    # Vind de eerste dag van carnaval per jaar op basis van is_carnaval == True
    carnaval_start = (
        df[df["is_carnaval"]]
        .groupby("year")["date"]
        .min()
        .reset_index()
        .rename(columns={"date": "start_date"})
    )

    if carnaval_start.empty:
        logger.warning("Geen carnavalstartdatums gevonden.")
        return

    # Combineer met volledige df (dus niet alleen is_carnaval)
    df = df.merge(carnaval_start, on="year", how="left")
    df["days_until_carnaval"] = (df["date"] - df["start_date"]).dt.days

    # Filter alleen berichten in [-14, +5] rond carnaval
    df_window = df[df["days_until_carnaval"].between(-14, 5)].copy()

    if df_window.empty:
        logger.warning("Geen berichten gevonden binnen het carnavalsvenster.")
        return

    # Aantal berichten per dag t.o.v. carnaval, per jaar
    agg = (
        df_window.groupby(["year", "days_until_carnaval"])
        .size()
        .reset_index(name="message_count")
    )

    # Plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=agg,
        x="days_until_carnaval",
        y="message_count",
        hue="year",
        marker="o",
    )
    plt.axvline(0, color="gray", linestyle="--", label="Start carnaval")
    plt.title("Activiteit in de 2 weken vóór carnaval")
    plt.xlabel("Dagen tot carnaval")
    plt.ylabel("Aantal berichten")
    plt.legend(title="Jaar")
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Afbeelding opgeslagen als: {output_path}")


def generate_time_charts(df: pd.DataFrame, output_dir: Path, les3_settings: dict):
    """
    Wrapperfunctie die beide les 3 visualisaties uitvoert.
    Bestandsnamen komen uit settings.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    output_week = output_dir / les3_settings["output_files"]["weekly"]
    output_detail = output_dir / les3_settings["output_files"]["detail"]

    generate_weekly_overview_chart(df, output_week)
    generate_carnaval_detail_chart(df, output_detail)


def group_consecutive(dates):
    """
    Groepeert opeenvolgende weken tot (start, end) tuples.
    Werkt met gesorteerde week-startdatums als '2024-02-05', '2024-02-12', ...
    """
    if not dates:
        return []

    ranges = []
    start = prev = dates[0]

    for current in dates[1:]:
        # Als verschil > 7 dagen, dan begint er een nieuwe reeks
        if (current - prev).days > 7:
            ranges.append((start, prev))
            start = current
        prev = current

    # Voeg laatste groep toe
    ranges.append((start, prev))
    return ranges
