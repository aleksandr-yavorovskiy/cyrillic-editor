import asyncio
import shutil
import tempfile
from pathlib import Path

from api.database import init_db
from api.config import config


def pytest_sessionstart():
    db_path = Path(str(config.DATABASE_URL).replace("sqlite+aiosqlite:///", ""))
    if db_path.exists():
        db_path.unlink()

    tmp_font_dir = Path(tempfile.mkdtemp(prefix="test_fonts_"))
    object.__setattr__(config, "FONT_DIR", tmp_font_dir)

    asyncio.run(init_db())


def pytest_sessionfinish():
    shutil.rmtree(config.FONT_DIR, ignore_errors=True)
