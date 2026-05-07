from dataclasses import dataclass, field
from pathlib import Path
from django.conf import settings


@dataclass(frozen=True)
class AppConfig:
    FONT_DIR: Path = field(default_factory=lambda: Path(settings.BASE_DIR) / "fonts")
    DEFAULT_FONT_SIZE: int = 14
    DEFAULT_MARGIN_CM: int = 2
    SOFT_BREAK_THRESHOLD: int = 15
    LATEX_LINE_HEIGHT_MULTIPLIER: float = 1.2
    MAX_FILE_SIZE_MB: int = 50
    XELATEX_TIMEOUT_SEC: int = 180
    SUPPORTED_IMPORT_EXTENSIONS: tuple = (".txt", ".docx", ".pdf")
    SUPPORTED_EXPORT_EXTENSIONS: tuple = (".docx", ".pdf")


config = AppConfig()
