import argparse
from pathlib import Path

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
    output_map = {
        2: (img_folder, generate_question_bar_chart, settings.les2),
        3: (img_folder, generate_time_charts, settings.les3),        
        4: (img_folder, generate_distribution_charts, getattr(settings, "les4", {})),
        5: (img_folder, generate_relation_charts, settings.les5),
        6: (img_folder, generate_les6_charts, settings.les6),
    }

    if lesson_number not in output_map:
        print(f"Les {lesson_number} wordt niet herkend.")
        return

    img_folder, chart_func, lesson_settings = output_map[lesson_number]
    chart_func(df, img_folder, lesson_settings)


def run_all_charts(df, output_folder: Path):
    run_chart_for_lesson(2, df, output_folder, settings)
    run_chart_for_lesson(3, df, output_folder, settings)
    run_chart_for_lesson(5, df, output_folder, settings)
    run_chart_for_lesson(5, df, output_folder, settings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Draai preprocessing of lesvisualisaties"
    )
    parser.add_argument(
        "--les",
        type=int,
        help="Genereer visualisatie voor specifieke les (bijv. 2 of 5)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Genereer alle visualisaties in één keer"
    )
    args = parser.parse_args()

    config = Config.load(Path("./config.toml").resolve())
    settings = Settings.load(Path("./settings.toml").resolve())

    img_folder = Path(config.img_folder)

    # whatsapp_processor = Preprocessor(config, settings)
    # df = whatsapp_processor.run()

    df = load_data_parquet(config)

    if args.les:
        run_chart_for_lesson(args.les, df, img_folder, settings)
    elif args.all:
        run_all_charts(df, img_folder)
    else:
        print("Gebruik --preprocess of --les [nummer] om iets uit te voeren.")
