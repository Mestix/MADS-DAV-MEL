import argparse
from pathlib import Path
from les2 import generate_question_bar_chart
from les4 import generate_distribution_charts
from les5 import generate_relation_charts
from preprocessor import Preprocessor
from config import Config
from les3 import generate_time_charts

def run_chart_for_lesson(lesson_number: int, df, img_folder: Path):
    output_map = {
        2: (img_folder, generate_question_bar_chart),
        3: (img_folder, generate_time_charts),
        4: (img_folder, generate_distribution_charts),
        5: (img_folder, generate_relation_charts),
    }

    if lesson_number not in output_map:
        print(f"Les {lesson_number} wordt niet herkend.")
        return

    img_folder, chart_func = output_map[lesson_number]
    chart_func(df, img_folder)

def run_all_charts(df, output_folder: Path):
    run_chart_for_lesson(2, df, output_folder)
    run_chart_for_lesson(3, df, output_folder)
    run_chart_for_lesson(4, df, output_folder)
    run_chart_for_lesson(5, df, output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draai preprocessing of lesvisualisaties")
    parser.add_argument("--les", type=int, help="Genereer visualisatie voor specifieke les (bijv. 2 of 5)")
    parser.add_argument("--all", action="store_true", help="Genereer alle visualisaties in één keer")
    args = parser.parse_args()

    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)

    img_folder = Path(config.img_folder)

    whatsapp_processor = Preprocessor(config)
    df = whatsapp_processor.run()

    if args.les:
        run_chart_for_lesson(args.les, df, img_folder)
    elif args.all:
        run_all_charts(df, img_folder)
    else:
        print("Gebruik --preprocess of --les [nummer] om iets uit te voeren.")