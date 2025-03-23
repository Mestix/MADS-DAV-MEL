import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger
from wa_analyzer.humanhasher import humanize
import tomllib

def preprocess_data(config_path: Path) -> None:
    # Load config and paths
    with config_path.open("rb") as f:
        config = tomllib.load(f)

    processed = Path(config["processed"])
    inputfile = processed / config["inputpath"]

    if not inputfile.exists():
        logger.warning(f"{inputfile} does not exist. Maybe first run wa-analyzer")
        return

    # Read data
    df = pd.read_csv(inputfile, parse_dates=["timestamp"])
    logger.info(f"Data geladen met {len(df)} rijen.")

    # Clean ~ + unicode from author
    clean_tilde = r"^~\u202f"
    df["author"] = df["author"].apply(lambda x: re.sub(clean_tilde, "", x))

    # Anonymiseer authors
    authors = df["author"].unique()
    anon_map = {k: humanize(k) for k in authors}
    assert len(anon_map) == len(authors), "Aantal authors klopt niet, check anonimisering"

    # Sla referentie op
    reference_file = processed / "anon_reference.json"
    ref_sorted = {v: k for k, v in sorted((v, k) for k, v in anon_map.items())}
    with open(reference_file, "w") as f:
        json.dump(ref_sorted, f)

    # Drop originele author, voeg anonieme toe
    df["anon_author"] = df["author"].map(anon_map)
    df.drop(columns=["author"], inplace=True)
    df.rename(columns={"anon_author": "author"}, inplace=True)

    # Verwijder eerste rij (versleuteld)
    df = df.drop(index=[0])

    # Save als csv en parquet met timestamp
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_csv = processed / f"whatsapp-{now}.csv"
    output_parquet = output_csv.with_suffix(".parquet")

    df.to_csv(output_csv, index=False)
    df.to_parquet(output_parquet, index=False)

    logger.success(f"Data opgeslagen als:\n- {output_csv}\n- {output_parquet}")
    logger.info("Vergeet niet je config.toml bij te werken met de nieuwe bestandsnaam!")
