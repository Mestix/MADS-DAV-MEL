import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from loguru import logger
from wa_analyzer.humanhasher import humanize
from config import Config

class Preprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.processed = Path(config.processed)
        self.inputfile = self.processed / config.current
        self.authorinfo = self.processed / config.author_info
        self.df = pd.DataFrame()

    def load_data_csv(self):
        if not self.inputfile.exists():
            logger.warning(f"{self.inputfile} bestaat niet.")
            return False

        try:
            if self.inputfile.suffix == ".parquet":
                self.df = pd.read_parquet(self.inputfile)
            else:
                self.df = pd.read_csv(self.inputfile, parse_dates=["timestamp"])
        except Exception as e:
            logger.error(f"Fout bij inlezen van {self.inputfile}: {e}")
            return False

        logger.info(f"Data geladen met {len(self.df)} rijen.")
        return True

    def clean_authors(self):
        clean_tilde = r"^~\u202f"
        if "author" not in self.df.columns:
            logger.error("Kolom 'author' ontbreekt in de data.")
            return False
    
        self.df["author"] = self.df["author"].apply(lambda x: re.sub(clean_tilde, "", x))

    def anonymize_authors(self):
        authors = self.df["author"].unique()
        anon_map = {k: humanize(k) for k in authors}
        assert len(anon_map) == len(authors), "Aantal authors klopt niet"

        # Referentie opslaan
        reference_file = self.processed / "anon_reference.json"
        ref_sorted = {v: k for k, v in sorted((v, k) for k, v in anon_map.items())}
        with open(reference_file, "w") as f:
            json.dump(ref_sorted, f)

        self.df["anon_author"] = self.df["author"].map(anon_map)
        self.df.drop(columns=["author"], inplace=True)
        self.df.rename(columns={"anon_author": "author"}, inplace=True)
        logger.info(f"{len(authors)} auteurs geanonimiseerd.")

    def remove_intro_line(self):
        self.df = self.df.drop(index=[0])

    def add_author_info(self):
        if not self.authorinfo.exists():
            logger.error(f"Bestand met auteur-info niet gevonden: {self.authorinfo}")
            return

        info_df = pd.read_csv(self.authorinfo)
        expected_cols = {"author", "age", "gender"}
        if not expected_cols.issubset(info_df.columns):
            logger.error(f"Verwachte kolommen ontbreken in {self.authorinfo}")
            return

        self.df = self.df.merge(info_df, on="author", how="left")
        logger.info(f"Leeftijd en geslacht toegevoegd voor {self.df['author'].nunique()} auteurs.")

    def save_output(self):
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_csv = self.processed / f"whatsapp-{now}.csv"
        output_parquet = output_csv.with_suffix(".parquet")

        self.df.to_csv(output_csv, index=False)
        self.df.to_parquet(output_parquet, index=False)

        logger.success(f"Data opgeslagen als:\n- {output_csv}\n- {output_parquet}")
        logger.info("Vergeet niet je config.toml bij te werken met de nieuwe bestandsnaam!")

    def run(self):
        if not self.load_data_csv():
            return

        self.clean_authors()
        self.anonymize_authors()
        self.remove_intro_line()
        self.add_author_info()
        self.save_output()
