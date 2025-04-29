from pathlib import Path

import pandas as pd
from loguru import logger

from plot_settings import set_plot_style
from plot_utils import plot_horizontal_bar


def generate_question_bar_chart(
    df: pd.DataFrame, img_folder: Path, les2_settings: dict
):
    """
    Genereer een bar chart van aantal vragen per gebruiker, volledig gestuurd door settings.
    """

    set_plot_style()

    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    col_author = les2_settings["columns"]["author"]
    col_message = les2_settings["columns"]["message"]

    # Vragen tellen
    df["questions"] = df[col_message].apply(lambda x: str(x).count("?"))
    vraag_count = (
        df.groupby(col_author)["questions"]
        .sum()
        .reset_index()
        .sort_values(by="questions", ascending=False)
    )
    vraag_count = vraag_count[vraag_count["questions"] > 0]

    if vraag_count.empty:
        logger.warning("Geen vragen gevonden om te plotten.")
        return

    # Kleuren per persoon
    colors_config = les2_settings["plot"]["colors"]
    me = les2_settings["highlight_users"]["me"]
    inlaw = les2_settings["highlight_users"]["inlaw"]

    colors = [
        (
            colors_config["me"]
            if author == me
            else colors_config["inlaw"] if author == inlaw else colors_config["other"]
        )
        for author in vraag_count[col_author]
    ]

    output_path = img_folder / les2_settings["output_image"]

    # Plot
    plot_horizontal_bar(
        vraag_count,
        value_col="questions",
        label_col=col_author,
        colors=colors,
        xlabel=les2_settings["plot"]["xlabel"],
        ylabel=les2_settings["plot"]["ylabel"],
        title=les2_settings["plot"]["title"],
        annotation=les2_settings["annotation"],
        legend_labels=les2_settings["plot"]["legend_labels"],
        legend_colors=les2_settings["plot"]["colors"],
        output_path=output_path,
    )

    logger.success(f"Afbeelding opgeslagen als: {output_path}")
