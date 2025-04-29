from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger


def generate_relations_chart(df: pd.DataFrame, output_path: Path, columns: dict):
    """
    Genereert een boxplot die laat zien of aangetrouwde familieleden
    meer of minder berichten sturen tijdens carnaval dan anderen.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Groepeer data per persoon: gemiddelde carnavalactiviteit en in-law status
    person_df = (
        df.groupby(columns["author"])
        .agg({columns["is_carnaval"]: "mean", columns["is_inlaw"]: "first"})
        .reset_index()
    )

    # Verwijder records zonder in-law informatie
    person_df = person_df[person_df[columns["is_inlaw"]].notna()]

    # Maak mooie labels voor de boxplot
    person_df["is_inlaw_label"] = person_df[columns["is_inlaw"]].map(
        {0: "Nee", 1: "Ja"}
    )

    # Plot de boxplot
    plt.figure(figsize=(6, 5))
    sns.boxplot(
        data=person_df,
        x="is_inlaw_label",
        y=columns["is_carnaval"],
        palette={"Nee": "skyblue", "Ja": "lightcoral"},
    )
    plt.xlabel("Is aangetrouwd?")
    plt.ylabel("Aandeel berichten tijdens carnaval")
    plt.title("Carnavalactiviteit: aangetrouwd versus niet")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Afbeelding opgeslagen als: {output_path}")


def generate_correlation_diagram(df: pd.DataFrame, output_path: Path, columns: dict):
    """
    Genereert een heatmap van correlaties tussen persoonskenmerken en chatgedrag.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Maak persoonsniveau-data aan
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
                columns["timestamp"]: "count",  # Aantal berichten
            }
        )
        .rename(columns={columns["timestamp"]: "message_count"})
        .reset_index()
    )

    # Verwijder records met ontbrekende waarden
    person_df = person_df.dropna()

    # Zet gender ('m' / 'f') om naar numeriek (0 / 1)
    person_df["gender_num"] = (
        person_df[columns["gender"]].str.lower().map({"m": 0, "f": 1})
    )

    # Bepaal correlaties tussen numerieke variabelen
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

    # Plot de correlatiematrix
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlaties tussen persoonskenmerken en gedrag")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Afbeelding opgeslagen als: {output_path}")


def generate_relation_charts(df: pd.DataFrame, output_dir: Path, les5_settings: dict):
    """
    Wrapper-functie die beide les 5 visualisaties uitvoert:
    - Correlatiematrix
    - Boxplot carnavalactiviteit vs. in-law status
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    columns = les5_settings.get("columns", {})
    output_files = les5_settings.get("output_files", {})

    # Genereer correlatiematrix
    generate_correlation_diagram(
        df,
        output_dir / output_files.get("correlation", "correlaties.png"),
        columns,
    )

    # Genereer carnaval vs. in-law vergelijking
    generate_relations_chart(
        df,
        output_dir / output_files.get("carnaval_relation", "carnaval_vs_inlaw.png"),
        columns,
    )
