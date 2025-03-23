import tomllib
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

class Config(BaseModel):
    processed: str
    current: str

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data)