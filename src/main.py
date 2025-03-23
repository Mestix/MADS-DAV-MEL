import argparse
from pathlib import Path
from my_module.les2 import generate_question_bar_chart
from my_module.les5 import generate_relations_chart
from my_module.config import Config, load_data

def run_chart_for_lesson(lesson_number: int):
    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)
    df = load_data(config)

    output_map = {
        2: ("./img/aantal_gestelde_vragen_per_gebruiker.jpg", generate_question_bar_chart),
        5: ("./img/carnaval_vs_gender_boxplot.png", generate_relations_chart),
    }

    if lesson_number not in output_map:
        print(f"Les {lesson_number} wordt niet herkend.")
        return

    output_path_str, chart_func = output_map[lesson_number]
    output_path = Path(output_path_str)
    chart_func(df, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draai visualisatie-opdrachten per les")
    parser.add_argument("--les", type=int, required=True, help="Lesnummer (bijv. 2 of 5)")
    args = parser.parse_args()

    run_chart_for_lesson(args.les)