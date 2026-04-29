from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from io import BytesIO

from api.services import CompilationService, ImportService, ExportService
from api.services import CompileOptions


@api_view(["GET"])
def ping(request):
    return JsonResponse({"status": "ok", "message": "Hello from backend!"})


@api_view(["POST"])
def compile_handler(request):
    text = request.data.get("text", "")
    options = CompileOptions(
        font=request.data.get("font", ""),
        fontSize=request.data.get("fontSize", 14),
        top=request.data.get("top", 2),
        bottom=request.data.get("bottom", 2),
        left=request.data.get("left", 2),
        right=request.data.get("right", 2),
    )

    try:
        pdf_bytes = CompilationService.get_instance().compile(text, options)
        return HttpResponse(
            pdf_bytes,
            content_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="result.pdf"'},
        )
    except Exception as e:
        return HttpResponse(str(e), status=500)


@api_view(["POST"])
def import_handler(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    try:
        file_data = BytesIO(file.read())
        text = ImportService.get_instance().import_file(file_data, file.name)
        return JsonResponse({"text": text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(["POST"])
def export_handler(request): # TODO: rename to export_docx
    text = request.data.get("text", "")
    format = request.data.get("format", ".docx")

    try:
        buffer = ExportService.get_instance().export(text, format)
        buffer.seek(0)

        content_types = {
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        content_type = content_types.get(format, "application/octet-stream")

        return HttpResponse(
            buffer.read(),
            content_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="document{format}"'},
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(["POST"])
def export_pdf_handler(request):
    text = request.data.get("text", "")
    options = CompileOptions(
        font=request.data.get("font", ""),
        fontSize=request.data.get("fontSize", 14),
        top=request.data.get("top", 2),
        bottom=request.data.get("bottom", 2),
        left=request.data.get("left", 2),
        right=request.data.get("right", 2),
    )

    try:
        pdf_bytes = CompilationService.get_instance().compile(text, options)
        pdf_bytes.seek(0)

        return HttpResponse(
            pdf_bytes.read(),
            content_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="document.pdf"'},
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
