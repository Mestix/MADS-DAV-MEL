from pathlib import Path
from loguru import logger
import pandas as pd
from config import Config

def load_data(config: Config) -> pd.DataFrame:
    # Vind de projectroot: map waarin 'config.toml' staat
    root = config.config_path or Path(".").resolve()
    
    processed = root / config.processed
    datafile = processed / config.current

    if not datafile.exists():
        logger.warning(f"{datafile} does not exist. First run preprocessing.")
        return pd.DataFrame()

    return pd.read_parquet(datafile)