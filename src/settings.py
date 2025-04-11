import tomllib
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class Columns(BaseModel):
    author: str
    message: str
    timestamp: str
    emoji_count: str
    message_length: str
    is_carnaval: str
    date: str


class PreprocessingSettings(BaseModel):
    start_date: str
    enabled_steps: List[str]
    auto_messages: Dict[str, List[str]]
    carnaval: Dict[str, List[str]]
    columns: Columns


class Settings(BaseModel):
    # Required
    preprocessing: PreprocessingSettings

    # Optional lesson-specific config
    les2: Optional[Dict[str, Any]] = {}
    les3: Optional[Dict[str, Any]] = {}

    # Metadata
    settings_path: Path

    @classmethod
    def load(cls, path: Path) -> "Settings":
        with path.open("rb") as f:
            data = tomllib.load(f)

        return cls(
            preprocessing=PreprocessingSettings(**data["preprocessing"]),
            les2=data.get("les2", {}),
            les3=data.get("les3", {}),
            settings_path=path.resolve(),
        )
