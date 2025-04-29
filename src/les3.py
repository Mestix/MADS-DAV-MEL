from pathlib import Path
import pandas as pd

from loguru import logger
from plot_settings import set_plot_style
from plot_utils import plot_line_chart
from plot_utils import plot_line_with_vertical_marker

def generate_weekly_overview_chart(df: pd.DataFrame, output_path: Path, chart_settings: dict):
    """
    Genereert een lijnplot van het aantal berichten per week.
    Carnavalperiodes worden gemarkeerd.
    """
    set_plot_style()

    df["week"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())

    # Tel berichten per week
    weekly_counts = df.groupby("week").size().reset_index(name="message_count")

    # Carnavalweken uit 'is_carnaval'
    carnaval_weken = (
        df[df["is_carnaval"]]
        .drop_duplicates("week")
        .sort_values("week")["week"]
        .tolist()
    )

    carnaval_perioden = group_consecutive(carnaval_weken)

    if weekly_counts.empty:
        logger.warning("Geen wekelijkse data gevonden.")
        return

    # Plot
    plot_line_chart(
        x=weekly_counts["week"],
        y=weekly_counts["message_count"],
        highlight_ranges=carnaval_perioden,
        xlabel=chart_settings["xlabel"],
        ylabel=chart_settings["ylabel"],
        title=chart_settings["title"],
        output_path=output_path,
        highlight_label="Carnaval",
        highlight_color="orange",
    )

def generate_carnaval_detail_chart(df: pd.DataFrame, output_path: Path, chart_settings: dict):
    """
    Zoomt in op berichten rond carnaval ([-14, +5 dagen]).
    """
    set_plot_style()

    df["date"] = df["timestamp"].dt.floor("D")
    df["year"] = df["timestamp"].dt.year

    # Eerste carnavaldag per jaar
    carnaval_start = (
        df[df["is_carnaval"]]
        .groupby("year")["date"]
        .min()
        .reset_index()
        .rename(columns={"date": "start_date"})
    )

    if carnaval_start.empty:
        logger.warning("Geen carnavalstart gevonden.")
        return

    df = df.merge(carnaval_start, on="year", how="left")
    df["days_until_carnaval"] = (df["date"] - df["start_date"]).dt.days

    df_window = df[df["days_until_carnaval"].between(-14, 5)]

    if df_window.empty:
        logger.warning("Geen data binnen carnavalsvenster.")
        return

    agg = (
        df_window.groupby(["year", "days_until_carnaval"])
        .size()
        .reset_index(name="message_count")
    )

    # plot
    plot_line_with_vertical_marker(
        data=agg,
        x="days_until_carnaval",
        y="message_count",
        hue="year",
        xlabel=chart_settings["xlabel"],
        ylabel=chart_settings["ylabel"],
        title=chart_settings["title"],
        output_path=output_path,
        marker_position=0,
        marker_label="Start carnaval",
    )

def generate_time_charts(df: pd.DataFrame, output_dir: Path, les3_settings: dict):
    """
    Wrapper die beide les3 charts maakt.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Geen grafieken gegenereerd.")
        return

    output_week = output_dir / les3_settings["output_files"]["weekly"]
    output_detail = output_dir / les3_settings["output_files"]["detail"]

    generate_weekly_overview_chart(df, output_week, les3_settings["weekly_chart"])
    generate_carnaval_detail_chart(df, output_detail, les3_settings["detail_chart"])

def group_consecutive(dates):
    """
    Groepeert aaneengesloten datums tot (start, end) tuples.
    """
    if not dates:
        return []

    ranges = []
    start = prev = dates[0]

    for current in dates[1:]:
        if (current - prev).days > 7:
            ranges.append((start, prev))
            start = current
        prev = current

    ranges.append((start, prev))
    return ranges
