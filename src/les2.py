from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from loguru import logger


def generate_question_bar_chart(df: pd.DataFrame, img_folder: Path, les2_settings: dict):
    """
    Genereer een horizontale staafgrafiek van het aantal vragen per gebruiker.
    Gebruikt settings voor kleuring, annotatie en bestandsnaam.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Kolomnamen
    col_author = les2_settings["columns"]["author"]
    col_message = les2_settings["columns"]["message"]

    # Vragen tellen
    df["questions"] = df[col_message].apply(lambda x: str(x).count("?"))
    vraag_count = df.groupby(col_author)["questions"].sum().reset_index()
    vraag_count = vraag_count.sort_values(by="questions", ascending=False)
    vraag_count = vraag_count[vraag_count["questions"] > 0]

    # Kleuren per gebruiker
    me = les2_settings["highlight_users"]["me"]
    inlaw = les2_settings["highlight_users"]["inlaw"]

    colors = [
        "red" if author == me
        else "blue" if author == inlaw
        else "grey"
        for author in vraag_count[col_author]
    ]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.barh(vraag_count[col_author], vraag_count["questions"], color=colors)
    plt.xlabel("Aantal Vragen")
    plt.ylabel("Gebruiker")
    plt.title("Deze groepsleden stellen de meeste vragen")
    plt.gca().invert_yaxis()

    # Annotatie voor inlaw
    annotation_user = les2_settings["annotation"]["user"]
    annotation_text = les2_settings["annotation"]["text"]

    if annotation_user in vraag_count[col_author].values:
        y_pos = list(vraag_count[col_author]).index(annotation_user)
        x_value = vraag_count["questions"].iloc[y_pos]

        plt.xlim(right=x_value + 10)
        plt.annotate(
            annotation_text,
            xy=(x_value, y_pos),
            xytext=(x_value + 8, y_pos),
            arrowprops=dict(facecolor="blue", arrowstyle="->"),
            fontsize=12,
            color="blue",
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="white"),
        )

    # Legenda
    plt.subplots_adjust(right=0.75)
    legend_handles = [
        mpatches.Patch(color="red", label="Ik"),
        mpatches.Patch(color="blue", label="Mijn Schoonmoeder"),
        mpatches.Patch(color="grey", label="Overige groepsleden"),
    ]
    plt.legend(handles=legend_handles, title="Legenda", loc="lower right", bbox_to_anchor=(1, 0))

    # Opslaan
    output_path = img_folder / les2_settings["output_image"]
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Afbeelding opgeslagen als: {output_path}")
