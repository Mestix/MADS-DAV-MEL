from pathlib import Path
import pandas as pd
from loguru import logger
from plot_utils import plot_distribution


def generate_distribution_charts(df: pd.DataFrame, img_folder: Path, settings: dict):
    """
    Genereert een distributieplot van de kans op een bericht per dag van de week.
    """
    if df.empty:
        logger.warning("Dataframe is leeg. Geen distributie gegenereerd.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["day_of_week"] = df["timestamp"].dt.day_name()

    distribution = (
        df["day_of_week"]
        .value_counts(normalize=True)
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
        .fillna(0)
    )

    output_path = img_folder / settings["output_files"]["week_distribution"]

    plot_distribution(
        x_labels=distribution.index.tolist(),
        y_values=distribution.values.tolist(),
        xlabel=settings["plot"]["xlabel"],
        ylabel=settings["plot"]["ylabel"],
        title=settings["plot"]["title"],
        highlight_color=settings["plot"]["highlight_color"],
        grey_color=settings["plot"]["grey_color"],
        output_path=output_path,
    )

    logger.success(f"Distributieplot opgeslagen als: {output_path}")
