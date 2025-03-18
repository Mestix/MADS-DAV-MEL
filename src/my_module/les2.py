import matplotlib.pyplot as plt
import pandas as pd
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

def generate_question_bar_chart(df: pd.DataFrame, output_path: Path):
    if df.empty:
        logger.warning("Dataframe is leeg. Kan geen grafiek genereren.")
        return
    
    df["questions"] = df["message"].apply(lambda x: str(x).count("?"))
    vraag_count = df.groupby("author")["questions"].sum().reset_index()
    vraag_count = vraag_count.sort_values(by="questions", ascending=False)
    vraag_count = vraag_count[vraag_count["questions"] > 0]

    # "laughing-cat" wordt rood, "decorated-shark" wordt blauw
    colors = [
        "red" if author == "laughing-cat" else 
        "blue" if author == "decorated-shark" else 
        "grey" 
        for author in vraag_count["author"]
    ]

    plt.figure(figsize=(10, 5))
    bars = plt.barh(vraag_count["author"], vraag_count["questions"], color=colors)
    plt.xlabel("Aantal Vragen")
    plt.ylabel("Gebruiker")
    plt.title("Deze groepsleden stellen de meeste vragen")

    plt.gca().invert_yaxis()  # Hoogste waarde bovenaan

    # y-positie van "decorated-shark"  (door chatGPT)
    if "decorated-shark" in vraag_count["author"].values:
        y_pos = list(vraag_count["author"]).index("decorated-shark")
        x_value = vraag_count["questions"].iloc[y_pos]  # Aantal vragen van decorated-shark 

        plt.xlim(right=x_value + 10)
        plt.annotate(
            "Mijn schoonmoeder:\n\"Wie komt er eten?\" =P",
            xy=(x_value, y_pos),  # Pijl naar de bar
            xytext=(x_value + 8, y_pos),  # Tekst nog verder naar rechts
            arrowprops=dict(facecolor='blue', arrowstyle="->"),
            fontsize=12,
            color="blue",
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="white")
        )

    # Extra marges om te zorgen dat de tekst niet buiten de afbeelding valt
    plt.subplots_adjust(right=0.75)  
    plt.savefig(output_path, bbox_inches="tight")  # Zorgt dat alles in beeld blijft

    logger.info(f"Afbeelding opgeslagen als: {output_path}")
    
    print("Grafiek gemaakt")

