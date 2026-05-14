from pathlib import Path
import re

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from api.config import config
from api.models import User
from api.dependencies import get_current_user_optional
from api.schemas import FontResponse


router = APIRouter(prefix="/api/fonts", tags=["fonts"])

ALLOWED_EXTENSIONS = {".ttf", ".otf"}
MAX_FONT_SIZE_MB = 10


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-Я0-9_-]", "", name.strip())


def _resolve_font_path(font_name: str) -> Path | None:
    root = config.FONT_DIR.resolve()
    for ext in ALLOWED_EXTENSIONS:
        path = (root / (font_name + ext)).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            continue
        if path.exists():
            return path
    return None


def _scan_fonts() -> list[FontResponse]:
    fonts = []
    for path in sorted(config.FONT_DIR.iterdir()):
        if path.suffix.lower() in ALLOWED_EXTENSIONS:
            fonts.append(FontResponse(
                name=path.stem,
                size=path.stat().st_size,
            ))
    return fonts


@router.get("/", response_model=list[FontResponse])
async def list_fonts(user: User | None = Depends(get_current_user_optional)):
    return _scan_fonts()


@router.post("/", response_model=FontResponse, status_code=201)
async def upload_font(
    file: UploadFile = File(...),
    name: str = Form(None),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported font format: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    stem = _sanitize_name(name or Path(file.filename).stem)
    if not stem:
        raise HTTPException(status_code=400, detail="Font name is required")

    root = config.FONT_DIR.resolve()
    dest = (root / (stem + ext)).resolve()
    try:
        dest.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid font name")

    if dest.exists():
        raise HTTPException(status_code=409, detail="Font with this name already exists")

    content = await file.read()
    if len(content) > MAX_FONT_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Font file exceeds maximum size of {MAX_FONT_SIZE_MB}MB")
    dest.write_bytes(content)

    return FontResponse(name=dest.stem, size=dest.stat().st_size)


@router.get("/{font_name}")
async def get_font(font_name: str):
    path = _resolve_font_path(font_name)
    if path is None:
        raise HTTPException(status_code=404, detail="Font not found")
    return FileResponse(path, media_type="application/octet-stream")


@router.delete("/{font_name}", status_code=204)
async def delete_font(
    font_name: str,
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    path = _resolve_font_path(font_name)
    if path is None:
        raise HTTPException(status_code=404, detail="Font not found")
    path.unlink()
