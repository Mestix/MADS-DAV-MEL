import pandas as pd
from loguru import logger

from config import Config


def load_data_parquet(config: Config) -> pd.DataFrame:
    # Vind de projectroot: map waarin 'config.toml' staat
    root = config.config_path
    processed = root / config.processed_dir
    datafile = processed / config.current

    if not datafile.exists():
        logger.warning(f"{datafile} does not exist. First run --preprocess")
        return pd.DataFrame()

    return pd.read_parquet(datafile)


def load_data_csv(config: Config) -> pd.DataFrame:
    root = config.config_path
    config = config
    processed = root / config.processed_dir
    inputfile = processed / config.input_path

    df = pd.DataFrame()

    if not inputfile.exists():
        logger.warning(f"{inputfile} bestaat niet.")
        return False

    try:
        df = pd.read_csv(inputfile, parse_dates=["timestamp"])
    except Exception as e:
        logger.error(f"Fout bij inlezen van {inputfile}: {e}")
        return False

    logger.info(f"Data geladen met {len(df)} rijen.")

    return df


def load_author_info(config: Config) -> pd.DataFrame:
    root = config.config_path
    config = config
    processed = root / config.processed_dir
    authorinfo = processed / config.author_info_path

    if not authorinfo.exists():
        logger.error(f"Bestand met auteur-info niet gevonden: {authorinfo}")
        return

    info_df = pd.read_csv(authorinfo)

    expected_cols = {"author", "age", "gender", "is_inlaw"}
    if not expected_cols.issubset(info_df.columns):
        logger.error(f"Verwachte kolommen ontbreken in {authorinfo}")
        return

    return info_df
