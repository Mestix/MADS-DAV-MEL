import argparse
from pathlib import Path
from my_module.les2 import Config, load_data, generate_question_bar_chart

def run_les2_chart():
    config_path = Path("./config.toml").resolve()
    config = Config.load(config_path)

    df = load_data(config)

    output_path = Path("./img/aantal_gestelde_vragen_per_gebruiker.jpg")
    generate_question_bar_chart(df, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run verschillende functies vanuit main.py")
    
    parser.add_argument(
        "function",
        choices=["generate_les2"],
        help="Genereer de comparing catagories bar chart van les 2",
    )

    args = parser.parse_args()

    if args.function == "generate_les2":
        run_les2_chart()