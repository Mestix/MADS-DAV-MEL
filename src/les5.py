import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger

warnings.simplefilter(action="ignore", category=FutureWarning)


def generate_relations_chart(df: pd.DataFrame, output_path: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Groepeert per persoon en bereken carnaval-ratio
    person_df = (
        df.groupby("author")
        .agg({"is_carnaval": "mean", "is_inlaw": "first"})
        .reset_index()
    )

    # Filtert op bekende gender en lowercase
    person_df = person_df[person_df["is_inlaw"].notna()]
    person_df["is_inlaw_label"] = person_df["is_inlaw"].map({0: "Nee", 1: "Ja"})

    # Plot
    plt.figure(figsize=(6, 5))
    sns.boxplot(
        data=person_df,
        x="is_inlaw_label",
        y="is_carnaval",
        palette={"Nee": "skyblue", "Ja": "lightcoral"},
    )
    plt.xlabel("Is aangetrouwd?")
    plt.ylabel("Aandeel berichten tijdens carnaval")
    plt.title("Carnavalactiviteit aangetrouwd ja of nee")
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"Afbeelding opgeslagen als: {output_path}")


def generate_corelation_diagram(df: pd.DataFrame, output_path: Path):
    # nieuw DataFrame op persoonsniveau
    person_df = (
        df.groupby("author")
        .agg(
            {
                "emoji_count": "mean",
                "message_length": "mean",
                "age": "first",
                "gender": "first",
                "is_inlaw": "first",
                "is_carnaval": "mean",  # Hoeveel % van hun berichten zijn tijdens carnaval
                "timestamp": "count",  # Aantal berichten
            }
        )
        .rename(columns={"timestamp": "message_count"})
        .reset_index()
    )

    # Haal NAN weg
    person_df = person_df[person_df.notna()].copy()

    # Zet gender om naar numeriek
    person_df["gender_num"] = person_df["gender"].str.lower().map({"m": 0, "f": 1})

    # Alleen numerieke kolommen gebruiken
    corr = person_df[
        [
            "age",
            "emoji_count",
            "message_length",
            "message_count",
            "is_carnaval",
            "gender_num",
            "is_inlaw",
        ]
    ].corr()

    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlaties tussen persoonskenmerken en gedrag")
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    logger.info(f"Afbeelding opgeslagen als: {output_path}")
    plt.close()


def generate_relation_charts(df: pd.DataFrame, output_dir: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    generate_corelation_diagram(df, output_dir / "les5_correlaties.png")
    generate_relations_chart(df, output_dir / "les5_carnaval_vs_aangetrouwd")
