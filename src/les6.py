from pathlib import Path
import pandas as pd
from loguru import logger
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import manhattan_distances
from sklearn.feature_extraction.text import CountVectorizer

from plot_utils import plot_pca_tsne
from plot_settings import set_plot_style

def prepare_chunks(df: pd.DataFrame, chunk_size: int = 200, min_chunks: int = 20) -> pd.DataFrame:
    """
    Maak tekstchunks van WhatsApp-berichten, gegroepeerd per auteur.
    """
    grouped = df.groupby("author")["message"].apply(lambda x: " ".join(str(m) for m in x)).reset_index()

    def split_text(text, size):
        words = text.split()
        return [" ".join(words[i: i + size]) for i in range(0, len(words), size)]

    chunk_data = []
    for _, row in grouped.iterrows():
        chunks = split_text(row["message"], chunk_size)
        for chunk in chunks:
            if len(chunk.split()) > 20:
                chunk_data.append({"author": row["author"], "text": chunk})

    chunk_df = pd.DataFrame(chunk_data)

    # Alleen auteurs met genoeg chunks
    author_counts = chunk_df["author"].value_counts()
    valid_authors = author_counts[author_counts >= min_chunks].index
    chunk_df = chunk_df[chunk_df["author"].isin(valid_authors)].reset_index(drop=True)

    logger.info(f"Chunks voorbereid: {len(chunk_df)} berichten van {chunk_df['author'].nunique()} auteurs.")
    return chunk_df

def generate_les6_charts(df: pd.DataFrame, output_dir: Path, les6_settings: dict):
    """
    Volledige pipeline voor Les 6: chunks maken, PCA en t-SNE grafieken genereren.
    """
    set_plot_style()

    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    chunk_df = prepare_chunks(
        df,
        chunk_size=les6_settings.get("chunk_size", 200),
        min_chunks=les6_settings.get("min_chunks", 20),
    )

    vectorizer = CountVectorizer(analyzer="char", ngram_range=(3, 3))
    X = vectorizer.fit_transform(chunk_df["text"])
    distance = manhattan_distances(X, X)
    labels = chunk_df["author"].reset_index(drop=True)

    highlight_author = les6_settings.get("highlight_author", "sprightly-rhinoceros")

    # === PCA plot
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(distance)
    pca_df = pd.DataFrame({"x": X_pca[:, 0], "y": X_pca[:, 1], "author": labels})

    plot_pca_tsne(
        df=pca_df,
        x="x",
        y="y",
        label_col="author",
        highlight_label=highlight_author,
        title=les6_settings["pca_chart"]["title"],
        output_path=output_dir / les6_settings["output_files"]["pca"],
        highlight_color=les6_settings["pca_chart"].get("highlight_color", "red"),
        other_color=les6_settings["pca_chart"].get("other_color", "lightgrey"),
    )

    # === t-SNE plot
    tsne = TSNE(n_components=2, perplexity=les6_settings.get("perplexity", 30), random_state=42)
    X_tsne = tsne.fit_transform(distance)
    tsne_df = pd.DataFrame({"x": X_tsne[:, 0], "y": X_tsne[:, 1], "author": labels})

    plot_pca_tsne(
        df=tsne_df,
        x="x",
        y="y",
        label_col="author",
        highlight_label=highlight_author,
        title=les6_settings["tsne_chart"]["title"],
        output_path=output_dir / les6_settings["output_files"]["tsne"],
        highlight_color=les6_settings["tsne_chart"].get("highlight_color", "red"),
        other_color=les6_settings["tsne_chart"].get("other_color", "lightgrey"),
    )
