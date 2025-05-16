import argparse
from pathlib import Path
import sys

sys.path.append(str(Path("./modules").resolve()))
sys.path.append(str(Path("./src/lessons").resolve()))

from loguru import logger

from config import Config
from dataloader import load_data_parquet
from les2 import generate_question_bar_chart
from les3 import generate_time_charts
from les4 import generate_distribution_charts
from les5 import generate_relation_charts
from les6 import generate_les6_charts
from preprocessor import Preprocessor
from settings import Settings


def run_chart_for_lesson(lesson_number: int, df, img_folder: Path, settings):
    "Voert de juiste chart-functie uit op basis van lesnummer."
    chart_mapping = {
        2: (generate_question_bar_chart, settings.les2),
        3: (generate_time_charts, settings.les3),
        4: (generate_distribution_charts, settings.les4),
        5: (generate_relation_charts, settings.les5),
        6: (generate_les6_charts, settings.les6),
    }

    if lesson_number not in chart_mapping:
        logger.error(f"Les {lesson_number} wordt niet ondersteund.")
        return

    chart_func, lesson_settings = chart_mapping[lesson_number]
    logger.info(f"Start genereren les {lesson_number}...")
    chart_func(df, img_folder, lesson_settings)
    logger.success(f"Les {lesson_number} succesvol afgerond.")


def run_all_charts(df, img_folder: Path, settings):
    "Voert alle gedefinieerde visualisaties achter elkaar uit."
    for lesson in [2, 3, 4, 5, 6]:
        run_chart_for_lesson(lesson, df, img_folder, settings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Voer preprocessing of visualisaties uit."
    )
    parser.add_argument(
        "--les",
        type=int,
        help="Genereer visualisatie voor specifieke les (bijv. 2 of 5)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Genereer alle visualisaties in één keer"
    )
    parser.add_argument(
        "--preprocess", action="store_true", help="Draai preprocessing opnieuw"
    )
    args = parser.parse_args()

    # Laad configuratie
    config = Config.load(Path("./config.toml").resolve())
    settings = Settings.load(Path("./settings.toml").resolve())
    img_folder = Path(config.img_folder)

    # Data laden of preprocessen
    if args.preprocess:
        logger.info("Start preprocessing van WhatsApp-data...")
        whatsapp_processor = Preprocessor(config, settings)
        df = whatsapp_processor.run()
    else:
        logger.info("Laad bestaande Parquet-bestand...")
        df = load_data_parquet(config)

    # Start verwerking
    if args.les:
        run_chart_for_lesson(args.les, df, img_folder, settings)
    elif args.all:
        run_all_charts(df, img_folder, settings)
    else:
        logger.error("Geef een lesnummer (--les) of gebruik --all of --preprocess.")
