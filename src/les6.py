from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import manhattan_distances
from loguru import logger


def prepare_chunks(df: pd.DataFrame, chunk_size: int = 200, min_chunks: int = 20) -> pd.DataFrame:
    """
    Maak chunks van tekst van een dataframe met WhatsApp-berichten.
    Groepeer berichten per auteur en splits in chunks van ongeveer 'chunk_size' woorden.
    """
    grouped = df.groupby('author')['message'].apply(lambda x: ' '.join(str(m) for m in x)).reset_index()

    def split_text(text, size):
        words = text.split()
        return [' '.join(words[i:i + size]) for i in range(0, len(words), size)]

    chunk_data = []
    for _, row in grouped.iterrows():
        chunks = split_text(row['message'], chunk_size)
        for chunk in chunks:
            if len(chunk.split()) > 20:
                chunk_data.append({'author': row['author'], 'text': chunk})

    chunk_df = pd.DataFrame(chunk_data)

    # Filter auteurs met genoeg chunks
    author_counts = chunk_df['author'].value_counts()
    valid_authors = author_counts[author_counts >= min_chunks].index
    chunk_df = chunk_df[chunk_df['author'].isin(valid_authors)].reset_index(drop=True)

    logger.info(f"Chunks voorbereid: {len(chunk_df)} berichten van {chunk_df['author'].nunique()} auteurs.")
    return chunk_df


def generate_pca_plot(X, labels, output_path: Path, highlight_author: str):
    """
    Voert PCA uit en plot de data.
    Alleen 'highlight_author' krijgt een kleur, anderen worden grijs.
    """
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    pca_df = pd.DataFrame({
        "x": X_pca[:, 0],
        "y": X_pca[:, 1],
        "author": labels
    })

    plt.figure(figsize=(6, 4))

    # Eerst alle auteurs grijs plotten
    sns.scatterplot(
        data=pca_df[pca_df["author"] != highlight_author],
        x="x", y="y",
        color="lightgrey",
        s=50,
        label="Overige auteurs"
    )

    # Dan highlight author
    sns.scatterplot(
        data=pca_df[pca_df["author"] == highlight_author],
        x="x", y="y",
        color="red",
        s=70,
        label=highlight_author
    )

    plt.title(f"PCA visualisatie ({highlight_author} gemarkeerd)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"PCA-plot opgeslagen als {output_path}")


def generate_tsne_plot(X, labels, output_path: Path, highlight_author: str, perplexity: int = 30):
    """
    Voert t-SNE uit en plot de data.
    Alleen 'highlight_author' krijgt een kleur, anderen worden grijs.
    """
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    X_tsne = tsne.fit_transform(X)

    tsne_df = pd.DataFrame({
        "x": X_tsne[:, 0],
        "y": X_tsne[:, 1],
        "author": labels
    })

    plt.figure(figsize=(6, 4))

    sns.scatterplot(
        data=tsne_df[tsne_df["author"] != highlight_author],
        x="x", y="y",
        color="lightgrey",
        s=50,
        label="Overige auteurs"
    )

    sns.scatterplot(
        data=tsne_df[tsne_df["author"] == highlight_author],
        x="x", y="y",
        color="red",
        s=70,
        label=highlight_author
    )

    plt.title(f"t-SNE visualisatie ({highlight_author} gemarkeerd)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    logger.info(f"t-SNE-plot opgeslagen als {output_path}")


def generate_les6_charts(df: pd.DataFrame, output_dir: Path, les6_settings: dict):
    """
    Draait de volledige pipeline voor Les 6:
    1. Bereidt tekst-chunks voor
    2. Vectoriseert tekst naar numerieke features
    3. Berekent afstanden tussen chunks
    4. Genereert PCA- en t-SNE-visualisaties van schrijfstijl
    Alles wordt aangestuurd via instellingen uit les6_settings.
    """

    # Check of het dataframe niet leeg is
    if df.empty:
        logger.warning("Dataframe is leeg. Geen visualisaties gegenereerd.")
        return

    # Bereid de tekst-chunks voor: groepsgewijs splitsen in stukken van 'chunk_size' woorden
    chunk_df = prepare_chunks(
        df,
        chunk_size=les6_settings.get("chunk_size", 200),
        min_chunks=les6_settings.get("min_chunks", 20)
    )

    # Vectoriseer de tekst: representatie maken op basis van character 3-grams
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(analyzer="char", ngram_range=(3, 3))
    X = vectorizer.fit_transform(chunk_df['text'])

    # Bereken pairwise Manhattan-afstanden tussen alle chunks
    distance = manhattan_distances(X, X)

    # Extract labels (de bijbehorende auteurs) voor latere kleuring in de plots
    labels = chunk_df['author'].reset_index(drop=True)

    # Zet output-bestanden klaar (paden naar de images)
    pca_output = output_dir / les6_settings["output_files"]["pca"]
    tsne_output = output_dir / les6_settings["output_files"]["tsne"]

    # Haal de auteur op die we speciaal willen highlighten
    highlight_author = les6_settings.get("highlight_author", "sprightly-rhinoceros")

    # Maak de PCA-plot met alle auteurs lichtgrijs behalve de highlight-auteur
    generate_pca_plot(distance, labels, pca_output, highlight_author)

    # Maak de t-SNE-plot met dezelfde logica
    generate_tsne_plot(
        distance,
        labels,
        tsne_output,
        highlight_author,
        perplexity=les6_settings.get("perplexity", 30)
    )

