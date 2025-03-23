import tomllib
from pydantic import BaseModel
from pathlib import Path
from loguru import logger
import pandas as pd

class Config(BaseModel):
    processed: str
    current: str

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data)

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