import json
from datetime import datetime

import emoji
import pandas as pd
from loguru import logger

from config import Config
from dataloader import load_author_info, load_data_csv
from settings import Settings


class Preprocessor:
    """
    Preprocessor voor WhatsApp-berichten.

    Voert een volledige preprocessing pipeline uit:
    - Anonimiseert auteurs
    - Verrijkt berichten met extra informatie
    - Filtert ongewenste berichten
    - Markeert berichten binnen carnavalsweken
    - Slaat de verwerkte dataset op

    Aangestuurd via een Settings-configuratie.
    """

    def __init__(self, config: Config, settings: Settings):
        """Initialiseer Preprocessor met config- en settingsobject."""
        self.config = config
        self.settings = settings.preprocessing
        self.columns = self.settings.columns
        self.df = load_data_csv(config)
        self.processed_dir = config.processed_dir

        # Initiele parameters
        self.auto_msgs = self.settings.auto_messages["keywords"]
        self.start_date = pd.to_datetime(self.settings.start_date).date()
        self.carnaval_ranges = [
            (pd.to_datetime(d[0]).date(), pd.to_datetime(d[1]).date())
            for d in self.settings.carnaval.values()
        ]

    # ─────────────────────────────────────────────────────────────────────────────
    #    1. Opschonen en anonimiseren
    # ─────────────────────────────────────────────────────────────────────────────

    def clean_authors(self):
        """Verwijder speciale tekens aan het begin van auteursnamen."""
        if self.columns.author not in self.df.columns:
            logger.error(f"Kolom '{self.columns.author}' ontbreekt.")
            return

        pattern = r"^~\u202f"  # Specifiek patroon voor ongewenste prefixen
        self.df[self.columns.author] = (
            self.df[self.columns.author]
            .astype(str)
            .str.replace(pattern, "", regex=True)
        )
        logger.info("Authors opgeschoond.")

    def anonymize_authors(self):
        """Anonimiseer auteursnamen en sla de originele namen als referentie op."""
        from wa_analyzer.humanhasher import humanize

        authors = self.df[self.columns.author].unique()
        anon_map = {author: humanize(author) for author in authors}

        if len(anon_map) != len(authors):
            logger.warning("Aantal unieke auteurs na anonymisatie klopt niet.")

        # Opslaan van mapping voor later herstel
        ref_file = self.processed_dir / self.config.anon_reference
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        ref_sorted = {v: k for k, v in sorted((v, k) for k, v in anon_map.items())}

        with open(ref_file, "w", encoding="utf-8") as f:
            json.dump(ref_sorted, f, ensure_ascii=False, indent=2)

        self.df[self.columns.author] = self.df[self.columns.author].map(anon_map)
        logger.info("Auteurs geanonimiseerd.")

    # ─────────────────────────────────────────────────────────────────────────────
    #    2. Informatie verrijking
    # ─────────────────────────────────────────────────────────────────────────────

    def add_message_length(self):
        """Bereken de lengte van elk bericht en voeg deze toe als nieuwe kolom."""
        self.df[self.columns.message_length] = (
            self.df[self.columns.message].astype(str).str.len()
        )
        logger.info("Kolom 'message_length' toegevoegd.")

    def add_author_info(self):
        """Verrijk de dataset met leeftijd, geslacht en andere info over auteurs."""
        info = load_author_info(self.config)
        self.df = self.df.merge(info, on=self.columns.author, how="left")
        logger.info("Auteur-info toegevoegd.")

    def set_has_emoji(self):
        """Tel het aantal emoji's per bericht en voeg toe als kolom."""

        def count_emojis(msg):
            return len([c for c in str(msg) if c in emoji.EMOJI_DATA])

        self.df[self.columns.emoji_count] = self.df[self.columns.message].apply(
            count_emojis
        )
        logger.info("Kolom 'emoji_count' toegevoegd.")

    def set_is_carnaval(self):
        """Markeer berichten die binnen een carnavalsperiode vallen."""
        self.df[self.columns.timestamp] = pd.to_datetime(
            self.df[self.columns.timestamp]
        )
        self.df[self.columns.date] = self.df[self.columns.timestamp].dt.date

        def is_carnaval(d):
            return any(start <= d <= end for (start, end) in self.carnaval_ranges)

        self.df[self.columns.is_carnaval] = self.df[self.columns.date].apply(
            is_carnaval
        )
        logger.info("Kolom 'is_carnaval' toegevoegd.")

    # ─────────────────────────────────────────────────────────────────────────────
    #    3. Filteren en opschonen
    # ─────────────────────────────────────────────────────────────────────────────

    def filter_automatic_messages(self):
        """Verwijder standaard automatische berichten zoals 'media weggelaten'."""
        pattern = "|".join(self.auto_msgs)  # Combineer alle keywords in regex
        before = len(self.df)
        self.df = self.df[
            ~self.df[self.columns.message]
            .astype(str)
            .str.contains(pattern, case=False, na=False)
        ]
        logger.info(f"{before - len(self.df)} automatische berichten verwijderd.")

    def filter_messages_after_start_date(self):
        """Verwijder berichten die vóór de ingestelde startdatum zijn verzonden."""
        self.df[self.columns.timestamp] = pd.to_datetime(
            self.df[self.columns.timestamp], errors="coerce"
        )
        before = len(self.df)
        self.df = self.df[self.df[self.columns.timestamp].dt.date >= self.start_date]
        logger.info(f"{before - len(self.df)} oude berichten verwijderd.")

    # ─────────────────────────────────────────────────────────────────────────────
    #    4. Output opslaan
    # ─────────────────────────────────────────────────────────────────────────────

    def save_output(self):
        """Sla de verwerkte dataset op in CSV- en Parquet-formaat."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_csv = self.processed_dir / f"whatsapp-{timestamp}-processed.csv"
        output_parquet = output_csv.with_suffix(".parquet")

        self.df.to_csv(output_csv, index=False)
        self.df.to_parquet(output_parquet, index=False)

        logger.success(f"Data opgeslagen:\n- {output_csv}\n- {output_parquet}")
        logger.info(
            "Vergeet niet je config.toml bij te werken met de nieuwe bestandsnaam!"
        )

    # ─────────────────────────────────────────────────────────────────────────────
    #    5. Pipeline runner
    # ─────────────────────────────────────────────────────────────────────────────

    def run(self):
        """
        Doorloop alle preprocessing stappen zoals gedefinieerd in settings.enabled_steps.

        Elk stap wordt dynamisch aangeroepen op basis van de methode-naam.
        """
        if self.df is None or self.df.empty:
            logger.error("Dataframe is leeg of niet geladen.")
            return None

        for step in self.settings.enabled_steps:
            func = getattr(self, step, None)
            if callable(func):
                logger.info(f"Stap: {step}")
                try:
                    func()
                except Exception as e:
                    logger.error(f"Fout bij stap '{step}': {e}")
            else:
                logger.warning(f"Stap '{step}' niet gevonden.")

        return self.df
