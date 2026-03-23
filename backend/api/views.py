from django.http import JsonResponse
from rest_framework.decorators import api_view
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
from io import BytesIO


@api_view(['POST'])
def compile_handler(request):
    return JsonResponse({"message": "hello world"})


@api_view(['GET'])
def ping(request):
    return JsonResponse({"message": "Hello backend!"})


# TODO: separate into different files all handlers

@api_view(['POST'])
def import_file(request):
    file = request.FILES.get("file")

    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    filename = file.name

    result = ""
    if filename.endswith(".txt"):
        result = file.read().decode("utf-8")
    elif filename.endswith(".docx"):
        doc = Document(BytesIO(file.read()))
        for paragraph in doc.paragraphs:
            result += paragraph.text + "\n"
    elif filename.endswith(".pdf"):
        reader = PdfReader(BytesIO(file.read()))
        for page in reader.pages:
            text = page.extract_text()

            # TODO: add paragraph newlines from source pdf
            if text:
                result += text + "\n"

    return JsonResponse({
        "text": result,
    })
