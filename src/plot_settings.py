import tomllib
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns
from pydantic import BaseModel


class PlotSettings(BaseModel):
    style: str
    context: str
    palette: str
    figsize: tuple
    title_size: int
    label_size: int
    tick_size: int
    legend_size: int

    @classmethod
    def load_from_toml(cls, path: Path):
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls(**data["plot"])  # Zorg dat je in settings.toml een [plot] blok hebt!


def set_plot_style(settings: Optional[PlotSettings] = None):
    """
    Zet de standaardstijl voor alle plots.
    """
    if settings is None:
        settings = PlotSettings.load_from_toml(Path("./settings.toml"))

    sns.set_theme(
        style=settings.style,
        context=settings.context,
        palette=settings.palette,
    )

    plt.rcParams.update(
        {
            "figure.figsize": settings.figsize,
            "axes.titlesize": settings.title_size,
            "axes.labelsize": settings.label_size,
            "xtick.labelsize": settings.tick_size,
            "ytick.labelsize": settings.tick_size,
            "legend.fontsize": settings.legend_size,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
