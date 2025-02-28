# create_image.py

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from loguru import logger
import warnings
import tomllib

warnings.simplefilter(action="ignore", category=FutureWarning)

def generate_question_bar_chart():
    # Laad de configuratie uit het TOML-bestand
    configfile = Path("./config.toml").resolve()
    with configfile.open("rb") as f:
        config = tomllib.load(f)

    root = Path(".").resolve()
    processed = root / Path(config["processed"])
    datafile = processed / config["current"]
    
    if not datafile.exists():
        logger.warning(
            f"{datafile} does not exist. First run src/preprocess.py, and check the timestamp!"
        )
        return
    
    df = pd.read_parquet(datafile)

    # Voeg een kolom toe die het aantal vraagtekens in elk bericht telt
    df["questions"] = df["message"].apply(lambda x: str(x).count("?"))

    # Groepeer per gebruiker en tel het aantal vraagtekens
    vraag_count = df.groupby("author")["questions"].sum().reset_index()

    # Sorteer op de meeste gestelde vragen
    vraag_count = vraag_count.sort_values(by="questions", ascending=False)

    # Verwijder gebruikers die 0 vragen hebben gesteld
    vraag_count = vraag_count[vraag_count["questions"] > 0]

    # Maak een staafdiagram van de gebruikers die de meeste vragen stellen
    plt.figure(figsize=(10, 5))
    plt.barh(vraag_count["author"], vraag_count["questions"], color='grey') # Begin met grijs
    plt.xlabel("Aantal Vragen")
    plt.ylabel("Gebruiker")
    plt.title("Meest nieuwsgierige groepsleden")
    plt.gca().invert_yaxis()  # Zodat de gebruiker met de meeste vragen bovenaan staat

    # Zorg ervoor dat de 'img' map bestaat
    img_folder = Path("./img")
    if not img_folder.exists():
        img_folder.mkdir(parents=True)

    # Opslaan van de figuur als een afbeelding in de 'img' map
    output_path = img_folder / "aantal_gestelde_vragen_per_gebruiker.jpg"
    plt.savefig(output_path)
    logger.info(f"Afbeelding opgeslagen als: {output_path}")

    # plt.show()
