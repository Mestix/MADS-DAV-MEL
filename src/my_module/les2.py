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
            f"{datafile} does not exist. First run src/preprocess.py, and check the timestamp!"
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
    
    plt.figure(figsize=(10, 5))
    plt.barh(vraag_count["author"], vraag_count["questions"], color='grey')
    plt.xlabel("Aantal Vragen")
    plt.ylabel("Gebruiker")
    plt.title("Meest nieuwsgierige groepsleden")
    plt.gca().invert_yaxis()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    logger.info(f"Afbeelding opgeslagen als: {output_path}")
    # plt.show()

if __name__ == "__main__":
    # Laad de configuratie
    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)

    # Laad de data
    df = load_data(config)

    # Geef het pad op waar de afbeelding moet worden opgeslagen
    output_path = Path("./img/aantal_gestelde_vragen_per_gebruiker.jpg")

    # Genereer de grafiek
    generate_question_bar_chart(df, output_path)
