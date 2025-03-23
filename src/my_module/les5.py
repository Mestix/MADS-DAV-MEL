import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from loguru import logger
import warnings
import tomllib
from pydantic import BaseModel

warnings.simplefilter(action="ignore", category=FutureWarning)

class Config(BaseModel):
    processed: str
    current: str

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data)

def load_data(config: Config) -> pd.DataFrame:
    root = Path(".").resolve()
    processed = root / Path(config.processed)
    datafile = processed / config.current
    
    if not datafile.exists():
        logger.warning(
            f"{datafile} does not exist. First run analyzer --device ios"
        )
        return pd.DataFrame()
    
    return pd.read_parquet(datafile)

def generate_relations_chart(df: pd.DataFrame, output_path: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return

    # Zorg dat timestamp en date kolommen goed staan
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    # Definieer carnavalsperiodes
    carnaval_2024 = (pd.to_datetime('2024-02-08').date(), pd.to_datetime('2024-02-15').date())
    carnaval_2025 = (pd.to_datetime('2025-02-27').date(), pd.to_datetime('2025-03-04').date())

    # Voeg is_carnaval toe
    def is_carnaval(date):
        return (
            carnaval_2024[0] <= date <= carnaval_2024[1] or
            carnaval_2025[0] <= date <= carnaval_2025[1]
        )
    df['is_carnaval'] = df['date'].apply(is_carnaval)

    # Groepeer per persoon en bereken carnaval-ratio
    person_df = df.groupby('author').agg({
        'is_carnaval': 'mean',
        'gender': 'first'
    }).reset_index()

    # Filter op bekende gender en lowercase
    person_df = person_df[person_df['gender'].notna()]
    person_df['gender'] = person_df['gender'].str.lower()

    # Plot
    plt.figure(figsize=(6, 5))
    sns.boxplot(
        data=person_df,
        x='gender',
        y='is_carnaval',
        palette={'m': '#0077B6', 'f': '#FF69B4'}
    )
    plt.xlabel('Geslacht')
    plt.ylabel('Aandeel berichten tijdens carnaval')
    plt.title('Carnavalactiviteit per geslacht')
    plt.tight_layout()

    # Sla op
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Afbeelding opgeslagen als: {output_path}")

