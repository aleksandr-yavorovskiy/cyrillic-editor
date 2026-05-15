import asyncio
import logging
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from api.config import config
from api.schemas import TextRequest
from api.services import CompilationService, ExportService, ImportService, CompileOptions


logger = logging.getLogger("api")

MAX_TEXT_LENGTH = config.MAX_FILE_SIZE_MB * 1024 * 1024

compilation_service = CompilationService()
import_service = ImportService()
export_service = ExportService()

router = APIRouter(prefix="/api", tags=["editor"])


def check_size(text_or_bytes: str | bytes) -> None:
    data = text_or_bytes.encode("utf-8") if isinstance(text_or_bytes, str) else text_or_bytes
    if len(data) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Text exceeds maximum size of {config.MAX_FILE_SIZE_MB}MB",
        )


def _make_options(req: TextRequest) -> CompileOptions:
    return CompileOptions(
        font=req.font,
        fontSize=req.fontSize,
        top=req.top,
        bottom=req.bottom,
        left=req.left,
        right=req.right,
    )


@router.get("/ping/")
async def ping():
    return {"status": "ok", "message": "Hello from backend!"}


@router.post("/compile/")
async def compile_text(req: TextRequest):
    try:
        check_size(req.text)
        options = _make_options(req)
        pdf_bytes = await asyncio.to_thread(compilation_service.compile, req.text, options)
        return Response(
            content=pdf_bytes.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="result.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/pdf/")
async def export_pdf(req: TextRequest):
    check_size(req.text)
    try:
        buffer = await asyncio.to_thread(export_service.export, req.text, ".pdf", options=_make_options(req))
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="document.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export/docx/")
async def export_docx(req: TextRequest):
    check_size(req.text)
    try:
        buffer = await asyncio.to_thread(export_service.export, req.text, ".docx", options=_make_options(req))
        return Response(
            content=buffer.read(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": 'attachment; filename="document.docx"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/")
async def import_file(file: UploadFile = File(...)):
    file_data = await file.read()
    check_size(file_data)
    try:
        text = await asyncio.to_thread(import_service.import_file, BytesIO(file_data), file.filename or "unknown")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
