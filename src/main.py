import sys
from pathlib import Path

# Voeg de map 'dev/scripts' toe aan sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'dev' / 'scripts'))

from les2 import generate_question_bar_chart

if __name__ == "__main__":
    # Roep de functie aan
    generate_question_bar_chart()
