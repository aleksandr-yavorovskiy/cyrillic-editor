import os

from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AppConfig:
    FONT_DIR: Path = field(default_factory=lambda: BASE_DIR / "fonts")
    DATABASE_URL: str = field(default_factory=lambda: f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3") # TODO: change to psql?
    EXPERT_USERNAME: str = field(default_factory=lambda: os.environ.get("EXPERT_USERNAME", "expert"))
    EXPERT_PASSWORD: str = field(default_factory=lambda: os.environ.get("EXPERT_PASSWORD", "expert123")) # TODO: change before prod
    DEFAULT_FONT_SIZE: int = 14
    DEFAULT_MARGIN_CM: int = 2
    SOFT_BREAK_THRESHOLD: int = 15
    LATEX_LINE_HEIGHT_MULTIPLIER: float = 1.2
    MAX_FILE_SIZE_MB: int = 50
    XELATEX_TIMEOUT_SEC: int = 180
    SUPPORTED_IMPORT_EXTENSIONS: tuple = (".txt", ".docx", ".pdf")
    SUPPORTED_EXPORT_EXTENSIONS: tuple = (".docx", ".pdf")


config = AppConfig()
