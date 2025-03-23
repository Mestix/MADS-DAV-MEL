import argparse
from pathlib import Path
from dataloader import load_data
from les2 import generate_question_bar_chart
from les5 import generate_relations_chart
from preprocessor import Preprocessor
from config import Config
from les3 import generate_time_charts

def run_chart_for_lesson(lesson_number: int):
    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)
    df = load_data(config)

    output_map = {
        2: ("./img/aantal_gestelde_vragen_per_gebruiker.jpg", generate_question_bar_chart),
        3: ("./img", generate_time_charts),
        5: ("./img/carnaval_vs_gender_boxplot.png", generate_relations_chart),
    }

    if lesson_number not in output_map:
        print(f"Les {lesson_number} wordt niet herkend.")
        return

    output_path_str, chart_func = output_map[lesson_number]
    chart_func(df, Path(output_path_str))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draai preprocessing of lesvisualisaties")
    parser.add_argument("--preprocess", action="store_true", help="Voer preprocessing uit")
    parser.add_argument("--les", type=int, help="Genereer visualisatie voor specifieke les (bijv. 2 of 5)")
    args = parser.parse_args()

    if args.preprocess:
        pre = Preprocessor(Path("./config.toml"))
        pre.run()
    elif args.les:
        run_chart_for_lesson(args.les)
    else:
        print("Gebruik --preprocess of --les [nummer] om iets uit te voeren.")
