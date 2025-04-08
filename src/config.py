import tomllib
from pathlib import Path

import pandas as pd
from pydantic import BaseModel


class Config(BaseModel):
    processed_dir: Path
    current: Path
    input_path: Path
    author_info_path: Path
    config_path: Path
    img_folder: Path

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data, config_path=path.parent.resolve())
