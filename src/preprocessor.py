import json
import re
from datetime import datetime

import emoji
import pandas as pd
from loguru import logger
from wa_analyzer.humanhasher import humanize

from config import Config
from dataloader import load_author_info, load_data_csv


class Preprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.df = load_data_csv(config)
        self.processed_dir = config.processed_dir

    def clean_authors(self):
        """Verwijder ongewenste tekens aan het begin van auteur-namen."""
        if "author" not in self.df.columns:
            logger.error("Kolom 'author' ontbreekt in de data.")
            return

        tilde_pattern = r"^~\u202f"
        self.df["author"] = (
            self.df["author"].astype(str).apply(lambda x: re.sub(tilde_pattern, "", x))
        )
        logger.info("Authors opgeschoond.")

    def anonymize_authors(self):
        """Anonymiseer auteursnamen en sla de referentie op."""
        authors = self.df["author"].unique()
        anon_map = {author: humanize(author) for author in authors}

        if len(anon_map) != len(authors):
            logger.warning(
                "Er is een probleem met het aantal unieke auteurs na anonymisatie."
            )

        # Sla de referentielijst op
        reference_file = self.processed_dir / "anon_reference.json"
        ref_sorted = {v: k for k, v in sorted((v, k) for k, v in anon_map.items())}
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        with open(reference_file, "w", encoding="utf-8") as f:
            json.dump(ref_sorted, f, ensure_ascii=False, indent=2)

        self.df["author"] = self.df["author"].map(anon_map)
        logger.info(f"{len(authors)} auteurs geanonimiseerd.")

    def add_message_length(self):
        """Voeg kolom toe met lengte van elk bericht."""
        self.df["message_length"] = self.df["message"].astype(str).str.len()
        logger.info("Kolom 'message_length' toegevoegd met lengte van elk bericht.")

    def add_author_info(self):
        """Voeg leeftijd en geslacht en trouwstatus toe aan auteurs."""
        author_info = load_author_info(self.config)
        self.df = self.df.merge(author_info, on="author", how="left")
        logger.info(
            f"Auteur-info toegevoegd voor {self.df['author'].nunique()} auteurs."
        )

    def filter_automatic_messages(self):
        """Verwijder automatische systeemberichten."""
        auto_msgs = [
            "afbeelding weggelaten",
            "media weggelaten",
            "document weggelaten",
            "oproep gemist",
            "bericht is verwijderd",
            "video weggelaten",
            "audio weggelaten",
        ]
        pattern = "|".join(auto_msgs)
        initial_count = len(self.df)
        self.df = self.df[
            ~self.df["message"].astype(str).str.contains(pattern, case=False, na=False)
        ]
        logger.info(
            f"{initial_count - len(self.df)} automatische berichten verwijderd."
        )

    def filter_messages_after_september_2023(self):
        """Filter berichten vanaf 1 september 2023."""
        if "timestamp" not in self.df.columns:
            logger.error("Kolom 'timestamp' ontbreekt in de data.")
            return

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], errors="coerce")
        initial_count = len(self.df)
        self.df = self.df[self.df["timestamp"].dt.date >= datetime(2023, 9, 1).date()]
        logger.info(
            f"{initial_count - len(self.df)} berichten vóór 1 september 2023 verwijderd."
        )

    def set_is_carnaval(self):
        # Zorgt dat timestamp en date kolommen goed staan
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["date"] = self.df["timestamp"].dt.date

        # Definieert carnavalsperiodes
        carnaval_2024 = (
            pd.to_datetime("2024-02-08").date(),
            pd.to_datetime("2024-02-15").date(),
        )
        carnaval_2025 = (
            pd.to_datetime("2025-02-27").date(),
            pd.to_datetime("2025-03-04").date(),
        )

        # Voegt is_carnaval toe
        def is_carnaval(date):
            return (
                carnaval_2024[0] <= date <= carnaval_2024[1]
                or carnaval_2025[0] <= date <= carnaval_2025[1]
            )

        self.df["is_carnaval"] = self.df["date"].apply(is_carnaval)

    def set_has_emoji(self):
        # has emoji
        def count_emojis(text):
            return len([char for char in str(text) if char in emoji.EMOJI_DATA])

        self.df["emoji_count"] = self.df["message"].apply(count_emojis)

    def save_output(self):
        """Sla de verwerkte data op in CSV en Parquet formaat."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_csv = self.processed_dir / f"whatsapp-{timestamp}-processed.csv"
        output_parquet = output_csv.with_suffix(".parquet")

        self.df.to_csv(output_csv, index=False)
        self.df.to_parquet(output_parquet, index=False)

        logger.success(
            f"Data opgeslagen:\n- CSV: {output_csv}\n- Parquet: {output_parquet}"
        )
        logger.info(
            "Vergeet niet je config.toml bij te werken met de nieuwe bestandsnaam!"
        )

    def run(self):
        """Voer het volledige preprocessing-pipeline uit."""
        if self.df is None or self.df.empty:
            logger.error("Dataframe is leeg of niet geladen.")
            return None

        self.clean_authors()
        self.anonymize_authors()
        self.add_message_length()
        self.add_author_info()
        self.filter_automatic_messages()
        self.filter_messages_after_september_2023()
        self.set_has_emoji()
        self.set_is_carnaval()
        # self.save_output()

        return self.df
