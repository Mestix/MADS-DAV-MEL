import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd


def plot_horizontal_bar(
    data,
    value_col,
    label_col,
    colors,
    xlabel,
    ylabel,
    title,
    annotation=None,
    legend_labels=None,
    output_path=None,
    legend_colors=None,
):
    """
    Plot een horizontale staafdiagram met optionele annotatie en legenda.
    """
    plt.figure()

    # Plot de staafdiagram
    plt.barh(data[label_col], data[value_col], color=colors)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gca().invert_yaxis()

    # Annotatie toevoegen (optioneel)
    if annotation:
        user = annotation.get("user")
        text = annotation.get("text")
        color = annotation.get("arrow_color", "blue")

        if user in data[label_col].values:
            y_pos = list(data[label_col]).index(user)
            x_value = data[value_col].iloc[y_pos]

            plt.xlim(right=x_value + 10)
            plt.annotate(
                text,
                xy=(x_value, y_pos),
                xytext=(x_value + 8, y_pos),
                arrowprops=dict(facecolor=color, arrowstyle="->"),
                fontsize=12,
                color=color,
                bbox=dict(boxstyle="round,pad=0.3", edgecolor=color, facecolor="white"),
            )

    # Legenda toevoegen (optioneel)
    if legend_labels and legend_colors:
        legend_handles = [
            mpatches.Patch(color=legend_colors[key], label=label)
            for key, label in legend_labels.items()
        ]
        plt.legend(
            handles=legend_handles,
            title="Legenda",
            loc="lower right",
            bbox_to_anchor=(1, 0),
        )

    # Opslaan of tonen
    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_line_chart(
    x,
    y,
    highlight_ranges=None,
    xlabel="",
    ylabel="",
    title="",
    output_path=None,
    highlight_color="orange",
    highlight_label="Highlight",
):
    """
    Eenvoudige lijnplot met optionele highlight-blokken (bijv. carnavalperiodes).
    """
    plt.figure()
    plt.plot(x, y, marker="o", label="Aantal berichten")

    if highlight_ranges:
        for start, end in highlight_ranges:
            plt.axvspan(
                start, end, color=highlight_color, alpha=0.3, label=highlight_label
            )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Legenda opschonen
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_line_with_vertical_marker(
    data,
    x,
    y,
    hue=None,
    xlabel="",
    ylabel="",
    title="",
    output_path=None,
    marker_position=0,
    marker_label="Marker",
):
    """
    Lijnplot uit DataFrame, met verticale markerlijn (bijv. start carnaval).
    """
    plt.figure()
    sns.lineplot(data=data, x=x, y=y, hue=hue, marker="o")

    plt.axvline(marker_position, color="gray", linestyle="--", label=marker_label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    plt.legend(title=hue)

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()

def plot_boxplot(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str,
    ylabel: str,
    title: str,
    palette: dict = None,
    output_path: str = None,
):

    plt.figure()
    sns.boxplot(
        data=data,
        x=x_col,
        y=y_col,
        # palette=palette
    )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()

def plot_heatmap(
    corr_matrix: pd.DataFrame,
    title: str,
    output_path: str = None,
):
    """
    Plot een heatmap voor correlaties.
    """
    plt.figure()

    sns.heatmap(
        corr_matrix,
        annot=True,        # Toon de getallen in de cellen
        fmt=".2f",         # Rond getallen af op 2 decimalen
        cmap="coolwarm",   # Kleurenpalet
        linewidths=0.5,    # Witte lijnen tussen cellen
        linecolor="white"
    )

    plt.title(title)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()