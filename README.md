# WhatsApp Analyseproject

Dit project analyseert WhatsApp-groepsgesprekken en genereert visualisaties over gebruikersgedrag, berichtenactiviteit, schrijfstijl en meer.

## Functionaliteit

- Preprocessing: Verrijkt ruwe WhatsApp-data met metadata zoals lengte, emoji's, carnavalindicatoren, enz.
- Visualisaties per les:
  - Les 2 – Wie stelt de meeste vragen?
  - Les 3 – Activiteit door de tijd (wekelijks & rondom carnaval)
  - Les 4 – (Nog in ontwikkeling)
  - Les 5 – Correlaties en groepsverschillen (aangetrouwd vs. anderen)
  - Les 6 – Schrijfstijlvisualisatie met PCA/t-SNE

## Installatie

1. Clone deze repo:
   ```bash
   git clone https://github.com/Mestix/MADS-DAV-MEL.git
   cd MADS-DAV-MEL
   ```

2. Maak een virtuele omgeving aan:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate   # Windows
   ```

3. Installeer dependencies:
   ```bash
   uv sync --all extras
   ```

## Preprocessing

1. Zet de ruwe WhatsApp-chat als _chat.txt in data/raw/.

2. Run wa-analyzer voor je toestel:
   ```bash
   analyzer --device ios   # of android
   ```

3. Zet het pad naar de geëxporteerde CSV uit data/processed in config.toml.

4. Zorg dat author_info.txt beschikbaar is in data/processed/ kloppend bij de geanonimiseerde users uit anon_reference.json:
   ```
   "author","age","gender","is_inlaw"
   "amusing-owl",36,"m",1
   ```

5. Run de preprocessor om het .parquet bestand te genereren en extra data toe te voegen, voeg de locatie van de .parq toe aan je config.toml:
   ```bash
   python src/main.py --preprocess
   ```

## Visualisaties genereren

- Eén specifieke les:
  ```bash
  python src/main.py --les 2
  ```

- Alle lessen:
  ```bash
  python src/main.py --all
  ```

Output wordt opgeslagen in de img/-map.

## Configuratie

- config.toml: Pad- en bestandsinstellingen
- settings.toml: Preprocessing- en plotinstellingen (zoals kleuren, labels, filters)

## Projectstructuur

```
.
├── src/                # Broncode per les
├── data/               # WhatsApp-data (raw/processed)
├── img/                # Afbeeldingen gegenereerd uit visualisaties
├── notebooks/          # Analyse notebooks
├── logs/               # Logbestanden
├── settings.toml       # Visualisatieconfiguratie
├── config.toml         # Pad- en inputconfiguratie
├── requirements.txt    # Pip dependencies
└── README.md
```

## Belangrijke dependencies

- pandas, numpy, scikit-learn, seaborn, matplotlib
- nltk, pyarrow, loguru
- wa-analyzer voor WhatsApp-parsering

© 2025 – WhatsApp Analyseproject – door Melistixx
