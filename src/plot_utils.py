import matplotlib.patches as mpatches
from matplotlib import pyplot as plt


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
    legend_colors=None,  # <-- Extra toegevoegd
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
