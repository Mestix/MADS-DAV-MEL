from pathlib import Path

import pandas as pd
from loguru import logger

from plot_settings import set_plot_style
from plot_utils import plot_boxplot, plot_heatmap

# Functie om een boxplot te genereren van de relatie tussen carnaval en schoonfamilie
def generate_relations_chart(df: pd.DataFrame, output_path: Path, settings: dict):
    set_plot_style()  # Stel standaard plotstijl in

    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen boxplot genereren.")
        return

    columns = settings["columns"]
    cfg = settings.get("relation_chart", {})

    # Groepeer op auteur en bereken gemiddelde carnaval-score en eerste in-law-status
    person_df = (
        df.groupby(columns["author"])
        .agg({columns["is_carnaval"]: "mean", columns["is_inlaw"]: "first"})
        .reset_index()
    )

    # Verwijder rijen zonder in-law-status
    person_df = person_df[person_df[columns["is_inlaw"]].notna()]

    # Maak labels voor in-law-status (bijvoorbeeld 0 -> "Nee", 1 -> "Ja")
    person_df["inlaw_label"] = person_df[columns["is_inlaw"]].map({0: "Nee", 1: "Ja"})

    # Verwijder rijen waar inlaw_label of carnaval-score ontbreekt
    person_df = person_df.dropna(subset=["inlaw_label", columns["is_carnaval"]])

    # Plot de boxplot
    plot_boxplot(
        data=person_df,
        x_col="inlaw_label",
        y_col=columns["is_carnaval"],
        xlabel=cfg.get("xlabel", ""),
        ylabel=cfg.get("ylabel", ""),
        title=cfg.get("title", ""),
        output_path=output_path,
    )

    logger.success(f"Boxplot opgeslagen als: {output_path}")


# Functie om een correlatie-heatmap te genereren van meerdere variabelen
def generate_correlation_diagram(df: pd.DataFrame, output_path: Path, settings: dict):
    set_plot_style()  # Stel standaard plotstijl in

    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen heatmap genereren.")
        return

    columns = settings["columns"]
    title = settings.get("correlation_chart", {}).get("title", "")

    # Groepeer op auteur en bereken gemiddelden of eerste waarden voor de geselecteerde kolommen
    person_df = (
        df.groupby(columns["author"])
        .agg(
            {
                columns["emoji_count"]: "mean",
                columns["message_length"]: "mean",
                columns["age"]: "first",
                columns["gender"]: "first",
                columns["is_inlaw"]: "first",
                columns["is_carnaval"]: "mean",
                columns["timestamp"]: "count",
            }
        )
        .rename(columns={columns["timestamp"]: "message_count"})
        .reset_index()
    )

    # Verwijder alle rijen met ontbrekende waarden
    person_df = person_df.dropna()

    # Zet geslacht om naar numerieke waarden (m -> 0, f -> 1)
    person_df["gender_num"] = (
        person_df[columns["gender"]].str.lower().map({"m": 0, "f": 1})
    )

    # Bereken correlatiematrix van de geselecteerde kolommen
    corr = person_df[
        [
            columns["age"],
            columns["emoji_count"],
            columns["message_length"],
            "message_count",
            columns["is_carnaval"],
            "gender_num",
            columns["is_inlaw"],
        ]
    ].corr()

    # Plot de heatmap
    plot_heatmap(corr_matrix=corr, title=title, output_path=output_path)

    logger.success(f"Heatmap opgeslagen als: {output_path}")


# Hoofdfunctie die zowel de correlatie-heatmap als de boxplot aanmaakt
def generate_relation_charts(df: pd.DataFrame, output_dir: Path, les5_settings: dict):
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    output = les5_settings["output_files"]

    # Genereer correlatie-diagram en sla op
    generate_correlation_diagram(df, output_dir / output["correlation"], les5_settings)

    # Genereer boxplot over carnaval en schoonfamilie en sla op
    generate_relations_chart(
        df, output_dir / output["carnaval_relation"], les5_settings
    )
