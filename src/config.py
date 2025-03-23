import tomllib
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

class Config(BaseModel):
    processed: str
    current: str
    author_info: str | None = None
    config_path: Path | None = None  

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data, config_path=path.parent.resolve())