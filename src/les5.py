from pathlib import Path

import pandas as pd
from loguru import logger

from plot_settings import set_plot_style
from plot_utils import plot_boxplot, plot_heatmap


def generate_relations_chart(df: pd.DataFrame, output_path: Path, settings: dict):
    set_plot_style()

    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen boxplot genereren.")
        return

    columns = settings["columns"]
    cfg = settings.get("relation_chart", {})

    person_df = (
        df.groupby(columns["author"])
        .agg({columns["is_carnaval"]: "mean", columns["is_inlaw"]: "first"})
        .reset_index()
    )
    # Drop lege in-law records
    person_df = person_df[person_df[columns["is_inlaw"]].notna()]

    # Maak labels voor de boxplot
    person_df["inlaw_label"] = person_df[columns["is_inlaw"]].map({0: "Nee", 1: "Ja"})

    # Drop NaN’s in relevante kolommen
    person_df = person_df.dropna(subset=["inlaw_label", columns["is_carnaval"]])

    # plot
    plot_boxplot(
        data=person_df,
        x_col="inlaw_label",
        y_col=columns["is_carnaval"],
        xlabel=cfg.get("xlabel", ""),
        ylabel=cfg.get("ylabel", ""),
        title=cfg.get("title", ""),
        palette=cfg.get("palette", None),
        output_path=output_path,
    )

    logger.success(f"Boxplot opgeslagen als: {output_path}")


def generate_correlation_diagram(df: pd.DataFrame, output_path: Path, settings: dict):
    set_plot_style()

    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen heatmap genereren.")
        return

    columns = settings["columns"]
    title = settings.get("correlation_chart", {}).get("title", "")

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

    person_df = person_df.dropna()
    person_df["gender_num"] = (
        person_df[columns["gender"]].str.lower().map({"m": 0, "f": 1})
    )

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

    plot_heatmap(corr_matrix=corr, title=title, output_path=output_path)

    logger.success(f"Heatmap opgeslagen als: {output_path}")


def generate_relation_charts(df: pd.DataFrame, output_dir: Path, les5_settings: dict):
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    output = les5_settings["output_files"]

    generate_correlation_diagram(df, output_dir / output["correlation"], les5_settings)
    generate_relations_chart(
        df, output_dir / output["carnaval_relation"], les5_settings
    )
