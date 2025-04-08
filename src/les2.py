import warnings
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

warnings.simplefilter(action="ignore", category=FutureWarning)


def generate_question_bar_chart(df: pd.DataFrame, img_folder: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    df["questions"] = df["message"].apply(lambda x: str(x).count("?"))
    vraag_count = df.groupby("author")["questions"].sum().reset_index()
    vraag_count = vraag_count.sort_values(by="questions", ascending=False)
    vraag_count = vraag_count[vraag_count["questions"] > 0]

    # "laughing-cat" wordt rood, "decorated-shark" wordt blauw
    colors = [
        (
            "red"
            if author == "laughing-cat"
            else "blue" if author == "decorated-shark" else "grey"
        )
        for author in vraag_count["author"]
    ]

    plt.figure(figsize=(10, 5))
    plt.barh(vraag_count["author"], vraag_count["questions"], color=colors)
    plt.xlabel("Aantal Vragen")
    plt.ylabel("Gebruiker")
    plt.title("Deze groepsleden stellen de meeste vragen")
    plt.gca().invert_yaxis()  # Hoogste waarde bovenaan

    # y-positie van "decorated-shark" (door ChatGPT bepaald)
    if "decorated-shark" in vraag_count["author"].values:
        y_pos = list(vraag_count["author"]).index("decorated-shark")
        x_value = vraag_count["questions"].iloc[y_pos]

        plt.xlim(right=x_value + 10)
        plt.annotate(
            'Mijn schoonmoeder:\n"Wie komt er eten?" =P',
            xy=(x_value, y_pos),
            xytext=(x_value + 8, y_pos),
            arrowprops=dict(facecolor="blue", arrowstyle="->"),
            fontsize=12,
            color="blue",
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="white"),
        )

    plt.subplots_adjust(right=0.75)

    legend_handles = [
        mpatches.Patch(color="red", label="Ik"),
        mpatches.Patch(color="blue", label="Mijn Schoonmoeder"),
        mpatches.Patch(color="grey", label="Overige groepsleden"),
    ]
    plt.legend(
        handles=legend_handles,
        title="Legenda",
        loc="lower right",
        bbox_to_anchor=(1, 0),
    )

    output_path = img_folder / "les2_meeste_vragen_gesteld.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Afbeelding opgeslagen als: {output_path}")
