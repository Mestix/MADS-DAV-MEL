from pathlib import Path
from typing import Optional
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger


def save_or_show(output_path: Optional[Path] = None):
    "Slaat grafiek op naar bestand of toont deze direct."
    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
        logger.success(f"Plot opgeslagen: {output_path}")
    else:
        plt.show()
        logger.info("Plot getoond op scherm.")


# Les 2
def plot_horizontal_bar(
    data,
    value_col,
    label_col,
    colors,
    xlabel,
    ylabel,
    title,
    annotation,
    legend_labels,
    legend_colors,
    arrow_color,
    output_path,
):
    "Maakt een horizontale staafdiagram met annotatie en legenda."
    plt.figure()

    plt.barh(data[label_col], data[value_col], color=colors)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gca().invert_yaxis()

    user = annotation["user"]
    text = annotation["text"]
    if user in data[label_col].values:
        y_pos = list(data[label_col]).index(user)
        x_value = data[value_col].iloc[y_pos]
        plt.xlim(right=x_value + 10)
        plt.annotate(
            text,
            xy=(x_value, y_pos),
            xytext=(x_value + 8, y_pos),
            arrowprops=dict(facecolor=arrow_color, arrowstyle="->"),
            fontsize=12,
            color=arrow_color,
            bbox=dict(
                boxstyle="round,pad=0.3", edgecolor=arrow_color, facecolor="white"
            ),
        )

    handles = [
        mpatches.Patch(color=legend_colors[k], label=v)
        for k, v in legend_labels.items()
    ]
    plt.legend(
        handles=handles, title="Legenda", loc="lower right", bbox_to_anchor=(1, 0)
    )

    plt.tight_layout()
    save_or_show(output_path)


# Les 3
def plot_line_chart(
    x,
    y,
    highlight_ranges,
    xlabel,
    ylabel,
    title,
    highlight_color,
    highlight_label,
    output_path,
):
    "Maakt een lijnplot met optionele highlightblokken."
    plt.figure()

    plt.plot(x, y, marker="o", label="Aantal berichten")
    for start, end in highlight_ranges:
        plt.axvspan(start, end, color=highlight_color, alpha=0.3, label=highlight_label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.tight_layout()
    save_or_show(output_path)


def plot_line_with_vertical_marker(
    data, x, y, marker_position, marker_label, xlabel, ylabel, title, hue, output_path
):
    "Maakt een lijnplot met een verticale marker."
    plt.figure()

    sns.lineplot(data=data, x=x, y=y, hue=hue, marker="o")
    plt.axvline(marker_position, color="gray", linestyle="--", label=marker_label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title=hue)

    plt.tight_layout()
    save_or_show(output_path)


# Les 4
def plot_distribution(
    x_labels, y_values, xlabel, ylabel, title, highlight_color, grey_color, output_path
):
    """
    Maakt een distributie-barplot waarbij top 3 hoogste kansen de highlight kleur krijgen en de rest lichtgrijs.
    """
    # Zet y_values om naar Series om makkelijk top 3 te pakken
    y_series = pd.Series(y_values, index=x_labels)
    top_3_labels = y_series.sort_values(ascending=False).index[:3]

    # top 3 = highlight_color, rest = grey
    colors = [
        highlight_color if label in top_3_labels else grey_color for label in x_labels
    ]

    sns.barplot(x=x_labels, y=y_values, palette=colors, hue=x_labels, legend=False)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()

    save_or_show(output_path)


# Les 5
def plot_boxplot(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str,
    ylabel: str,
    title: str,
    palette: dict,
    output_path: Path,
):
    "Maakt een eenvoudige boxplot met kleuren."
    plt.figure()

    sns.boxplot(data=data, x=x_col, y=y_col, palette=palette, hue=x_col)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.tight_layout()
    save_or_show(output_path)


def plot_heatmap(corr_matrix: pd.DataFrame, title: str, output_path: Path):
    "Maakt een heatmap van een correlatiematrix."
    plt.figure()

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linewidths=0.5,
        linecolor="white",
    )

    plt.title(title)
    plt.tight_layout()
    save_or_show(output_path)


# Les 6
def plot_pca_tsne(
    df: pd.DataFrame,
    x: str,
    y: str,
    label_col: str,
    highlight_label: str,
    title: str,
    highlight_color: str,
    other_color: str,
    output_path: Path,
):
    "Maakt een scatterplot voor PCA of t-SNE met 1 auteur gehighlight."
    plt.figure(figsize=(8, 5))

    sns.scatterplot(
        data=df[df[label_col] != highlight_label],
        x=x,
        y=y,
        color=other_color,
        label="Andere auteurs",
    )
    sns.scatterplot(
        data=df[df[label_col] == highlight_label],
        x=x,
        y=y,
        color=highlight_color,
        label=highlight_label,
    )

    plt.title(title)
    plt.legend()
    plt.tight_layout()
    save_or_show(output_path)
