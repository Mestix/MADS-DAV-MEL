import tomllib
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List


class ColumnMap(BaseModel):
    author: str
    message: str
    timestamp: str
    emoji_count: str
    message_length: str
    is_carnaval: str
    date: str


class Settings(BaseModel):
    start_date: str
    auto_messages: Dict[str, List[str]]
    carnaval: Dict[str, List[str]]
    columns: ColumnMap
    enabled_steps: List[str]
    settings_path: Path

    les2: dict

    @classmethod
    def load(cls, path: Path):
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls(
            **data["preprocessing"],
            les2=data["les2"],
            settings_path=path.resolve()
        )
