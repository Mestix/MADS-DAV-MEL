import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from loguru import logger
import numpy as np
from scipy.stats import lognorm
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

def generate_message_length_distribution(df: pd.DataFrame, output_path: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Bepaal berichtlengtes
    df = df.copy()
    df['message_length'] = df['message'].astype(str).str.len()
    message_lengths = df['message_length']
    positive_lengths = message_lengths[message_lengths > 0]

    # Maak bins: 0–200 in stappen van 1 + alles daarboven in 1 bin
    bins = list(range(0, 200, 1)) + [positive_lengths.max()]

    # Fit een lognormale verdeling
    shape, loc, scale = lognorm.fit(positive_lengths, floc=0)
    x = np.linspace(positive_lengths.min(), 200, 1000)
    pdf = lognorm.pdf(x, shape, loc=loc, scale=scale)

    # Plot histogram + lognormale fit
    plt.figure(figsize=(14, 5))
    sns.histplot(
        positive_lengths,
        bins=bins,
        stat="probability",
        color="skyblue",
        edgecolor="black",
        label="Data"
    )

    plt.plot(x, pdf, "r", lw=2, label="Lognormale fit")
    plt.xlim(0, 200)
    xticks = list(range(0, 200, 20)) + [200]
    xtick_labels = [str(x) for x in xticks[:-1]] + ['200+']
    plt.xticks(xticks, xtick_labels)

    plt.xlabel("Aantal tekens per bericht")
    plt.ylabel("Kans")
    plt.title("Lognormale fit op berichtlengte in de familiechat")
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_path, bbox_inches="tight")
    logger.info(f"Afbeelding opgeslagen als: {output_path}")
    plt.close()

def generate_distribution_charts(df: pd.DataFrame, output_dir: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    generate_message_length_distribution(df, output_dir / "les4_berichtlengte_distributie.png")
