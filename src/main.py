import argparse
from pathlib import Path
from dataloader import load_data_parquet
from les2 import generate_question_bar_chart
from les5 import generate_relations_chart
from preprocessor import Preprocessor
from config import Config
from les3 import generate_time_charts

def run_chart_for_lesson(lesson_number: int, df, output_folder: Path):
    output_map = {
        2: (output_folder / "aantal_gestelde_vragen_per_gebruiker.jpg", generate_question_bar_chart),
        3: (output_folder, generate_time_charts),
        5: (output_folder / "carnaval_vs_gender_boxplot.png", generate_relations_chart),
    }

    if lesson_number not in output_map:
        print(f"Les {lesson_number} wordt niet herkend.")
        return

    output_path, chart_func = output_map[lesson_number]
    chart_func(df, output_path)

def run_all_charts(df, output_folder: Path):
    print("Genereer alle visualisaties...")
    run_chart_for_lesson(2, df, output_folder)
    run_chart_for_lesson(3, df, output_folder)
    run_chart_for_lesson(5, df, output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draai preprocessing of lesvisualisaties")
    parser.add_argument("--preprocess", action="store_true", help="Voer preprocessing uit")
    parser.add_argument("--les", type=int, help="Genereer visualisatie voor specifieke les (bijv. 2 of 5)")
    parser.add_argument("--all", action="store_true", help="Genereer alle visualisaties in één keer")
    args = parser.parse_args()

    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)

    df = load_data_parquet(config)

    if args.preprocess:
        whatsapp_processor = Preprocessor(config)
        whatsapp_processor.run()
    elif args.les:
        run_chart_for_lesson(args.les, df, Path(config.img_folder))
    elif args.all:
        run_all_charts(df, Path(config.img_folder))
    else:
        print("Gebruik --preprocess of --les [nummer] om iets uit te voeren.")