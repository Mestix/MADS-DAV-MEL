from pathlib import Path
from loguru import logger
import pandas as pd
from config import Config

def load_data(config: Config) -> pd.DataFrame:
    root = Path(".").resolve()
    processed = root / Path(config.processed)
    datafile = processed / config.current
    
    if not datafile.exists():
        logger.warning(
            f"{datafile} does not exist. First run analyzer --device ios"
        )
        return pd.DataFrame()
    
    return pd.read_parquet(datafile)